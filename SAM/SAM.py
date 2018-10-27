#!/usr/bin/env python
# import threading
import time
import numpy as np
from Queue import Queue
from Queue import Empty as q_Empty
from Queue import Full

from multiprocessing import Process
from multiprocessing import Queue as mult_Queue

from merger import Merger
from visualizer import Visualizer
from speaker import Speaker
from recording import Recording
from t2t_stt import T2t_stt

from speaker_recognition.speaker_recognition import Speaker_recognition

# kevins ros changes
import rospy
from std_msgs.msg import String
from roboy_communication_cognition.srv import RecognizeSpeech
from roboy_communication_control.msg import ControlLeds
from std_msgs.msg import Empty as msg_Empty, Int32


class SAM:

    def __init__(self, visualization=False, speaker_recognition=False):
        self.merger_to_main_queue = Queue(maxsize=1000)  # very roughly 30sec
        self.merger = Merger(self.merger_to_main_queue)

        self.visualization = visualization
        if self.visualization:
            self.main_to_vis_queue = Queue(maxsize=50)
            self.visualizer = Visualizer(self.main_to_vis_queue)

        self.speakers = {}
        self.num_speakers = 0
        self.stt = T2t_stt()
        self.speaker_recognition = speaker_recognition
        if self.speaker_recognition:
            self.sr = Speaker_recognition()
        self.text_queue = mult_Queue()
        self.bing_allowed = False

    def handle_service(self, req):
        rospy.loginfo("entered handle service")
        msg = ControlLeds()
        msg.mode = 2
        msg.duration = 0
        self.ledmode_pub.publish(msg)
        queue = mult_Queue()
        self.bing_allowed = True
        p = Process(target=self.stt_subprocess, args=(queue,))
        p.start()
        p.join()
        msg = msg_Empty()
        self.ledfreeze_pub.publish(msg)
        self.bing_allowed = False
        return queue.get()

    def stt_subprocess(self, q):
        # clear the text queue
        # rospy.loginfo("clear the text queue")
        # while not self.text_queue.empty():
        #     rospy.loginfo("got an item from the queue ->" + self.text_queue.get())

        # wait for the next text to arrive
        rospy.loginfo("going to wait for the text_queue to be filled again")
        rate = rospy.Rate(1)
        while self.text_queue.empty() and not rospy.is_shutdown():
            rospy.loginfo("still waiting, current length : " + str(self.text_queue.qsize()))
            rate.sleep()

        # put it into the return queue
        rospy.loginfo("got one and put it into the dedicated queue")
        q.put(self.text_queue.get())

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
        pub = rospy.Publisher('SAM_output', String, queue_size=10)
        s = rospy.Service('SAM_service', RecognizeSpeech, self.handle_service)
        self.ledmode_pub = rospy.Publisher("/roboy/control/matrix/leds/mode", ControlLeds, queue_size=3)
        self.ledoff_pub = rospy.Publisher('/roboy/control/matrix/leds/off', msg_Empty, queue_size=10)
        self.ledfreeze_pub = rospy.Publisher("/roboy/control/matrix/leds/freeze", msg_Empty, queue_size=1)
        self.ledpoint_pub = rospy.Publisher("/roboy/control/matrix/leds/point", Int32, queue_size=1)
        rospy.init_node("SAM", anonymous=True)

        # operation average
        angle_list = []

        while self.merger.is_alive() and not rospy.is_shutdown():

            # we do ask for the next data block
            # maybe this is the place where i can insert a call and replace the while loop

            # wait for/get next data
            try:
                next_data = self.merger_to_main_queue.get(block=True, timeout=1)
            except q_Empty:
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
                        # a person started speaking
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
                        output_string = "both agree that rec %d is new speaker %d" % (
                            rec_id, recordings[rec_id].preliminary_speaker_id)
                        rospy.logdebug(output_string)
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
                            # check the angle the the speaker sr suggested, and depending on the certainty decide
                            # go through the list of speaker angles and find the one one which sr suggests
                            found = False
                            for (oth_id, angl) in recordings[rec_id].angles_to_speakers:
                                if oth_id == sr_id:
                                    # the further we are away the shurer sr has to be
                                    if certainty * 20 > angl:
                                        recordings[rec_id].final_speaker_id = sr_id
                                        recordings[rec_id].sr_changed_speaker = True
                                    else:
                                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                                    found = True
                                    break
                            if not found:
                                # this shouldn't happen
                                output_string = "Speaker recognition suggestested id {} for recording {}," \
                                                " which doesn't exist".format(sr_id, rec_id)
                                rospy.logerr(output_string)
                                recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id

                    output_string = "response for req %d, results is %d, certanty %d" % (rec_id, sr_id, certainty)
                    rospy.logdebug(output_string)
                    recordings[rec_id].is_back_from_sr = True
                    to_delete_req.append(rec_id)

                except q_Empty:
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

            # ---------------------------------------------------------------------------------------------------
            # new doa to led addon
            rec_info_to_vis = []
            # ---------------------------------------------------------------------------------------------------

            for rec_id, rec in recordings.iteritems():

                # print
                # print "-------------------------------"
                # print "maybe position info"
                # print "-------------------------------"
                # print "rec_id: ", rec_id
                # print "rec.currentpos[0]: ", rec.currentpos[0]
                # print "rec.currentpos[1]: ", rec.currentpos[1]
                # print "rec.currentpos[2]: ", rec.currentpos[2]
                # print "-------------------------------"
                # print
                # msg = Int32()
                # if 1 > rec.currentpos[0] >= 0.5:
                #     msg.data = 0
                #     self.ledpoint_pub.publish(msg)
                # elif 0.5 > rec.currentpos[0] >= 0:
                #     msg.data = 9
                #     self.ledpoint_pub.publish(msg)
                # elif 0 > rec.currentpos[0] >= -0.5:
                #     msg.data = 18
                #     self.ledpoint_pub.publish(msg)
                # elif -0.5 > rec.currentpos[0] >= -1:
                #     msg.data = 27
                #     self.ledpoint_pub.publish(msg)
                if self.visualization:
                    if not rec.stopped:
                        rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2],
                                                200])  # 200 is the size of the blob
                    else:
                        rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2], 50])

                # ---------------------------------------------------------------------------------------------------
                # new doa to led addon
                if not rec.stopped:
                    rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2],
                                            200])  # 200 is the size of the blob
                else:
                    rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2], 50])

                # ---------------------------------------------------------------------------------------------------

                if rec.new:
                    output_string = "new recording " + str(rec_id)
                    rospy.loginfo(output_string)
                    # get angles to all known speakers
                    rec.get_angles_to_all_speakers(self.speakers, rec.startpos)

                    # if it is wihthin a certain range to a known speaker, assign it to him
                    if len(self.speakers) > 0 and rec.angles_to_speakers[0][1] < 35:  # degree
                        output_string = "preliminary assigning recording %d to speaker %d, angle is %d" % (
                            rec_id, rec.angles_to_speakers[0][0], rec.angles_to_speakers[0][1])
                        rospy.loginfo(output_string)
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
                        output_string = "creating new speaker %d for recording %d, closest angle is %d" % (
                            new_id, rec_id, closest_ang)
                        rospy.logdebug(output_string)

                        if self.num_speakers == 1:
                            rec.send_to_trainer = True

                    rec.new = False

                elif self.speaker_recognition and (not rec.was_sent_sr and rec.audio.shape[
                    0] > 16000 * 3):  # its longer than 3 sec, time to send it to speaker recognition
                    sr_requests[rec_id] = Queue(maxsize=1)
                    self.sr.test(rec.audio, rec.preliminary_speaker_id, sr_requests[rec_id])
                    rec.was_sent_sr = True
                    rec.time_sent_to_sr = time.time()

                elif rec.stopped:
                    # speaker finished, handle this
                    if not rec.alldone:
                        if rec.audio.shape[0] < 16000 * 0.4:  # everything shorter than this we simply discard
                            output_string = "recording %d was too short, discarding" % (rec_id)
                            print output_string
                            rospy.loginfo(output_string)
                            if rec.created_new_speaker:
                                del self.speakers[rec.preliminary_speaker_id]
                                output_string = "thus also deleting speaker" + str(rec.preliminary_speaker_id)
                                rospy.logdebug(output_string)
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
                                    output_string = "Error deleting preliminary speaker " + str(rec.preliminary_speaker_id)
                                    print output_string
                                    rospy.logerr(output_string)

                            # TODO:
                            # send to speech to text
                            if self.bing_allowed:
                                text = self.stt.get_text(rec.audio)
                            else:
                                text = "bing is not allowed yet"
                            output_string = "Speaker {}: ".format(rec.final_speaker_id) + text.encode('utf-8')
                            rospy.loginfo(output_string)
                            pub.publish(output_string)

                            if self.bing_allowed:
                                self.text_queue.put(output_string)
                                rospy.logdebug("text_queue lenght in main: " + str(self.text_queue.qsize()))

                            # send this to trainer
                            if self.speaker_recognition and rec.send_to_trainer:
                                #self.sr.train(rec.final_speaker_id, rec.audio)
                                output_string = "sending recording %d to trainer" % (rec_id)
                                rospy.loginfo(output_string)

                            output_string = "succesfully handeld recording " + str(rec_id)
                            rospy.logdebug(output_string)
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
            # ---------------------------------------------------------------------------------------------------
            # new doa to led addon
            # print
            # print "------------------------------------"
            # print "speakers: "
            # print self.speakers
            # print "rec_info_to_vis: "
            # operation average
            # if len(rec_info_to_vis) > 0 and not self.bing_allowed:
            #     # print "0 -> ", rec_info_to_vis[0][0]
            #     # print "1 -> ", rec_info_to_vis[0][1]
            #     # print "2 -> ", rec_info_to_vis[0][2]
            #     # print "3 -> ", rec_info_to_vis[0][3]
            #     # print "4 -> ", rec_info_to_vis[0][4]
            #     angle_list.append(rec_info_to_vis[0][1])
            #     if len(angle_list) >= 10:
            #         publish_point_left_right(self.ledpoint_pub, sum(angle_list)/len(angle_list))
            #         angle_list = []
            # else:
            #     print "Empty dude"
            # print "------------------------------------"
            # print
            # publish_point(self.ledpoint_pub, rec_info_to_vis[1])
            # ---------------------------------------------------------------------------------------------------

        output_string = "SAM is done."
        print output_string
        rospy.loginfo(output_string)
        self.merger.stop()
        if self.visualization:
            self.visualizer.stop()


# ---------------------------------------------------------------------------------------------------
# new doa to led addon
def publish_point(pub, angle):
    msg = ControlLeds()
    if -0.125 < angle < 0.125:
        msg.data = 25
        pub.publish(msg)
    elif 0.125 < angle < 0.625:
        msg.data = 15
        pub.publish(msg)
    elif 0.625 < angle < 0.825:
        msg.data = 10
        pub.publish(msg)
    elif 0.825 < angle < 1:
        msg.data = 5
        pub.publish(msg)
    elif -1 < angle < -0.825:
        msg.data = 0
        pub.publish(msg)
    elif -0.825 < angle < -0.625:
        msg.data = 35
        pub.publish(msg)
    elif -0.625 < angle < -0.125:
        msg.data = 30
        pub.publish(msg)


def publish_point_left_right(pub, angle):
    msg = Int32()
    #msg.duration = 0
    if -1 < angle <= 0:
        msg.data = 35
        pub.publish(msg)
    elif 0 < angle <= 1:
        msg.data = 17
        pub.publish(msg)
# ---------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    sam = SAM()
    sam.run()
