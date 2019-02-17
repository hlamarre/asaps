import pyo
import numpy as np
from numpy.random import choice
import random
import time
s = pyo.Server().boot()
bs = s.getBufferSize()

son = 'C:/Users/Hubert Lamarre/Desktop/sintra_arbres.wav'

class Sound:
    def __init__(self, sound=son, start=0, stop=None, res=50):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.res = res

    def getSound(self):
        #self.son = self.sound
        return self.sound

    def getRes(self):    
        #self.res = self.res
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=self.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

    def getDur(self):
        self.dur = int(self.getTable().getDur())
        return self.dur
        
    def play(self):
        self.tableR = pyo.TableRead(self.getTable(), 1/self.getDur(), 1).play()
        return self.tableR
    
    def out(self):
        self.son = self.play()
        return self.son.out()

anlys = Sound()

tabOG = pyo.DataTable(size=anlys.getDur()*anlys.getRes())
datarOG = np.asarray(tabOG.getBuffer())

'''algos'''
class AsIs:
    def __init__(self, start=0, stop=None, res=50):
        self.start = start
        self.stop = stop
        self.res = res

    def getRes(self):    
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=anlys.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

    def getDur(self):
        self.dur = int(self.getTable().getDur())
        return self.dur

    def getEnv(self):    
        self.env = self.getTable().getEnvelope(self.getDur()*self.getRes())
        return self.env

    def play(self):
        self.env = self.getEnv()
        def call():
            datarOG[:] = np.asarray(self.env)
        self.pat = pyo.Pattern(call, 1/self.getRes()).play()
        self.mul = pyo.TableRead(tabOG, 1/self.getDur(), 1, 3).play()
        return pyo.SigTo(self.mul, 1/self.getRes())

class FreeAmp:
    #.getamp() for random amplitude
    def __init__(self, start=0, stop=None, res=50):
        self.start = start
        self.stop = stop
        self.res = res

    def getRes(self):    
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=anlys.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
    
    def getSize(self):
        self.size = self.getEnvAr().size
        return self.size

    def getMean(self):
        self.mean = np.float(np.mean(self.getEnvAr()))
        return self.mean

    def getMed(self):    
        self.med = np.float(np.median(self.getEnvAr()))
        return self.med

    def getStd(self):
        self.std = np.float(np.std(self.getEnvAr()))
        return self.std
        
    def play(self):
        self.amp_min = self.getMed() - self.getStd()
        self.amp_max = self.getMed() + self.getStd()
        self.mul = pyo.Randi(self.amp_min, self.amp_max, self.res)
        return pyo.SigTo(self.mul, 1/anlys.getRes())

class FreeDev:
    def __init__(self, start=0, stop=None, res=50):
        self.start = start
        self.stop = stop
        self.res = res

    def getRes(self):    
        return self.res

    def getTable(self):
        self.sound = anlys.getSound()
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
    
    def getSize(self):
        self.size = self.getEnvAr().size
        return self.size

    def getMean(self):
        self.mean = np.float(np.mean(self.getEnvAr()))
        return self.mean

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
        return pyo.SigTo(self.mul, 1/self.getRes())
    
class Histori:
    def __init__(self, start=0, stop=None, res=50, nbin=50):
        self.start = start
        self.stop = stop
        self.res = res
        self.nbin = pyo.Sig(nbin)
        
    def getRes(self):    
        return self.res

    def getTable(self):
        self.sound = anlys.getSound()
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
            datar[:] = np.asarray(randHist)
        self.pat = pyo.Pattern(call, 1/self.getRes()).play()
        self.mul = pyo.TableRead(tab, 1/self.getDur(), 1, 3).play()
        return pyo.SigTo(self.mul, 1/self.getRes())

    def changeNbins(self, nBins):
        self.nbin.value = nBins
        
