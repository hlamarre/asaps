import pyo
import numpy as np
from numpy.random import choice
import random
s = pyo.Server().boot()


'''input'''
class SndReader:

    def __init__(self, sound='feu.wav', start=0, stop=None):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        self.dur = self.table.getDur()
        self.refreshRate = 3600
        self.OGTable = pyo.SndTable(path=self.sound, chnl=0, initchnls=0)
        self.OGDur = self.OGTable.getDur()

    def refresh(self):
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0)
        self.dur = self.table.getDur()
        self.OGTable = pyo.SndTable(path=self.sound, chnl=0, initchnls=0)
        self.OGDur = self.OGTable.getDur()

    def setSound(self, sound):
        self.sound = sound
        self.refresh()
        
    def setDur(self, start=0, stop=None):
        self.start = start
        self.stop = stop
        self.refresh()

class LiveIn:

    def __init__(self, dur=1, refreshRate=1):  
        self.dur = dur  
        self.refreshRate = refreshRate  
        self.table = pyo.SndTable()
        self.input = pyo.Input() 
        self.tabFill = pyo.TableFill(self.input, self.table)

    def refresh(self):   
        self.table = pyo.SndTable()
        self.input = pyo.Input() 
        self.tabFill = pyo.TableFill(self.input, self.table)

    def setSound(self, sound):
        pass

    def setDur(self, start=1, stop=1):
        self.dur = start
        self.refRate = stop
        self.refresh()


'''parent'''
class Amplitude:
    #parent

    def __init__(self, res=50, lag=.01, lag2=.03):
        self.res = res
        self.lag = lag
        self.lag2 = lag2

        self.dur = snd.dur
        self.refreshRate = snd.refreshRate
        self.len = int(self.dur*self.res)
        self.tab = pyo.DataTable(self.len)
        self.datar = np.asarray(self.tab.getBuffer())

        self.table = snd.table
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 2))

        self.sig = None


    def refresh(self):
        self.dur = snd.dur
        self.refreshRate = snd.refreshRate
        self.len = int(self.dur*self.res)
        self.tab = pyo.DataTable(self.len)
        self.datar = np.asarray(self.tab.getBuffer())

        self.table = snd.table
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 2))

    def refreshTable(self):
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 2))


    def play(self):
        def call():
            self.refreshTable()     
            self.datar[:] = self.envAr
        self.pat = call()
        self.pat = pyo.Pattern(call, self.refreshRate).play()
        self.mul = pyo.TableRead(self.tab, 1/self.dur, 1, 3).play()
        return self.mul

    def amp(self):
        self.sig = pyo.SigTo(self.play(), self.lag)
        return self.sig

    def amp2(self):
        self.sig2 = pyo.SigTo(self.play(), self.lag2)
        return self.sig2       

    def setSound(self, sound):
        snd.setSound(sound)
        self.refresh()
        self.play()

    def setStartStop(self, start=0, stop=None):
        # when in live mode start is buffer time and stop is freq of analysis
        snd.setDur(start=start, stop=stop)
        self.refresh()
        self.play()

    def setRes(self, res):
        self.res = res
        self.refresh()
        self.play()

    def setLag(self, lag):
        self.lag = lag
        self.refresh()
        self.play()

    def seLag2(self, lag):
        self.lag2 = lag
        self.refresh()
        self.play()
        
    def out(self):
        self.son = pyo.TableRead(self.table, 1/self.dur, 1).play()
        return self.son.out()
    
'''amp'''
class AsAmp(Amplitude):
    # original amplitude
    pass

class AvgAmp(Amplitude):
    # moving average
    def __init__(self, res=50, lag=.01, lag2=.03, period=10):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.period = period

    def play(self):
        def call():
            self.avList = []
            self.refreshTable()     
            self.envarMo = self.envAr
            for i in range(self.envarMo.size):
                x = i+self.period
                self.avList.append(self.envarMo[ x - self.period : x ].mean())
            self.datar[:] = np.asarray(self.avList)
            print(self.tab.get(1))
        self.pat = pyo.Pattern(call, self.refreshRate).play()
        self.mul = pyo.TableRead(self.tab, 1/self.dur, 1, 3).play()
        return self.mul

    def setPeriod(self, period):
        self.period = period
        self.play()

class DevAmp(Amplitude):
    # random difference between sample
    def __init__(self, res=50, lag=.01, lag2=.03):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.mul = 0

    def play(self):
        self.devList = []
        def deviation():
            self.devList.clear()
            self.refreshTable()
            for i in range(self.envAr.size):
                x = self.envAr[i] - self.envAr[i-1]
                self.devList.append(x)
        self.pat = deviation()
        self.pat = pyo.Pattern(deviation, self.refreshRate).play()  

        self.mul += pyo.Choice(self.devList, self.res)
        return self.mul

