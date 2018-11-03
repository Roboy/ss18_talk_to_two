import traceback
import bing_voice

# kevins ros changes
import rospy
from std_msgs.msg import String

######hier bing key einsetzen
BING_KEY = '5d655632276744b388fce13c1045c757'

class T2t_stt:
    def __init__(self):
        self.pub = rospy.Publisher("stt", String, queue_size=10)
        if BING_KEY != '':
            self.bing = bing_voice.BingVoice(BING_KEY)
        else:
            pass
        
    def get_text(self, audio):
        while 1:
            # recognize speech using Microsoft Bing Voice Recognition
            try:
                # pdb.set_trace()
                if BING_KEY != '':
                    text = self.bing.recognize(audio, language='en-US')
                else:
                    text = "Bing key is not set"
                # pdb.set_trace()
                output_text = 'Bing:' + text.encode('utf-8')
                self.pub.publish(output_text)
                return text
            except bing_voice.UnknownValueError:
                output_text = "Microsoft Bing Voice Recognition could not understand audio, going to try it again"
                self.pub.publish(output_text)
            except bing_voice.RequestError as e:
                output_text = "Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e)
                self.pub.publish(output_text)
                return "Error"
            except Exception as e:
                output_text = "Generic Bing Error", e
                self.pub.publish(output_text)
                return "Error"
