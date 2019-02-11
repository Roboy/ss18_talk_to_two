import threading
from Queue import Queue
from Queue import Empty

from audio_receiver import Audio_Receiver
from id_receiver import Id_Receiver


# Merges to two continuous asynchronous streams of id and audio together, to a chunked stream of tagged audio data
class Merger(threading.Thread):

    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.please_stop = threading.Event()

        self.id_to_merger_queue = Queue(maxsize=50)
        self.audio_to_merger_queue = Queue(maxsize=1000)
        self.id_recv = Id_Receiver(self.id_to_merger_queue)
        self.audio_recv = Audio_Receiver(self.audio_to_merger_queue)

        self.outq = outq

    def run(self):
        self.id_recv.start()
        self.audio_recv.start()

        while self.id_recv.is_alive() and self.audio_recv.is_alive() and not self.please_stop.is_set():

            # wait for new audio data
            try:
                latest_audio = self.audio_to_merger_queue.get(block=True, timeout=1)
            except Empty:
                continue  # restart loop, but check again if we maybe got a stop signal

            # get the latest id update (empties queue and save the last one)
            while 1:
                try:
                    latest_id = self.id_to_merger_queue.get(block=False)
                except Empty:
                    break

            # get id data and put it into a list of 4 lists
            # each of the 4 will contain odas_id, x,y,z,activity
            id_info = []
            for i in range(len(latest_id['src'])):
                id_info.append([latest_id['src'][i]['id'], latest_id['src'][i]['x'], latest_id['src'][i]['y'],
                                latest_id['src'][i]['z'], latest_id['src'][i]['activity']])

            # merge in a dict and put into a queue
            nextout = {'audio_data': latest_audio, 'id_info': id_info}

            if self.outq.qsize() > self.outq.maxsize - 20:
                print("merger out queue has grown to large, discarding some, this should rarely happen!!!!!!")
                for i in range(20):  # q is almost full, discard some data
                    try:
                        self.outq.get(block=False)
                    except Empty:
                        pass
            self.outq.put(nextout)  # this is blocking and thread safe

        if self.please_stop.is_set():
            print("Merger is stopping as externally requested.")
        else:
            print("Merger is stopping as one of the receivers has stopped.")
        self.id_recv.stop()
        self.audio_recv.stop()

    def stop(self):
        self.please_stop.set()
