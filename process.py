import pyo
import numpy as np
from numpy.random import choice
import random
s = pyo.Server().boot()


'''parent'''
class Amplitude:
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
    
    def getTable(self):
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table
    
    def getRes(self):    
            return self.res

    def getDur(self):
        self.dur = int(self.getTable().getDur())
        return self.dur

    def getEnv(self):    
        self.env = self.getTable().getEnvelope(self.getDur()*self.getRes())
        return self.env

    def getEnvAr(self):
        self.envAr = np.absolute(np.asarray(self.getEnv()))
        self.envAr = self.envAr / np.max(self.envAr)
        self.envAr = np.concatenate(np.round(self.envAr, 2))
        return self.envAr

    def play(self):
        self.env = self.getEnv()
        def call():
            self.datar[:] = np.asarray(self.env)
        self.pat = pyo.Pattern(call, 1/self.getRes()).play()
        self.mul = pyo.TableRead(self.tab, 1/self.getDur(), 1, 3).play()
        return self.mul

    def amp(self):
        self.lg = self.lag
        self.amp = pyo.SigTo(self.play(), self.lg)
        return self.amp

    def setSound(self, sound):
        self.sound = sound
        self.play()

    def setStartStop(self, start=0, stop=None):
        self.start = start
        self.stop = stop
        self.getTable()

    def setRes(self, res=50):
        self.res = res
        self.__init__()

    def setLag(self, lag):
        self.lag = lag
        self.play()
    
'''amp'''
class AsAmp(Amplitude):
    # original amplitude
    def out(self):
        self.son = pyo.TableRead(self.getTable(), 1/self.getDur(), 1).play()
        return self.son.out()

class AvgAmp(Amplitude):
    # moving average
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01, period=10):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.period = period

    def play(self):
        self.avList = []
        self.envarMo = self.getEnvAr()
        for i in range(self.envarMo.size):
            x = i+self.period
            self.avList.append(self.envarMo[ x - self.period : x ].mean())
        self.datar[:] = np.asarray(self.avList)
        self.mul = pyo.TableRead(self.tab, 1/self.getDur(), 1, 3).play()
        return self.mul

    def setPeriod(self, period):
        self.period = period
        self.play()

class DevAmp(Amplitude):
    # random difference between sample
    def getDev(self):
        self.dev = []
        for i in range(self.getEnvAr().size):
            x = self.envAr[i] - self.envAr[i-1]
            self.dev.append(x)
        return self.dev    

    def play(self):
        self.mul = 0
        self.dev = pyo.Choice(self.getDev(), self.getRes())  
        self.mul += self.dev
        return self.mul

class HistAmp(Amplitude):
    # random on histogram
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01, nbin=50):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.nbin = nbin

    def getHist(self): 
        self.hist, self.bin = np.histogram(self.getEnvAr(), density=True, bins = self.nbin)
        self.hist = np.round(self.hist,8)
        self.hist = self.hist/self.hist.sum()
        self.bins = self.bin[0:self.nbin]       
        return self.hist, self.bins

    def play(self):
        self.histp, self.binsp = self.getHist()
        self.a = 1
        def call():
            randHist = np.float(np.random.choice(self.binsp, p=self.histp))
            self.datar[:] = np.asarray(randHist)
        self.pat = pyo.Pattern(call, 1/self.getRes()).play()
        self.mul = pyo.TableRead(self.tab, 1/self.getDur(), 1, 3).play()
        return self.mul
        
    def setNbins(self, nBins=50):
        self.nbin = nBins
        self.play()

class SectAmp(Amplitude):
    # scramble of sections
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01, thresh=.03, length=100000):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.thresh = thresh
        self.length = length
      
    def getSections(self):
        self.envar = self.getEnvAr()
        self.sectList = []
        '''division en sections'''
        for i in range(self.envar.size):
            if self.envar[i] - self.envar[i-1] > self.thresh :
                self.sectList.append(i)
        self.sectAr = np.split(self.envar, self.sectList)
        '''suppression des sections > self.length pour plus de densite'''
        for i in reversed(range(len(self.sectAr))):
            if self.sectAr[i].size > self.length:
                del self.sectAr[i]
        return self.sectAr

    def play(self):
        def call():
            '''copie de l'array sur sois meme pour atteindre meme taille que la table'''
            self.durP = (self.getDur() * self.getRes())
            self.sect = self.getSections()
            while True:
                self.sect = np.hstack([self.sect,self.sect])
                if self.sect.size > self.durP:
                    break
            '''permutation'''
            self.sect = np.random.permutation(self.sect)
            self.sect = np.concatenate(self.sect)
            self.sect = self.sect[:self.durP]           
            self.datar[:] = np.asarray(self.sect)
        self.pat = pyo.Pattern(call, self.getDur()).play()
        self.mul = pyo.TableRead(self.tab, 1/self.getDur(), 1, 3).play()
        return self.mul 

    def setThresh(self, thresh):
        self.thresh = thresh
        self.play()   

    def setLength(self, length):
        self.length = length
        self.getSections()   

