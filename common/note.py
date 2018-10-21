#####################################################################
#
# note.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
from .audio import Audio

# Twelevth root of 2
kTRT = pow(2.0, 1.0/12.0)

# convert midi pitch to frequency in Hz
# A440 = midi note 69
def midi_to_frequency(n) :
    return 440.0 * pow(kTRT, (n - 69))

class NoteGenerator(object):
    sine   = (1., )
    square = (1., 0, 1/3., 0, 1/5., 0, 1/7., 0, 1/9.)
    saw    = (1., 1/2., 1/3., 1/4., 1/5., 1/6., 1/7., 1/8., 1/9.)
    tri    = (1., 0, -1/9., 0, 1/25., 0, -1/49.)

    def __init__(self, pitch, gain, duration, attack = 0.01, harmonics = (1.0,) ):
        super(NoteGenerator, self).__init__()

        self.freq = midi_to_frequency(pitch)
        self.gain = float(gain)
        self.duration = float(duration)
        self.frame = 0
        self.env = Envelope(attack, duration - attack, 2, 2)
        self.harmonics = harmonics

    def generate(self, num_frames, num_channels) :
        # normal case:
        end_frame = self.frame + num_frames
        continue_flag = True

        # check duration / end of this note
        if end_frame > self.duration * Audio.sample_rate:
            continue_flag = False

        frames = np.arange(self.frame, end_frame)          # frame range for this buffer
        factor = (2.0 * np.pi) * self.freq / Audio.sample_rate   # frequency / time conversion
        env = self.env.generate(num_frames)                # envelope

        # final output with gain and envelope
        output = self.gain * env * sin_with_harmonics( factor * frames,  self.harmonics)

        self.frame += num_frames

        # convert from mono to stereo
        if num_channels == 2:
            stereo = np.empty(num_frames * 2)
            stereo[0::2] = output
            stereo[1::2] = output
            output = stereo

        return (output, continue_flag)


def sin_with_harmonics(time, harmonics) :
    # create fundamental frequency
    signal = harmonics[0] * np.sin( time )

    # add additional harmonics
    for (h, w) in enumerate( harmonics[1:] ):
        if w != 0: # optimization for amplitude weight = 0
            signal += w * np.sin( time * (h+2))
    return signal


class Envelope(object):
    def __init__(self, attack_t, decay_t, n1, n2):
        super(Envelope, self).__init__()

        # attack / decay time parameters (converted from seconds to frames)
        self.attack_f = round(attack_t * Audio.sample_rate)
        self.decay_f =  round(decay_t * Audio.sample_rate)

        # attack / decay envelope shapes
        self.n1 = n1
        self.n2 = n2

        self.frame = 0

    def generate(self, num_frames) :
        # set up correct frame ranges:
        end_frame = self.frame + num_frames
        frames = np.arange(self.frame, end_frame)

        # boundary is the transition location between attack and decay functions
        boundary = int(np.clip(self.attack_f - self.frame, 0, num_frames))

        # attack part:
        env1 = (frames[:boundary] / self.attack_f) ** (1.0/self.n1)

        # decay part:
        env2 = 1.0 - ((frames[boundary:] - self.attack_f) / self.decay_f) ** (1.0/self.n2)

        # combine:
        env = np.append(env1, env2)

        # clamp curve to 0, so we don't get any negative values
        if end_frame > self.attack_f + self.decay_f:
            env[env < 0] = 0

        # advance frame counter
        self.frame = end_frame
        return env
