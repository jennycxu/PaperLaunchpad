#####################################################################
#
# wavesrc.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
import wave
from .audio import Audio

# Interface for reading data from a wave file. Does not store this data locally.
# Simple call to get_frames() to get data in format we like (numpy array, float32)
class WaveFile(object):
    def __init__(self, filepath) :
        super(WaveFile, self).__init__()

        self.wave = wave.open(filepath)
        self.num_channels, self.sampwidth, self.sr, self.end, \
           comptype, compname = self.wave.getparams()

        # for now, we will only accept 16 bit files and the sample rate must match
        assert(self.sampwidth == 2)
        assert(self.sr == Audio.sample_rate)

    # read an arbitrary chunk of data from the file
    def get_frames(self, start_frame, end_frame) :
        # get the raw data from wave file as a byte string. If asking for more than is available, it just
        # returns what it can
        self.wave.setpos(start_frame)
        raw_bytes = self.wave.readframes(end_frame - start_frame)

        # convert raw data to numpy array, assuming int16 arrangement
        samples = np.fromstring(raw_bytes, dtype = np.int16)

        # convert from integer type to floating point, and scale to [-1, 1]
        samples = samples.astype(np.float32)
        samples *= (1 / 32768.0)

        return samples

    def get_num_channels(self):
        return self.num_channels

# We can generalize the thing that WaveFile does - it provides arbitrary wave
# data. We can define a "wave data providing interface" (called WaveSource)
# if it can support the function:
#
# get_frames(self, start_frame, end_frame)
#
# Now create WaveBuffer. Same WaveSource interface, but can take a subset of
# audio data from a wave file and holds all that data in memory.
class WaveBuffer(object):
    def __init__(self, filepath, start_frame, num_frames):
        super(WaveBuffer, self).__init__()

        # get a local copy of the audio data from WaveFile
        wr = WaveFile(filepath)
        self.data = wr.get_frames(start_frame, start_frame + num_frames)
        self.num_channels = wr.get_num_channels()

    # start and end args are in units of frames,
    # so take into account num_channels when accessing sample data
    def get_frames(self, start_frame, end_frame) :
        start_sample = start_frame * self.num_channels
        end_sample = end_frame * self.num_channels
        return self.data[start_sample : end_sample]

    def get_num_channels(self):
        return self.num_channels



# simple class to hold a region: name, start frame, length (in frames)
from collections import namedtuple
AudioRegion = namedtuple('AudioRegion', ['name', 'start', 'len'])


# a collection of regions read from a file
class SongRegions(object):
    def __init__(self, filepath):
        super(SongRegions, self).__init__()

        self.regions = []
        self._read_regions(filepath)

    def __repr__(self):
        out = ''
        for r in self.regions:
            out = out + str(r) + '\n'
        return out

    def _read_regions(self, filepath) :
        lines = open(filepath).readlines()

        for line in lines:
            # each region is: start_time val len name, separated by tabs.
            # we don't care about val
            # time values are in seconds
            (start_sec, x, len_sec, name) = line.strip().split('\t')

            # convert time (in seconds) to frames. Assumes Audio.sample_rate
            start_f = int( float(start_sec) * Audio.sample_rate )
            len_f = int( float(len_sec) * Audio.sample_rate )

            self.regions.append(AudioRegion(name, start_f, len_f))

# Reads from a regions file and a wave file to create a bunch of WaveBuffers,
# one per region.
def make_wave_buffers(regions_path, wave_path):
    sr = SongRegions(regions_path)
    buffers = {}
    for r in sr.regions:
        buffers[r.name] = WaveBuffer(wave_path, r.start, r.len)
    return buffers
