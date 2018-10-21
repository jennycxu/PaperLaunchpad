from common.core import *
from common.gfxutil import *
from common.audio import *
from common.mixer import *
from common.note import *
from common.wavegen import *
from common.wavesrc import *
from launchpad import Launchpad

import time

# Main app
class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        self.audio = Audio(2)# two channel
        self.mixer = Mixer()

        self.audio.set_generator(self.mixer)
        self.wave_file_gen = WaveGenerator(WaveFile("data/shelter.wav"))
        self.drum_loop = WaveGenerator(WaveFile("data/drumloop.wav"),True)
        self.kick_loop = WaveGenerator(WaveFile("data/kick.wav"))
        self.tune_loop = WaveGenerator(WaveFile("data/tune.wav"))
        self.snare_loop = WaveGenerator(WaveFile("data/snare.wav"))

        self.launchpad = []
        self.launchpad.append(self.wave_file_gen)
        self.launchpad.append(self.drum_loop)
        self.launchpad.append(self.kick_loop)
        self.launchpad.append(self.tune_loop)
        self.launchpad.append(self.snare_loop)

        self.mixer.add(self.wave_file_gen)
        self.mixer.add(self.tune_loop)
        self.mixer.add(self.snare_loop)
        self.mixer.add(self.drum_loop)
        self.mixer.add(self.kick_loop)
        self.drum_loop.play()
        self.wave_file_gen.pause()
        self.kick_loop.play()
        self.tune_loop.play()
        self.snare_loop.play()
        

        self.L = Launchpad(self.play_audio)
        # print('HI THERE\n HI THERE')
        self.L.calibration_mode()

    def play_audio(self, index):
        print("PLAY THIS AUDIO " , index)
        if(index == 1):
            self.launchpad[1].play_toggle()
        

    def on_update(self) :
        self.audio.on_update()
        
        # print(self.L.is_calibrating)
        if self.L.is_calibrating:
            pass
        else:
            self.L.main()

    def on_key_down(self,keycode,modifier):
        if(keycode[1] == 'c'):
            self.L.calibration_mode()
        elif(keycode[1] == 'q'):
            raise SystemExit
        elif(keycode[1] == 'a'):
            self.play_audio(1)
        elif(keycode[1] == 's'):
            self.play_audio(2)
            


run(MainWidget)