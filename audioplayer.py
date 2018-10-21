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

        keys = ["shelter","workit","harder","doit","stronger","drop","drop2","drop3","drop4","drop5","getdown","getdownbuild","getup","overtime","again","build"]
        self.songs = {}
        for key in keys:
            self.songs[key] = WaveFile("data/" + key + ".wav")

        self.shelter_gen = WaveGenerator(self.songs['shelter'],True)
        self.workit_gen = WaveGenerator(self.songs['workit'])
        self.doit_gen = WaveGenerator(self.songs['doit'])
        self.harder_gen = WaveGenerator(self.songs['harder'])
        self.stronger_gen = WaveGenerator(self.songs['stronger'])
        self.drop_gen = WaveGenerator(self.songs['drop'],True)
        self.drop_gen2 = WaveGenerator(self.songs['drop2'],True)
        self.drop_gen3 = WaveGenerator(self.songs['drop3'],True)
        self.drop_gen4 = WaveGenerator(self.songs['drop4'],True)
        self.drop_gen5 = WaveGenerator(self.songs['drop5'],True)
        self.getdown_gen = WaveGenerator(self.songs['getdown'])
        self.getdownbuild_gen = WaveGenerator(self.songs['getdownbuild'],True)
        self.getup_gen = WaveGenerator(self.songs['getup'])
        self.overtime_gen = WaveGenerator(self.songs['overtime'])
        self.again_gen = WaveGenerator(self.songs['again'])
        self.build_gen = WaveGenerator(self.songs['build'],True)

        self.gens = []
        self.gens.append(self.shelter_gen)
        self.gens.append(self.workit_gen)
        self.gens.append(self.doit_gen)
        self.gens.append(self.harder_gen)
        self.gens.append(self.stronger_gen)
        self.gens.append(self.drop_gen)
        self.gens.append(self.drop_gen2)
        self.gens.append(self.drop_gen3)
        self.gens.append(self.drop_gen4)
        self.gens.append(self.drop_gen5)
        self.gens.append(self.getdown_gen)
        self.gens.append(self.getdownbuild_gen)
        self.gens.append(self.getup_gen)
        self.gens.append(self.overtime_gen)
        self.gens.append(self.again_gen)
        self.gens.append(self.build_gen)

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
        #print("PLAY THIS AUDIO " , key, " and exists: ",key in self.launchpad.keys())
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
            self.play_audio("drop")
        elif(keycode[1] == 's'):
            self.play_audio("drop2")
        elif(keycode[1] == 'd'):
            self.play_audio("drop3")
        elif(keycode[1] == 'f'):
            self.play_audio("drop4")
        elif(keycode[1] == 'g'):
            self.play_audio("drop5")
        elif(keycode[1] == 'h'):
            self.play_audio("getdown")
        elif(keycode[1] == 'j'):
            self.play_audio("getdownbuild")
        elif(keycode[1] == 'k'):
            self.play_audio("getup")
        elif(keycode[1] == 'l'):
            self.play_audio("build")
        elif(keycode[1] == 'z'):
            self.play_audio("overtime")
        elif(keycode[1] == 'x'):
            self.play_audio("again")
            


run(MainWidget)