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

        keys = ["shelter","workit","harder","doit","stronger","drop"]
        self.songs = {}
        for key in keys:
            self.songs[key] = WaveFile("data/" + key + ".wav")

        self.shelter_gen = WaveGenerator(self.songs['shelter'],True)
        self.workit_gen = WaveGenerator(self.songs['workit'])
        self.doit_gen = WaveGenerator(self.songs['doit'])
        self.harder_gen = WaveGenerator(self.songs['harder'])
        self.stronger_gen = WaveGenerator(self.songs['stronger'])
        self.drop_gen = WaveGenerator(self.songs['drop'],True)

        self.gens = []
        self.gens.append(self.shelter_gen)
        self.gens.append(self.workit_gen)
        self.gens.append(self.doit_gen)
        self.gens.append(self.harder_gen)
        self.gens.append(self.stronger_gen)
        self.gens.append(self.drop_gen)

        self.launchpad = {}
        for i in range(len(self.gens)): 
            self.launchpad[keys[i]] = self.gens[i]
        
            self.mixer.add(self.gens[i])
            self.gens[i].pause()

        self.L = Launchpad(self)
        # print('HI THERE\n HI THERE')
        self.L.calibration_mode()
    # in the case that this a note that hasn't played yet 
    def reset_audio(self,key):
        #make a new instance 
        self.launchpad[key] = WaveGenerator(self.songs[key])

    def play_audio(self, key):
        print("PLAY THIS AUDIO " , key, " and exists: ",key in self.launchpad.keys())
        if(key in self.launchpad.keys()):
            if(self.launchpad[key].loop):
                self.launchpad[key].play_toggle()
            else:
                self.reset_audio(key)
                self.launchpad[key].play()
                self.mixer.add(self.launchpad[key])
    def is_loop(self,key):
        if(key in self.launchpad.keys()):
            if(self.launchpad[key].loop):
                return True
        return False 
        

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
            self.play_audio("workit")
        elif(keycode[1] == 's'):
            self.play_audio("drop")
            


run(MainWidget)