import traceback
import bing_voice


######hier bing key einsetzen
BING_KEY = 'b62d103033b94881b01bf73c1d44ac60'

class T2t_stt:
    def __init__(self):
        
        if BING_KEY != '':
            self.bing = bing_voice.BingVoice(BING_KEY)
        else:
            pass
        
    def get_text(self, audio):
        # recognize speech using Microsoft Bing Voice Recognition
        try:
            # pdb.set_trace()
            if BING_KEY != '':
                text = self.bing.recognize(audio, language='en-US')
            else:
                text = "Bing key is not set"
            # pdb.set_trace()
            print('Bing:' + text.encode('utf-8'))
            return text
        except bing_voice.UnknownValueError:
            traceback.print_exc()
            print("Microsoft Bing Voice Recognition could not understand audio")
            return "Error"
        except bing_voice.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
            return "Error"
        except Exception as e:
            print("Generic Bing Error", e)
            return "Error"
        
        
