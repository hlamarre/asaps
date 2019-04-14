import pyo
import numpy as np
from numpy.random import choice
import random
import time
s = pyo.Server().boot()


class pitchDetect:
    
    def __init__(self, sound='01-181117_1724.wav'):
        self.sound = sound
        self.table = pyo.SndTable(path=self.sound, stop=5, chnl=0, initchnls=0).normalize()
        self.read = pyo.TableRead(self.table, loop=0).play()

    def analysis(self):
        self.pitchList = []
        self.pitch = pyo.Yin(self.read)
        s.setStartOffset(self.table.getDur())

        self.x = 0
        def pitchFunc():
            self.x +=1
            if self.x <= 5:
                self.pitchList.append(round(self.pitch.get()))

        self.pitchPat = pyo.Pattern(pitchFunc, .1).play()
        return self.pitchList


if __name__ == "__main__":
    
    pitch = pitchDetect()
    pitList = pitch.analysis()
    time.sleep(5)
    print(pitList)
    
    s.gui(locals())