class Sections:
    def __init__(self, start=0, stop=None, res=50, thresh=.03, length=100000):
        self.start = start
        self.stop = stop
        self.res = res
        self.thresh = thresh
        self.length = length

    def getRes(self):    
        return self.res

    def getTable(self):
        self.sound = anlys.getSound()
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
    
    def getSize(self):
        self.size = self.getEnvAr().size
        return self.size

    def getMean(self):
        self.mean = np.float(np.mean(self.getEnvAr()))
        return self.mean

    def getMed(self):    
        self.med = np.float(np.median(self.getEnvAr()))
        return self.med

    def getStd(self):
        self.std = np.float(np.std(self.getEnvAr()))
        return self.std
    
      
    def getSections(self):
        self.envar = self.getEnvAr()
        self.sectList = []
        '''division en sections'''
        for i in range(self.envar.size):
            if self.envar[i] - self.envar[i-1] > self.thresh :
                self.sectList.append(i)
        self.sectAr = np.split(self.envar, self.sectList)
        '''suppression des sections > self.length'''
        for i in reversed(range(len(self.sectAr))):
            if self.sectAr[i].size > self.length:
                del self.sectAr[i]
        return self.sectAr

    def play(self):
        def call():
            '''copie de l'array sur sois meme'''
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
            datar[:] = np.asarray(self.sect)
        self.pat = pyo.Pattern(call, self.getDur()).play()
        self.mul = pyo.TableRead(tab, 1/self.getDur(), 1, 3).play()
        return pyo.SigTo(self.mul, 1/self.getRes())

class Markov:
    def __init__(self, start=0, stop=10, res=50, order=1):
        self.start = start
        self.stop = stop
        self.res = res
        self.order = order

    def getRes(self):    
        return self.res

    def getTable(self):
        self.sound = anlys.getSound()
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
        datar[:] = np.asarray(self.markEnv)
        self.mul = pyo.TableRead(tab, 1/self.getDur(), 1, 3).play()
        return pyo.SigTo(self.mul, 1/self.getRes())

       
'''else'''
class MovAv:
    def __init__(self, start=0, stop=None, res=50, period=10):
        self.start = start
        self.stop = stop
        self.res = res
        self.per = period

    def getRes(self):    
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=anlys.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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
        self.avList = []
        self.envarMo = self.getEnvAr()
        for i in range(self.envarMo.size):
            self.avList.append(self.envarMo[ i - self.per : i ].mean())
        datar[:] = np.asarray(self.avList)
        self.mul = pyo.TableRead(tab, 1/self.getDur(), 1, 3).play()
        return pyo.SigTo(self.mul, 1/self.getRes())

class Gate:
    def __init__(self, start=0, stop=None, res=50, gate=.03):
        self.start = start
        self.stop = stop
        self.res = res
        self.gate = gate

    def getRes(self):    
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=anlys.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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

    def getGate(self):#gate = self.mean???
        self.envArGt = self.getEnvAr()
        self.gateAr = np.zeros(self.envArGt.shape)
        for i in range(self.envArGt.size):
            if self.envArGt[i] > self.gate :
                self.gateAr[i] = 1
        return self.gateAr

class Change:
    def __init__(self, start=0, stop=None, res=50, gate=.03):
        self.start = start
        self.stop = stop
        self.res = res
        self.gate = gate

    def getRes(self):    
        return self.res

    def getTable(self):
        self.table = pyo.SndTable(path=anlys.getSound(), chnl=0, start=self.start, stop=self.stop, initchnls=0)
        return self.table

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

    def getChange(self): # A travailler (ref. une moyenne?)
        self.envArCh = self.getEnvAr()
        self.changeAr = np.zeros(self.envArCh.shape)
        for i in range(self.envArCh.size):
            if self.envArCh[i] - self.envArCh[i-1] > self.envArCh[i-1] :
                self.changeAr[i] = 1
        return self.changeAr

  
asis = AsIs()
algo = Histori()
algo.changeNbins(20)
tab = pyo.DataTable(size=algo.getDur()*algo.getRes())
datar = np.asarray(tab.getBuffer())


x = 1
mul = algo.play()*x + asis.play()*(1-x)

osc = pyo.Sine(400, mul=mul).out()

s.gui(locals())