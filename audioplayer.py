from common.core import *
from common.gfxutil import *
from common.audio import *
from common.mixer import *
from common.note import *
from common.wavegen import *
from common.wavesrc import *
from launchpad import Launchpad

# Main app
class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        self.audio = Audio(2)# two channel
        self.mixer = Mixer()

        self.audio.set_generator(self.mixer)
        self.wave_file_gen = WaveGenerator(WaveFile("data/shelter.wav"))
        self.wave_file_gen.play()
        self.mixer.add(self.wave_file_gen)

        self.L = Launchpad(self.play_audio)

    def play_audio(self, index):
        print("PLAY THIS AUDIO " , index)

    def on_update(self) :
        self.audio.on_update()
        self.L.main()

    def on_key_down(self,keycode,modifier):
        if(keycode[1] == 'c'):
            self.L.calibration_mode()
        elif(keycode[1] == 'q'):
            raise SystemExit

run(MainWidget)