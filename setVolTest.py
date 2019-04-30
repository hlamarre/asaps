import pyo
import numpy as np
from numpy.random import choice
import random

s = pyo.Server().boot()


table = pyo.SndTable('feu.wav')
dur = table.getDur()
read = pyo.TableRead(table, 1/dur, 1).out()


def out(mul=1):
    vol = mul
    read.setMul(vol)
    return read

#pat = pyo.Pattern(out, .5, 0).play()










s.gui(locals())