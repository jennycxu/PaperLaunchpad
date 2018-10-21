#####################################################################
#
# audio.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import sys
sys.path.append('.')
sys.path.append('..')

import pyaudio
import numpy as np
from common import core
import time
import os.path
from configparser import ConfigParser


class Audio(object):
    # global variable: might change when Audio driver is set up.
    sample_rate = 44100

    def __init__(self, num_channels, listen_func = None, input_func = None):
        super(Audio, self).__init__()

        assert(num_channels == 1 or num_channels == 2)
        self.num_channels = num_channels
        self.listen_func = listen_func
        self.input_func = input_func
        self.audio = pyaudio.PyAudio()

        out_dev, in_dev, buffer_size, sr = self._get_parameters()
        Audio.sample_rate = sr

        # create stream
        self.stream = self.audio.open(format = pyaudio.paFloat32,
                                      channels = num_channels,
                                      frames_per_buffer = buffer_size,
                                      rate = Audio.sample_rate,
                                      output = True,
                                      input = input_func != None,
                                      output_device_index = out_dev,
                                      input_device_index = in_dev)

        self.generator = None
        self.cpu_time = 0
        core.register_terminate_func(self.close)

    def close(self) :
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    # set a generator. The generator must support the method
    # generate(num_frames, num_channels), 
    # which returns a numpy array of length (num_frames * num_channels)
    def set_generator(self, gen) :
        self.generator = gen

    # return cpu time calcuating audio time in milliseconds
    def get_cpu_load(self) :
        return 1000 * self.cpu_time

    # must call this every frame.
    def on_update(self):
        t_start = time.time()

        # get input audio if desired
        if self.input_func:
            try:
                num_frames = self.stream.get_read_available() # number of frames to ask for
                if num_frames:
                    data_str = self.stream.read(num_frames, False)
                    data_np = np.fromstring(data_str, dtype=np.float32)
                    self.input_func(data_np, self.num_channels)
            except IOError as e:
                print('got error', e)

        # Ask the generator to generate some audio samples.
        num_frames = self.stream.get_write_available() # number of frames to supply
        if self.generator and num_frames != 0:
            (data, continue_flag) = self.generator.generate(num_frames, self.num_channels)

            # make sure we got the correct number of frames that we requested
            assert len(data) == num_frames * self.num_channels, \
                "asked for (%d * %d) frames but got %d" % (num_frames, self.num_channels, len(data))

            # convert type if needed and write to stream
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            self.stream.write(data.tostring())

            # send data to listerner as well
            if self.listen_func:
                self.listen_func(data, self.num_channels)

            # continue flag
            if not continue_flag:
                self.generator = None

        # how long this all took
        dt = time.time() - t_start
        a = 0.9
        self.cpu_time = a * self.cpu_time + (1-a) * dt


    # return parameter values for output device idx, input device idx, and
    # buffer size
    def _get_parameters(self):
        config = load_audio_config(self.audio)

        out_dev     = config['outputdevice']
        in_dev      = config['inputdevice']
        buf_size    = config['buffersize']
        sample_rate = config['samplerate']

        # for Windows, we want to find the ASIO host API and associated devices
        if out_dev == 'None':
            cnt = self.audio.get_host_api_count()
            for i in range(cnt):
                api = self.audio.get_host_api_info_by_index(i)
                if api['type'] == pyaudio.paASIO:
                    host_api_idx = i
                    out_dev = api['defaultOutputDevice']
                    in_dev = api['defaultInputDevice']
                    print('Found ASIO API', host_api_idx)

        # string 'None' must be converted to type None for pyaudio API to work
        if out_dev == 'None':
           out_dev = None
        if in_dev == 'None':
            in_dev = None

        print('using audio params:')
        print('  samplerate: {}\n  buffersize: {}\n  outputdevice: {}\n  inputdevice: {}'.format(
            sample_rate, buf_size, out_dev, in_dev))
        return out_dev, in_dev, buf_size, sample_rate


# location of config file (in User's home directory)
CONFIG_FILE = os.path.expanduser('~/audio_config.cfg')


# load config file. If not found or missing items, will setup default values
def load_audio_config(py_audio = None):
    devices = get_audio_devices(py_audio)
    out = {}

    config = ConfigParser()
    try:
        config.read((CONFIG_FILE))
        items = config.items('audio')

        for opt in items:
            val = 'None' if opt[1] == 'None' else int(opt[1])
            out[ opt[0] ] = val

    except Exception as e:
        print(e)
        pass

    # fill in default values if not found:
    if 'outputdevice' not in out:
        out['outputdevice'] = 'None'

    if 'inputdevice' not in out:
        out['inputdevice'] = 'None'

    if 'buffersize' not in out:
        out['buffersize'] = 512

    if 'samplerate' not in out:
        out['samplerate'] = 44100

    # make sure input and output devices are valid:
    if out['outputdevice'] != 'None' and out['outputdevice'] >= len(devices['output']):
        out['outputdevice'] = 'None'

    if out['inputdevice'] != 'None' and out['inputdevice'] >= len(devices['input']):
        out['inputdevice'] = 'None'

    return out

# save audio config
def save_audio_config(cfg):
    print('saving config to', CONFIG_FILE)
    config = ConfigParser()
    config.add_section('audio')
    for option in cfg.keys():
        print('  ', option, cfg[option])
        config.set('audio', option, str(cfg[option]))
    config.write(open(CONFIG_FILE, 'w'))


gDevices = None
def get_audio_devices(py_audio = None):
    '''Returns the available input and output devices as { 'input': <list>, 'output': <list> }
<list> is a list of device descriptors, each being a dictionary:
    {'index': <integer>, 'name': <string>, 'latency': (low, high), 'channels': <max # of channels>
'''
    global gDevices
    if gDevices:
        return gDevices

    def add_device(arr, io_type, dev) :
        info = {}
        info['index'] = dev['index']
        info['name'] = dev['name']
        info['latency'] = (dev['defaultLow' + io_type + 'Latency'], 
                           dev['defaultHigh' + io_type + 'Latency'])
        info['channels'] = dev['max' + io_type + 'Channels']
        arr.append(info)

    audio = py_audio if py_audio else pyaudio.PyAudio()

    out_devs = [{'index':'None', 'name':'Default', 'channels':0, 'latency':(0,0)}]
    in_devs  = [{'index':'None', 'name':'Default', 'channels':0, 'latency':(0,0)}]

    cnt = audio.get_device_count()
    for i in range(cnt):
        dev = audio.get_device_info_by_index(i)

        if dev['maxOutputChannels'] > 0:
            add_device(out_devs, 'Output', dev)

        if dev['maxInputChannels'] > 0:
            add_device(in_devs, 'Input', dev)

    if not py_audio:
        audio.terminate()
    gDevices = {'output': out_devs, 'input': in_devs}
    return gDevices


def print_audio_devices():
    devs = get_audio_devices()

    print("\nOutput Devices")
    print('{:>5}: {:<40} {:<6} {}'.format('idx', 'name', 'chans', 'latency'))
    for d in devs['output']:
        print('{index:>5}: {name:<40} {channels:<6} {latency[0]:.3f} - {latency[1]:.3f}'.format(**d))

    print("\nInput Devices")
    print('{:>5}: {:<40} {:<6} {}'.format('idx', 'name', 'chans', 'latency'))
    for d in devs['input']:
        print('{index:>5}: {name:<40} {channels:<6} {latency[0]:.3f} - {latency[1]:.3f}'.format(**d))


if __name__ == "__main__":
    print_audio_devices()