class HistAmp(Amplitude):
    # random on histogram
    def __init__(self, res=50, lag=.01, lag2=.03, nbin=50):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.nbin = nbin


    def getHist(self): 
        self.hist, self.bin = np.histogram(self.envAr, density=True, bins = self.nbin)
        self.hist = np.round(self.hist,8)
        self.hist = self.hist/self.hist.sum()
        self.bins = self.bin[0:self.nbin]       
        return self.hist, self.bins

    def play(self):
        def hist():
            self.refreshTable()
            self.hist, self.bin = np.histogram(self.envAr, density=True, bins = self.nbin)
            self.hist = np.round(self.hist,8)
            self.hist = self.hist/self.hist.sum()
            self.bins = self.bin[0:self.nbin]
        self.patHist = hist()
        self.patHist = pyo.Pattern(hist, self.refreshRate).play()

        def call():
            randHist = np.float(np.random.choice(self.bins, p=self.hist))
            self.datar[:] = randHist
        self.pat = pyo.Pattern(call, 1/self.res).play()
        self.mul = pyo.TableRead(self.tab, 1/self.dur, 1, 3).play()
        return self.mul
        
    def setDensity(self, nBins=50):
        self.nbin = nBins
        self.refresh()
        self.play()

class SectAmp(Amplitude):
    # scramble of sections
    def __init__(self, res=50, lag=.01, lag2=.03, thresh=.03, length=3000):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.thresh = thresh
        self.length = length
      
    def getSections(self):

        def sect():
            self.refreshTable()
            self.sectList = []
            self.difAr = np.zeros(self.envAr.shape)
            '''division en sections'''
            for i in range(self.envAr.size):
                x = self.envAr[i] - self.envAr[i-1]
                self.difAr[i] = x
                if x > self.thresh :
                    self.sectList.append(i)
            self.sectMean = np.float(np.mean(self.difAr))
            self.sectAr = np.split(self.envAr, self.sectList)         
            '''suppression des sections > self.length pour plus de densite'''
            if self.length > self.sectMean:
                for i in reversed(range(len(self.sectAr))):
                    if self.sectAr[i].size > self.length:
                        del self.sectAr[i]
            else:
                for i in reversed(range(len(self.sectAr))):
                    if self.sectAr[i].size < self.length:
                        del self.sectAr[i]

        self.patSect = sect()
        self.patSect = pyo.Pattern(sect, self.dur).play()
        return self.sectAr

    def play(self):
        self.sectOG = self.sect = self.getSections()
        self.sectDum = np.concatenate(self.sect)
        time = np.size(self.sectDum)/self.dur

        def call():
            self.refreshTable()
            self.sect = self.getSections()
            self.sect = np.random.permutation(self.sect)
            self.sect = np.concatenate(self.sect)
            self.sect = np.resize(self.sect, self.datar.shape)
            self.datar[:] = np.asarray(self.sect)
            self.sect = self.sectOG

        self.pat = pyo.Pattern(call, self.refreshRate).play()
        self.mul = pyo.TableRead(self.tab, 1/self.dur, 1, 3).play()
        return self.mul 

    def setThresh(self, thresh):
        self.thresh = thresh
        self.play()   

    def setLength(self, length):
        self.length = length
        self.play()   

class MarkAmp(Amplitude):
    # markov chain
    def __init__(self, res=50, lag=.01, lag2=.03, order=1):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.order = order

    def play(self):
        def call():
            self.refreshTable()
            self.envList = self.envAr.tolist()
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

        self.pat = call()
        self.pat = pyo.Pattern(call, self.refreshRate).play()
        self.mul = pyo.TableRead(self.tab, 1/self.dur, 1, 3).play()
        return self.mul

    def setOrder(self, order):
            self.order = order
            self.play()


'''other'''
class GateAmp(Amplitude):
    # output 1 everytime signal cross threshold
    def __init__(self, res=50, lag=.01, lag2=.03, thresh=.03):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.thresh = thresh

    def getGate(self):#thresh = self.mean???
        self.envArGt = self.envAr
        self.gateAr = np.zeros(self.envArGt.shape)
        for i in range(self.envArGt.size):
            if self.envArGt[i] > self.thresh :
                self.gateAr[i] = 1
        return self.gateAr

    def setThresh(self, thresh):
        self.thresh = thresh
        self.getGate()

class Change(Amplitude):
    # detect deviation > i-1, calculate time (in sample) between each of them and make random version of the change array
    def __init__(self, res=50, lag=.01, lag2=.03, gate=.03):
        super().__init__(res=50, lag=.01, lag2=.03)
        self.gate = gate

    def getChange(self): 
        self.envArCh = self.envAr
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
        self.randGateAr = np.zeros(self.getChange().size)
        self.periodChoice = self.getPeriod()
        for i in range(self.periodChoice.size):
            i = np.random.choice(self.periodChoice)
            self.randGateAr[i] = 1
        return self.randGateAr

    def setGate(self, gate):
        self.gate = gate
        self.getChange()


snd = SndReader()


if __name__ == "__main__":

    algo = AsAmp()

    osc = pyo.Sine(400, mul=algo.amp()).out()

    s.gui(locals())