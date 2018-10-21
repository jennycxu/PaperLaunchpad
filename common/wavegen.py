#####################################################################
#
# wavegen.py
#
# Copyright (c) 2018, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


import numpy as np

# generates audio data by asking an audio-source (ie, WaveFile) for that data.
class WaveGenerator(object):
    def __init__(self, wave_source, loop=False):
        super(WaveGenerator, self).__init__()
        self.source = wave_source
        self.loop = loop
        self.frame = 0
        self.paused = False
        self._release = False
        self.gain = 1.0

    def reset(self):
        self.paused = True
        self.frame = 0

    def play_toggle(self):
        self.paused = not self.paused

    def play(self):
        self.paused = False

    def pause(self):
        self.paused = True

    def release(self):
        self._release = True

    def set_gain(self, g):
        self.gain = g

    def get_gain(self):
        return self.gain

    def generate(self, num_frames, num_channels) :
        if self.paused:
            output = np.zeros(num_frames * num_channels)
            return (output, True)

        else:
            # get data based on our position and requested # of frames
            output = self.source.get_frames(self.frame, self.frame + num_frames)

            # check for end-of-buffer condition:
            actual_num_frames = len(output) // num_channels
            continue_flag = actual_num_frames == num_frames

            # advance current-frame
            self.frame += actual_num_frames

            # looping. If we got to the end of the buffer, don't actually end.
            # Instead, read some more from the beginning
            if self.loop and not continue_flag:
                continue_flag = True
                remainder = num_frames - actual_num_frames
                output = np.append(output, self.source.get_frames(0, remainder))
                self.frame = remainder

            if self._release:
                continue_flag = False

            # zero-pad if output is too short (may happen if not looping / end of buffer)
            shortfall = num_frames * num_channels - len(output)
            if shortfall > 0:
                output = np.append(output, np.zeros(shortfall))

            # return
            return (output * self.gain, continue_flag)



class SpeedModulator(object):
    def __init__(self, generator, speed = 1.0):
        super(SpeedModulator, self).__init__()
        self.generator = generator
        self.speed = speed

    def set_speed(self, speed) :
        self.speed = speed

    def generate(self, num_frames, num_channels) :
        # optimization if speed is 1.0
        if self.speed == 1.0:
            return self.generator.generate(num_frames, num_channels)

        # otherwise, we need to ask self.generator for a number of frames that is
        # larger or smaller than num_frames, depending on self.speed
        adj_frames = int(round(num_frames * self.speed))

        # get data from generator
        data, continue_flag = self.generator.generate(adj_frames, num_channels)

        # split into multi-channels:
        data_chans = [ data[n::num_channels] for n in range(num_channels) ]

        # stretch or squash data to fit exactly into num_frames
        from_range = np.arange(adj_frames)
        to_range = np.arange(num_frames) * (float(adj_frames) / num_frames)
        resampled = [ np.interp(to_range, from_range, data_chans[n]) for n in range(num_channels) ]

        # convert back by interleaving into a single buffer
        output = np.empty(num_channels * num_frames, dtype=np.float32)
        for n in range(num_channels) :
            output[n::num_channels] = resampled[n]

        return (output, continue_flag)
