import sys
# sys.path.append('/home/parallels/catkin_ws/src/roboy_matrix_utils/led_control/src')
sys.path.append('/home/pi/ros_catkin_ws/src/roboy_matrix_utils/led_control/src')

from leds import MatrixLeds
from visualizer import Visualizer
import numpy as np
from Queue import Empty


class LedVisualizer(Visualizer):
    """
    Specialized Visualizer class, that visualizes the speaker by using the LEDs
    """
    def __init__(self, inq):
        Visualizer.__init__(self, inq)
        self.leds = MatrixLeds()

    def run(self):

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # plt.ion()
        # ax.autoscale(enable=False)
        # ax.set_xlim3d(-1.2,1.2)
        # ax.set_ylim3d(-1.2,1.2)
        # ax.set_zlim3d(-1.2,1.2)
        #
        # fig.show()
        # fig.canvas.draw()

        # last_time = time.time()

        while not self.please_stop.is_set():
            # wait for data to arrive
            latest_data = self.inq.get(block=True)

            # sometime multiple rrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_data = self.inq.get(block=False)
                except Empty:
                    break

            speakers_for_vis = []
            speakers_for_vis.append([0, 0, 0, 0, 300])  # center point
            for sp_id, sp in latest_data['speakers'].iteritems():
                speakers_for_vis.append([sp_id, sp.pos[0], sp.pos[1], sp.pos[2], 100])

            rec_for_vis = latest_data['recordings']

            # ax.clear()
            # TODO: fic colors
            if (len(speakers_for_vis) > 0):
                speakers_for_vis = np.array(speakers_for_vis)
                # ax.scatter(speakers_for_vis[:,1], speakers_for_vis[:,2], speakers_for_vis[:,3], s=speakers_for_vis[:,4])
                print "------------------------------------"
                print "speakers:"
                print "x : ", speakers_for_vis[:, 1], "| y : ", speakers_for_vis[:, 2], "| z: ", speakers_for_vis, "| marker size: ", speakers_for_vis[:, 4]
                print "------------------------------------"
                if len(speakers_for_vis[:, 1]) >= 4:
                    self.leds.visualize_da_4(led_by_angle(speakers_for_vis[1, 1]), led_by_angle(speakers_for_vis[2, 1]),
                                             led_by_angle(speakers_for_vis[3, 1]), led_by_angle(speakers_for_vis[4, 1]))
                for sp in speakers_for_vis:  # display the assigned id
                    if sp[0] > 0:
                        pass
                        # ax.text(sp[1], sp[2], sp[3],  '%s' % (str(int(sp[0]))), size=15)
            if (len(rec_for_vis) > 0):
                rec_for_vis = np.array(rec_for_vis)
                # ax.scatter(rec_for_vis[:,1], rec_for_vis[:,2], rec_for_vis[:,3], s=rec_for_vis[:,4])
                print "------------------------------------"
                print "recordings: "
                print "x : ", rec_for_vis[:, 1], "| y : ", rec_for_vis[:,
                                                                2], "| z: ", rec_for_vis, "| marker size: ", rec_for_vis[
                                                                                                                  :, 4]
                print "------------------------------------"
                if len(rec_for_vis[:, 1]) >= 4:
                    self.leds.visualize_da_4(led_by_angle(rec_for_vis[0, 1]), led_by_angle(rec_for_vis[1, 1]),
                                             led_by_angle(rec_for_vis[2, 1]), led_by_angle(rec_for_vis[3, 1]))
                for rec in rec_for_vis:  # display the assigned id
                    pass
                    # ax.text(rec[1],rec[2],rec[3],  '%s' % (str(int(rec[0]))), size=15, color='red')
            # ax.set_xlim3d(-1.2,1.2) #dont know why, but otherwise it keeps changin them...
            # ax.set_ylim3d(-1.2,1.2)
            # ax.set_zlim3d(-1.2,1.2)
            # #plt.pause(0.001)
            # fig.canvas.draw()

            # print("elapsed time:", time.time() - last_time)
            # last_time = time.time()

        # plt.close()
        print("stopping visulaization")


def led_by_angle(angle):
    """
    maps euler angle to led number, based on the MAtrix Creator LED allignment
    :param angle: euler angle between -1 and 1 as a float
    :return: number of according led
    """
    zero_led = 25  # counted from 0 to 35
    led_offset = int(angle * 17)

    # zero led + the mapped offset plus 1
    # such that leds whos angles  are closer to the 17,  get 17 instead of 16
    led_to_be = zero_led - led_offset + 1

    # map led if over 36
    # like 36 will get 0 and so on
    if led_to_be >= 36:
        led_to_be -= 36

    return led_to_be

