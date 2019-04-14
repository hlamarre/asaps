import pyo
import numpy as np
from numpy.random import choice
import random
import time

s = pyo.Server().boot()


sound = 'feu.wav'
table = pyo.SndTable(path=sound, stop=5, chnl=0, initchnls=0).normalize()
son = pyo.TableRead(table, loop=0).play()


pitchList = []

pitch = pyo.Yin(son)

ti = time.time()

s.setStartOffset(table.getDur())


'''V1'''
x = 0
def pitchFunc():
    global x
    x+=1
    print("pattern")
    if x <= round(table.getDur()):
        pitchList.append(pitch.get())
    else:
        pitchPat.stop()
        #onComplete()

pitchPat = pyo.Pattern(pitchFunc, .1).play()


def onComplete():
    pit = pyo.Choice(pitchList)
    osc = pyo.Sine(pit).out()

print("Start begin")
s.start()
onComplete()

