# import threading
import time
import numpy as np
from Queue import Queue
from Queue import Empty
from Queue import Full

from merger import Merger
from visualizer import Visualizer
from speaker import Speaker
from recording import Recording
from t2t_stt import T2t_stt

from speaker_recognition.speaker_recognition import Speaker_recognition

# kevins ros changes
import rospy


class SAM:

    def __init__(self, visualization=True):
        self.merger_to_main_queue = Queue(maxsize=1000)  # very roughly 30sec
        self.merger = Merger(self.merger_to_main_queue)

        self.visualization = visualization
        if self.visualization:
            self.main_to_vis_queue = Queue(maxsize=50)
            self.visualizer = Visualizer(self.main_to_vis_queue)

        self.speakers = {}
        self.num_speakers = 0
        self.stt = T2t_stt()
        self.sr = Speaker_recognition()

    def run(self):
        self.merger.start()

        if self.visualization:
            self.visualizer.start()

        recording_id_odas = [0, 0, 0, 0]
        last_recording_id_odas = [0, 0, 0, 0]

        recordings = {}
        # request to speaker recognition waiting to be answered, key is the id,
        # value is the queue in which the result will be stored
        sr_requests = {}

        # kevins ros changes
        rospy.init_node("SAM", anonymous=True)
        rate = rospy.Rate(10)

        while self.merger.is_alive() and not rospy.is_shutdown():

            # wait for/get next data
            try:
                next_data = self.merger_to_main_queue.get(block=True, timeout=1)
            except Empty:
                continue  # restart loop, but check again if we maybe got a stop signal

            cid = next_data['id_info']
            caudio = next_data['audio_data']

            ############################################################################################
            # this part separates the 4 streams and manages the ones where currently audio is being recorded
            #########################################################################################
            # cid[i] = [id, x, y, z, activity]
            for i in range(len(cid)):  # len=4

                recording_id_odas[i] = cid[i][0]

                if recording_id_odas[i] > 0:
                    if recording_id_odas[i] == last_recording_id_odas[i]:
                        # same person continues speaking
                        recordings[recording_id_odas[i]].audio = np.append(recordings[recording_id_odas[i]].audio,
                                                                           caudio[i])
                        recordings[recording_id_odas[i]].currentpos = [cid[i][1], cid[i][2], cid[i][3]]

                    else:
                        # a person startet speaking
                        recordings[recording_id_odas[i]] = Recording(recording_id_odas[i],
                                                                     [cid[i][1], cid[i][2], cid[i][3]])
                        recordings[recording_id_odas[i]].audio = np.append(recordings[recording_id_odas[i]].audio,
                                                                           caudio[i])

                        # if a different person was speaking before, he is now done
                        if last_recording_id_odas[i] > 0:
                            recordings[last_recording_id_odas[i]].stopped = True
                elif recording_id_odas[i] == 0 and last_recording_id_odas[i] > 0:
                    # if a different person was speaking before, he is now done
                    recordings[last_recording_id_odas[i]].stopped = True

                last_recording_id_odas[i] = recording_id_odas[i]

            ##########################################################     
            # check if we got any answers from sr (speaker recognition) in the meantime
            #############################################################
            to_delete_req = []
            for rec_id, req in sr_requests.iteritems():
                try:
                    # sr_id: -99 means new speaker
                    # certainty between 0-10
                    certainty = 0
                    preliminary_id, sr_id, certainty = req.get(block=False)

                    # Fuse info of speaker recognition on localization together
                    # First the best case, both agree on an is/new speker
                    if sr_id == recordings[rec_id].preliminary_speaker_id:
                        # both agree, thats nice
                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                        recordings[rec_id].send_to_trainer = True
                    elif recordings[rec_id].created_new_speaker and sr_id == -99:
                        # both agree, that this is a new speaker
                        rospy.loginfo("both agree that rec %d is new speaker %d" % (
                            rec_id, recordings[rec_id].preliminary_speaker_id))
                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                        recordings[rec_id].send_to_trainer = True
                    else:

                        # Now come the harder parts.
                        if certainty < 1:
                            # if speaker recognition is unsure we rely on localization
                            recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                        elif certainty > 8:
                            # sr is super sure, we trust it
                            recordings[rec_id].final_speaker_id = sr_id
                            recordings[rec_id].sr_changed_speaker = True
                        else:
                            # check the angle the the speaker sr suggested, and depending on the certatnty decide
                            # go through the lsit of speaker angles and find the one one which sr suggests
                            found = False
                            for (oth_id, angl) in recordings[rec_id].angles_to_speakers:
                                if oth_id == sr_id:
                                    # the furthere we are away the shurer sr has to be
                                    if certainty * 20 > angl:
                                        recordings[rec_id].final_speaker_id = sr_id
                                        recordings[rec_id].sr_changed_speaker = True
                                    else:
                                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                                    found = True
                                    break
                            if not found:
                                # this shouldn't happen
                                rospy.loginfo(
                                    "Speaker recognition suggestested id {} for recording {}, which doesn't exist".format(
                                        sr_id, rec_id))
                                recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id

                    rospy.loginfo("response for req %d, results is %d, certanty %d" % (rec_id, sr_id, certainty))
                    recordings[rec_id].is_back_from_sr = True
                    to_delete_req.append(rec_id)

                except Empty:
                    if time.time() - recordings[rec_id].time_sent_to_sr > 3:  # no response from sr for 3 sec -> timeout
                        # print("no response for request %d in 3 sec -> timeout" % (rec_id))
                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                        recordings[rec_id].is_back_from_sr = True
                        to_delete_req.append(rec_id)

            for req in to_delete_req:
                del sr_requests[req]

            ##################################################################################      
            # here we go through our recordings and handle them based on their current status
            ####################################################################################
            to_delete = []
            if self.visualization:
                rec_info_to_vis = []
            for rec_id, rec in recordings.iteritems():

                if self.visualization:
                    if not rec.stopped:
                        rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2],
                                                200])  # 200 is the size of the blob
                    else:
                        rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2], 50])

                if rec.new:
                    rospy.loginfo("new recording ", rec_id)
                    # get angles to all known speakers
                    rec.get_angles_to_all_speakers(self.speakers, rec.startpos)

                    # if it is wihthin a certain range to a known speaker, assign it to him
                    if len(self.speakers) > 0 and rec.angles_to_speakers[0][1] < 35:  # degree
                        rospy.loginfo("preliminary assigning recording %d to speaker %d, angle is %d" % (
                            rec_id, rec.angles_to_speakers[0][0], rec.angles_to_speakers[0][1]))
                        rec.preliminary_speaker_id = rec.angles_to_speakers[0][0]
                        rec.final_speaker_id = rec.preliminary_speaker_id  # this will be overwritten later

                    else:
                        # create a new speaker
                        self.num_speakers += 1
                        new_id = self.num_speakers
                        self.speakers[new_id] = Speaker(new_id, rec.startpos)
                        rec.preliminary_speaker_id = new_id
                        rec.final_speaker_id = rec.preliminary_speaker_id  # this will be overwritten later
                        rec.created_new_speaker = True
                        closest_ang = -999
                        if len(rec.angles_to_speakers) > 0:
                            closest_ang = rec.angles_to_speakers[0][1]
                        rospy.loginfo("creating new speaker %d for recording %d, closest angle is %d" % (
                            new_id, rec_id, closest_ang))

                        if self.num_speakers == 1:
                            rec.send_to_trainer = True

                    rec.new = False

                elif not rec.was_sent_sr and rec.audio.shape[
                    0] > 16000 * 3:  # its longer than 3 sec, time to send it to speaker recognition
                    sr_requests[rec_id] = Queue(maxsize=1)
                    self.sr.test(rec.audio, rec.preliminary_speaker_id, sr_requests[rec_id])
                    rec.was_sent_sr = True
                    rec.time_sent_to_sr = time.time()

                elif rec.stopped:
                    # speaker finished, handle this
                    if not rec.alldone:
                        if rec.audio.shape[0] < 16000 * 0.4:  # everything shorter than this we simply discard
                            rospy.loginfo("recording %d was too short, discarding" % (rec_id))
                            if rec.created_new_speaker:
                                del self.speakers[rec.preliminary_speaker_id]
                                rospy.loginfo("thus also deleting seaker", rec.preliminary_speaker_id)
                            rec.alldone = True
                    if not rec.alldone:
                        if (rec.was_sent_sr and rec.is_back_from_sr) or (not rec.was_sent_sr):
                            if not rec.was_sent_sr:
                                # it seems like this has been to short to be sent to
                                rec.final_speaker_id = rec.preliminary_speaker_id
                            self.speakers[rec.final_speaker_id].pos = rec.currentpos

                            if rec.created_new_speaker and rec.sr_changed_speaker:
                                try:
                                    del self.speakers[rec.preliminary_speaker_id]
                                except:
                                    rospy.loginfo("Error deleting preliminary speaker ", rec.preliminary_speaker_id)

                            # TODO:
                            # send to speech to text
                            text = self.stt.get_text(rec.audio)
                            rospy.loginfo("\n\n")
                            rospy.loginfo("Speaker {}: ".format(rec.final_speaker_id) + text.encode('utf-8'))
                            rospy.loginfo("\n\n")

                            # send this to trainer
                            if (rec.send_to_trainer):
                                self.sr.train(rec.final_speaker_id, rec.audio)
                                rospy.loginfo("sending recording %d to trainer" % (rec_id))

                            rospy.loginfo("succesfully handeld recording ", rec_id)
                            rec.alldone = True

                        else:
                            pass  # wait for the response of sr

                if rec.alldone:
                    to_delete.append(rec_id)

            for rec_id in to_delete:
                del recordings[rec_id]

            if self.visualization:
                try:
                    self.main_to_vis_queue.put({'speakers': self.speakers, 'recordings': rec_info_to_vis}, block=False)
                except Full:
                    # print("couldn't put data into visualization queue, its full")
                    pass
            # kevins ros changes
            # for normal here should come a rate.sleep but maybe i just let it commented out
            #rate.sleep()

        print("SAM is done.")
        self.merger.stop()
        if self.visualization:
            self.visualizer.stop()
