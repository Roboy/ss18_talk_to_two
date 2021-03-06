from visualizer import Visualizer
import numpy as np
from Queue import Empty
import rospy
#from roboy_cognition_msgs.msg import AudioLocation
import time
from std_msgs.msg import Int32
from roboy_cognition_msgs.srv import SetPoint
from led_visualizer import led_by_angle
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


class RosVisualizer(Visualizer):
    """
    Specialized Visualizer class, that visualizes the speaker by using the LEDs
    """
    def __init__(self, inq):
        Visualizer.__init__(self, inq)
        self.ledmode_pub = rospy.Publisher("/roboy/control/matrix/leds/mode/simple", Int32, queue_size=1)
        self.led_point = rospy.ServiceProxy('/roboy/control/matrix/leds/point/service', SetPoint)
        self.idle_timeout = time.time()
        self.idle_even = True
        self.idle = True

    def run(self):

        start = time.time()
        while not self.please_stop.is_set() and not rospy.is_shutdown():
            # wait for data to arrive
            latest_data = self.inq.get(block=True)

            # sometime multiple arrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_data = self.inq.get(block=False)
                except Empty:
                    break

            rec_for_vis = latest_data['recordings']

            if self.idle:
                if time.time() - start > 2:
                    msg = Int32()
                    msg.data = 9
                    self.ledmode_pub.publish(msg)
                    start = time.time()
            else:
                if len(rec_for_vis) > 0:
                    rec_for_vis = np.array(rec_for_vis)
                    record_leds = []
                    speaker_id = []
                    for i in range(0, len(rec_for_vis), 2):
                        speaker_id.append(0)
                        record_leds.append(led_by_angle(np.arctan2(rec_for_vis[i, 1], rec_for_vis[i, 2]) * 180/np.pi))

                    for r_led in record_leds:
                        try:
                            if self.led_point(r_led):
                                rospy.logdebug("led point did work")
                            else:
                                rospy.logdebug("led point didn't work")
                        except rospy.ServiceException, e:
                            print "Service called failed: %s" % e
                # else:
                #     msg = Int32()
                #     msg.data = 2
                #     self.ledmode_pub.publish(msg)

        print("stopping visualization")

    def stop(self):
        self.please_stop.set()

