import sys
# sys.path.append('/home/parallels/catkin_ws/src/roboy_matrix_utils/led_control/src')
sys.path.append('/home/pi/ros_catkin_ws/src/roboy_matrix_utils/led_control/src')

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
        self.speaker_location_pub = rospy.Publisher("/roboy/cognition/audio/speaker/location", AudioLocation)
        self.record_location_pub = rospy.Publisher("/roboy/cognition/audio/record/location", AudioLocation)
        self.idle_timeout = time.time()
        self.idle_even = True
        self.idle = True

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

            if self.idle:
                self.idle_light()
            else:
                pixels = [0, 0, 0, 0] * 36

                if len(rec_for_vis) > 0:
                    rec_for_vis = np.array(rec_for_vis)
                    record_leds = []
                    speaker_id = []
                    for i in range(0, len(rec_for_vis), 2):
                        speaker_id.append(0)
                        record_leds.append(led_by_angle(np.arctan2(rec_for_vis[i, 1], rec_for_vis[i, 2]) * 180/np.pi))

                    for r_led in record_leds:
                        pixels[4 * r_led] = 0
                        pixels[4 * r_led + 1] = 200
                        pixels[4 * r_led + 2] = 200
                        pixels[4 * r_led + 3] = 50

                self.leds.write_pixels(pixels)
        print("stopping visualization")

    def stop(self):
        self.please_stop.set()

    def idle_light(self):
        if self.idle_timeout - time.time() >= 1:
            self.idle_even = not self.idle_even
        pixels = []
        for i in range(36):
            if self.idle_even:
                if i % 2 == 0:
                    pixels += [0, 0, 50, 0]
                else:
                    pixels += [0, 0, 0, 0]
            else:
                if i % 2 == 0:
                    pixels += [0, 0, 0, 0]
                else:
                    pixels += [0, 0, 50, 0]
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