class MarkAmp(Amplitude):
    # markov chain
    def __init__(self, sound='feu.wav', start=0, stop=10, res=50, lag=.01, order=1):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.order = order

    def getSize(self):
        self.size = self.getEnvAr().size
        return self.size

    def play(self):
        self.envList = self.getEnvAr().tolist()
        self.envLen = len(self.envList)
        self.tempEnv = []
        self.playedEnv = []

        for val in self.envList:
            self.tempEnv.append( val )
        for i in range(self.order):
            self.tempEnv.append(self.envList[i])
        self.playedEnv = self.envList[self.envLen - self.order:] 

        self.newVal = 0
        self.condition = False
        self.probTable = []
        self.markEnv = []

        for val in range(self.envLen):        
            for i in range(len(self.tempEnv) - self.order):           
                for iord in range(self.order):            
                    if self.playedEnv[len(self.playedEnv) - (iord + 1)] != self.tempEnv[(self.order - 1) + i - iord]:
                        self.condition = False
                        break
                    else:
                        self.condition = True
                if self.condition:
                    self.probTable.append(self.tempEnv[i + self.order])

            self.newVal = self.probTable[random.randint(0, (len(self.probTable) - 1))]    
            self.markEnv.append( self.newVal )
            self.playedEnv.append( self.newVal )

        self.markEnv = np.asarray(self.markEnv)
        self.datar[:] = np.asarray(self.markEnv)
        self.mul = pyo.TableRead(self.tab, 1/self.getDur(), 1, 3).play()
        return self.mul

    def setOrder(self, order):
            self.order = order
            self.play()

'''other'''
class GateAmp(Amplitude):
    # output 1 everytime signal cross threshold
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01, thresh=.03):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.thresh = thresh

    def getEnvAr(self):
        self.envAr = np.absolute(np.asarray(self.getEnv()))
        self.envAr = self.envAr / np.max(self.envAr)
        self.envAr = np.concatenate(np.round(self.envAr, 2))
        return self.envAr

    def getGate(self):#thresh = self.mean???
        self.envArGt = self.getEnvAr()
        self.gateAr = np.zeros(self.envArGt.shape)
        for i in range(self.envArGt.size):
            if self.envArGt[i] > self.thresh :
                self.gateAr[i] = 1
        return self.gateAr

    def setThresh(self, gate):
        self.thresh = thresh
        self.getGate()

class Change(Amplitude):
    # detect deviation > i-1 and calculate time (in sample) between each of them
    def __init__(self, sound='feu.wav', start=0, stop=None, res=50, lag=.01, gate=.03):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res
        self.tab = pyo.DataTable(size=self.getDur()*self.getRes())
        self.datar = np.asarray(self.tab.getBuffer())
        self.lag = lag
        self.gate = gate

    def getEnvAr(self):
        self.envAr = np.absolute(np.asarray(self.getEnv()))
        self.envAr = self.envAr / np.max(self.envAr)
        self.envAr = np.concatenate(np.round(self.envAr, 2))
        return self.envAr

    def getChange(self): 
        self.envArCh = self.getEnvAr()
        self.changeAr = np.zeros(self.envArCh.shape)
        for i in range(self.envArCh.size):
            if self.envArCh[i] - self.envArCh[i-1] > self.envArCh[i-1] :
                self.changeAr[i] = 1
        return self.changeAr

    def getPeriod(self):
        self.envArChR = self.getChange()
        self.lenlis = []
        for i in range(self.envArChR.size):
            if self.envArChR[i] == 1 :
                self.lenlis.append(i)
        for i in range(len(self.lenlis)-1):
            x = self.lenlis[i+1] - self.lenlis[i]
            self.lenlis[i] = x
        return np.asarray(self.lenlis)
        
    def randGate(self):
        self.randGateAr = np.zeros(self.getPeriod().size)
        for i in range(self.envArChR.size):
            i = np.random.choice(self.getPeriod())
            self.randGateAr[i] = 1
        return self.randGateAr

    def setGate(self, gate):
        self.gate = gate
        self.getChange()


if __name__ == "__main__":

    algo = AvgAmp()

    osc = pyo.Sine(400, mul=algo.amp()).out()

    s.gui(locals())