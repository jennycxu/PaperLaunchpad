#####################################################################
#
# gfxutil.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


from kivy.clock import Clock as kivyClock
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Rectangle, Ellipse, Color, Fbo, ClearBuffers, ClearColor, Line
from kivy.graphics import PushMatrix, PopMatrix, Scale, Callback
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.core.window import Window

import numpy as np


# return a Label object configured to look good and be positioned at
# the top-left of the screen
def topleft_label() :
    l = Label(text = "text", valign='top', font_size='20sp',
              pos=(Window.width * 0.5, Window.height * 0.4),
              text_size=(Window.width, Window.height))
    return l

# Override Ellipse class to add centered functionality.
# use cpos and csize to set/get the ellipse based on a centered registration point
# instead of a bottom-left registration point
class CEllipse(Ellipse):
    def __init__(self, **kwargs):
        super(CEllipse, self).__init__(**kwargs)
        if 'cpos' in kwargs:
            self.cpos = kwargs['cpos']

        if 'csize' in kwargs:
            self.csize = kwargs['csize']

    def get_cpos(self):
        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)

    def set_cpos(self, p):
        self.pos = (p[0] - self.size[0]/2 , p[1] - self.size[1]/2)

    def get_csize(self) :
        return self.size

    def set_csize(self, p) :
        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)



# KeyFrame Animation class
# initialize with an argument list where each arg is a keyframe.
# one keyframe = (t, k1, k2, ...), where t is the time of the keyframe and
# k1, k2, ..., kN are the values
class KFAnim(object):
    def __init__(self, *kwargs):
        super(KFAnim, self).__init__()
        frames = list(zip(*kwargs))
        self.time = frames[0]
        self.frames = frames[1:]

    def eval(self, t):
        if len(self.frames) == 1:
            return np.interp(t, self.time, self.frames[0])
        else:
            return [np.interp(t, self.time, y) for y in self.frames]

    # return true if given time is within keyframe range. Otherwise, false.
    def is_active(self, t) :
        return t < self.time[-1]


# AnimGroup is a simple manager of objects that get drawn, updated with
# time, and removed when they are done
class AnimGroup(InstructionGroup) :
    def __init__(self):
        super(AnimGroup, self).__init__()
        self.objects = []

    # add an object. The object must be an InstructionGroup (ie, can be added to canvas) and
    # it must have an on_update(self, dt) method that returns True to keep going or False to end
    def add(self, obj):
        super(AnimGroup, self).add(obj)
        self.objects.append(obj)

    def on_update(self):
        dt = kivyClock.frametime
        kill_list = [o for o in self.objects if o.on_update(dt) == False]

        for o in kill_list:
            self.objects.remove(o)
            self.remove(o)

    def size(self):
        return len(self.objects)


# A graphics object for displaying a point moving in a pre-defined 3D space
# the 3D point must be in the range [0,1] for all 3 coordinates.
# depth is rendered as the size of the circle.
class Cursor3D(InstructionGroup):
    def __init__(self, area_size, area_pos, rgb, size_range = (10, 50), border = True):
        super(Cursor3D, self).__init__()
        self.area_size = area_size
        self.area_pos = area_pos
        self.min_sz = size_range[0]
        self.max_sz = size_range[1]

        if border:
            self.add(Color(1, 0, 0))
            self.add(Line(rectangle= area_pos + area_size))

        self.color = Color(*rgb)
        self.add(self.color)

        self.cursor = CEllipse(segments = 40)
        self.cursor.csize = (30,30)
        self.cursor.cpos = self.area_pos
        self.add(self.cursor)

    # position is a 3D point with all values from 0 to 1
    def set_pos(self, pos):
        radius = self.min_sz + pos[2] * (self.max_sz - self.min_sz)
        self.cursor.csize = (radius*2, radius*2)
        self.cursor.cpos = pos[0:2] * self.area_size + self.area_pos

    def set_color(self, rgb):
        self.color.rgb = rgb

    def get_screen_xy(self) :
        return self.cursor.cpos
