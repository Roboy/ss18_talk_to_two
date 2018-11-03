import sys
# sys.path.append('/home/parallels/catkin_ws/src/roboy_matrix_utils/led_control/src')
sys.path.append('/home/pi/ros_catkin_ws/src/roboy_matrix_utils/led_control/src')

from leds import MatrixLeds
from visualizer import Visualizer
import numpy as np
from Queue import Empty
import rospy
from roboy_communication_cognition.msg import AudioLocation

color_array = [
    [50, 0, 0, 0],
    [0, 50, 0, 0],
    [0, 0, 50, 0],
    [50, 50, 0, 0],
    [50, 0, 50, 0],
    [50, 0, 0, 50],
    [0, 50, 50, 0]
]


class LedVisualizer(Visualizer):
    """
    Specialized Visualizer class, that visualizes the speaker by using the LEDs
    """
    def __init__(self, inq):
        Visualizer.__init__(self, inq)
        self.leds = MatrixLeds()
        self.speaker_location_pub = rospy.Publisher("/roboy/cognition/audio/speaker/location", AudioLocation)
        self.record_location_pub = rospy.Publisher("/roboy/cognition/audio/record/location", AudioLocation)

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
        location_id = 0
        while not self.please_stop.is_set() and not rospy.is_shutdown():
            # wait for data to arrive
            latest_data = self.inq.get(block=True)

            # sometime multiple rrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_data = self.inq.get(block=False)
                except Empty:
                    break

            speakers_for_vis = []
            # speakers_for_vis.append([0, 0, 0, 0, 300])  # center point
            for sp_id, sp in latest_data['speakers'].iteritems():
                angle = np.arctan2(sp.pos[0], sp.pos[1]) * 180 / np.pi
                speakers_for_vis.append([sp_id, sp.pos[0], sp.pos[1], sp.pos[2], 100, angle, led_by_angle(angle)])

            rec_for_vis = latest_data['recordings']

            # ax.clear()
            # TODO: fic colors
            pixels = [0, 0, 0, 0] * 36
            vis_count = 0
            if (len(speakers_for_vis) > 0):
                location_id += 1
                speakers_for_vis = np.array(speakers_for_vis)
                # ax.scatter(speakers_for_vis[:,1], speakers_for_vis[:,2], speakers_for_vis[:,3], s=speakers_for_vis[:,4])
                msg = AudioLocation()
                msg.id = location_id
                msg.type = "speaker"
                msg.x = speakers_for_vis[:, 1]
                msg.y = speakers_for_vis[:, 2]
                msg.z = speakers_for_vis[:, 3]
                msg.azimuth = speakers_for_vis[:, 5]
                msg.led = speakers_for_vis[:, 6]


                self.speaker_location_pub.publish(msg)

                for sp in speakers_for_vis:  # display the assigned id
                    #if sp[0] > 0:
                    pixels[4 * sp[6]] += color_array[vis_count][0]
                    pixels[4 * sp[6] + 1] += color_array[vis_count][1]
                    pixels[4 * sp[6] + 2] += color_array[vis_count][2]
                    pixels[4 * sp[6] + 3] += color_array[vis_count][3]
                    if vis_count < len(color_array):
                        vis_count += 1
                    else:
                        vis_count = 0
                        # ax.text(sp[1], sp[2], sp[3],  '%s' % (str(int(sp[0]))), size=15)
            if (len(rec_for_vis) > 0):
                rec_for_vis = np.array(rec_for_vis)
                # ax.scatter(rec_for_vis[:,1], rec_for_vis[:,2], rec_for_vis[:,3], s=rec_for_vis[:,4])
                msg = AudioLocation()
                msg.id = location_id
                msg.type = "record"
                msg.x = rec_for_vis[:, 1]
                msg.y = rec_for_vis[:, 2]
                msg.z = rec_for_vis[:, 3]
                self.record_location_pub.publish(msg)
                # for rec in rec_for_vis:  # display the assigned id
                #     # ax.text(rec[1],rec[2],rec[3],  '%s' % (str(int(rec[0]))), size=15, color='red')
                #     pass
                speaker_id = []
                for i in range(0, len(rec_for_vis), 2):
                    x1 = np.array(rec_for_vis[i, 1], rec_for_vis[i, 2], rec_for_vis[i, 3])
                    min_dist = 100
                    speaker_id.append(0)
                    for sp in speakers_for_vis:
                        x2 = np.array(sp[1], sp[2], sp[3])
                        dist = np.linalg.norm(x1 - x2)
                        if dist < min_dist:
                            min_dist = dist
                            speaker_id[len(speaker_id) - 1] = sp[0]

                for s_id in speaker_id:
                    pixels[4 * speakers_for_vis[s_id - 1] + 3] += 100

            self.leds.write_pixels(pixels)
            # ax.set_xlim3d(-1.2,1.2) #dont know why, but otherwise it keeps changin them...
            # ax.set_ylim3d(-1.2,1.2)
            # ax.set_zlim3d(-1.2,1.2)
            # #plt.pause(0.001)
            # fig.canvas.draw()

            # print("elapsed time:", time.time() - last_time)
            # last_time = time.time()

        # plt.close()
        print("stopping visulaization")

    def stop(self):
        self.please_stop.set()


def led_by_angle(angle):
    """
    maps euler angle to led number, based on the MAtrix Creator LED allignment
    :param angle: euler angle between -1 and 1 as a float
    :return: number of according led
    """
    zero_led = 8  # counted from 0 to 35
    led_offset = int(angle / 10)

    # zero led + the mapped offset plus 1
    # such that leds whos angles  are closer to the 17,  get 17 instead of 16
    led_to_be = led_offset - 1 + 8

    # map led if over 36
    # like 36 will get 0 and so on
    if led_to_be < 0:
        led_to_be += 36

    return led_to_be

