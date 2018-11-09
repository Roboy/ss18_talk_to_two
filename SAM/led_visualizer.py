import sys
#sys.path.append('/home/parallels/catkin_ws/src/roboy_matrix_utils/led_control/src')
sys.path.append('/home/pi/workspace/src/roboy_matrix_utils/led_control/src')

from leds import MatrixLeds
from visualizer import Visualizer
import numpy as np
from Queue import Empty
import rospy
from roboy_communication_cognition.msg import AudioLocation
import time

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
        self.idle_timeout = time.time()
        self.idle_even = True
        self.idle = False
        self.rec_loc_pub = rospy.Publisher('/roboy/cognition/audio/record/location', AudioLocation)

    def run(self):

        while not self.please_stop.is_set() and not rospy.is_shutdown():
            # wait for data to arrive
            latest_data = self.inq.get(block=True)

            # sometime multiple rrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_data = self.inq.get(block=False)
                except Empty:
                    break

            rec_for_vis = latest_data['recordings']

            msg = AudioLocation()
            msg.x = rec_for_vis[:, 1]
            msg.y = rec_for_vis[:, 2]
            msg.z = rec_for_vis[:, 3]
            self.rec_loc_pub.publish(msg)

            if self.idle:
                self.idle_light()
            else:
                pixels = [0, 0, 0, 0] * 36

                if len(rec_for_vis) > 0:
                    rec_for_vis = np.array(rec_for_vis)
                    record_leds = []
                    speaker_id = []
                    for i in range(0, len(rec_for_vis)):
                        speaker_id.append(0)
                        record_leds.append(led_by_angle(np.arctan2(rec_for_vis[i, 1], rec_for_vis[i, 2]) * 180/np.pi))

                    for r_led in record_leds:
                        # find the other leds
                        sup_leds = [r_led + 1, r_led - 1, r_led + 2, r_led -2]
                        for i in range(len(sup_leds)):
                            if sup_leds[i] < 0:
                                sup_leds[i] += 36
                            if sup_leds[i] >= 36:
                                sup_leds[i] -= 36

                        pixels[4 * r_led] = 0
                        pixels[4 * r_led + 1] = 200
                        pixels[4 * r_led + 2] = 200
                        pixels[4 * r_led + 3] = 50

                        sup_cnt = 0
                        for s_l in sup_leds:
                            try:
                                if sup_cnt < 2:
                                    pixels[4 * s_l] = 0
                                    pixels[4 * s_l + 1] = 150
                                    pixels[4 * s_l + 2] = 150
                                    pixels[4 * s_l + 3] = 30
                                    sup_cnt += 1
                                else:
                                    pixels[4 * s_l] = 0
                                    pixels[4 * s_l + 1] = 100
                                    pixels[4 * s_l + 2] = 100
                                    pixels[4 * s_l + 3] = 10
                                    sup_cnt += 1
                            except IndexError:
                                rospy.logerr("caught an IndexError.r_led : " + str(r_led) + " s_l : " + str(s_l))

                self.leds.write_pixels(pixels)
        print("stopping visualization")

    def stop(self):
        self.please_stop.set()

    def idle_light(self):
        if time.time() - self.idle_timeout >= 1:
            self.idle_even = not self.idle_even
            self.idle_timeout = time.time()
            pixels = []
            for i in range(36):
                if self.idle_even:
                    if i % 2 == 0:
                        pixels += [0, 0, 20, 0]
                    else:
                        pixels += [0, 0, 0, 0]
                else:
                    if i % 2 == 0:
                        pixels += [0, 0, 0, 0]
                    else:
                        pixels += [0, 0, 20, 0]
            self.leds.write_pixels(pixels)


def led_by_angle(angle):
    """
    maps azimuthal angle to led number, based on the MAtrix Creator LED allignment
    :param angle: azimuthal angle between -180 and 180 as a float
    :return: number of according led
    """
    zero_led = 8  # counted from 0 to 35
    led_offset = int(angle / 10)

    # the calculated led offset -1 ( because we start counting at 0)
    # plus the "zero" led
    led_to_be = led_offset - 1 + zero_led

    # map led if under 0
    # everything smaller than 0 just substracts 36 and gets the new number then
    if led_to_be < 0:
        led_to_be += 36

    # make sure we return an integer
    return int(led_to_be)

