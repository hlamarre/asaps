import pyo
import numpy as np
from numpy.random import choice
import random

from scipy.signal import blackmanharris, fftconvolve, resample
from scipy.fftpack import rfft, irfft, fftfreq
from matplotlib.mlab import find 

s = pyo.Server().boot()


'''input'''

class SndReader:

    def __init__(self, sound='01-181117_1724.wav', start=0, stop=None):
        self.sound = sound
        self.start = start
        self.stop = stop
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0).normalize()
        self.dur = self.table.getDur()
        self.tableOG = pyo.SndTable(path=self.sound, chnl=0, start=0, stop=None, initchnls=0).normalize()
        self.durOG = self.tableOG.getDur()
        self.refreshRate = 3600
        self.OGTable = pyo.SndTable(path=self.sound, chnl=0, initchnls=0).normalize()
        self.OGDur = self.OGTable.getDur()

    def refresh(self):
        self.table = pyo.SndTable(path=self.sound, chnl=0, start=self.start, stop=self.stop, initchnls=0).normalize()
        self.dur = self.table.getDur()
        self.tableOG = pyo.SndTable(path=self.sound, chnl=0, start=0, stop=None, initchnls=0).normalize()
        self.durOG = self.tableOG.getDur()
        self.OGTable = pyo.SndTable(path=self.sound, chnl=0, initchnls=0).normalize()
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
        self.tableOG = pyo.SndTable()
        self.durOG = 1
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

        self.snd = SndReader()

        self.res = res
        self.lag = lag
        self.lag2 = lag2

        self.dur = self.snd.dur
        self.refreshRate = self.snd.refreshRate
        self.len = int(self.dur*self.res)
        self.tab = pyo.DataTable(self.len)
        self.datar = np.asarray(self.tab.getBuffer())

        self.table = self.snd.table
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 3))

        self.tableOG = self.snd.tableOG
        self.durOG = self.snd.durOG 
        self.sig = None


    def refresh(self):
        self.snd.refresh()
        self.dur = self.snd.dur
        self.refreshRate = self.snd.refreshRate
        self.len = int(self.dur*self.res)
        self.tab = pyo.DataTable(self.len)
        self.datar = np.asarray(self.tab.getBuffer())

        self.table = self.snd.table
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 3))

        self.tableOG = self.snd.tableOG
        self.durOG = self.snd.durOG 

    def refreshTable(self):
        self.env = self.table.getEnvelope(self.len)
        self.envAr = np.concatenate(np.round(np.absolute(np.asarray(self.env)), 3))

    def getEnvAr(self):
        self.refreshTable()
        return self.envAr

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

    def setMode(self, mode):
        self.snd = mode
        self.snd.refresh()
        self.refresh()
        self.play()   

    def setSound(self, sound):
        self.snd.setSound(sound)
        self.refresh()
        self.play()

    def setStartStop(self, start=0, stop=None):
        # when in live mode start is buffer time and stop is freq of analysis
        self.snd.setDur(start=start, stop=stop)
        self.refresh()
        #self.play()

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
        
    def out(self, mul=1):
        self.son = pyo.TableRead(self.table, 1/self.dur, 1, mul=mul).play()
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
        self.snd.setDur(stop=1)

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
        return self.gateAr.tolist()

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
        return self.randGateAr.tolist()

    def setGate(self, gate):
        self.gate = gate
        self.getChange()

class ZeroCross(Amplitude):
    #https://gist.github.com/endolith/255291
    #zero crossing

    def cross(self):
        self.data = self.envAr
        self.pos = self.data > 0
        self.npos = ~self.pos
        self.crossing = ((self.pos[:-1] & self.npos[1:]) | (self.npos[:-1] & self.pos[1:])).nonzero()[0]
        return self.crossing

    def getPitch(self):
        self.notes = []
        self.cro = self.cross()
        self.res = self.res
        for p in range(self.cro.size):
            c = self.cro[p]-self.cro[p-1]
            n = self.res/c
            self.notes.append(n)
        return self.notes


'''pitch

class AutoCorePit(Amplitude):
    #https://gist.github.com/endolith/255291
    #auto corellation pitch detection
    def __init__(self, ctrl, res=44100, lag=.01, lag2=.03):
        super().__init__(res=44100, lag=.01, lag2=.03)
        self.ctrl = ctrl

    def getPitch(self):
        self.res = self.snd.table.getRate()
        self.windowLen = 1024
        self.window = np.blackman(self.windowLen)
        self.step = 0
        self.freqs = [0 for i in range(int(self.envAr.size/self.windowLen))]
        def play():
            self.freqs.clear()
            self.refreshTable()
            for i in range(int(self.envAr.size/self.windowLen)):
                if self.envAr.sum() == 0.0 :
                    break
                a  = self.envAr[self.step:self.step+self.windowLen]
                self.corr = fftconvolve(a, a[::-1], mode='full')
                self.corr = self.corr[len(self.corr)//2:]
                self.step += self.windowLen
                # Find the first low point
                self.d = np.diff(self.corr)
                self.first = find(abs(self.d) > 0)[0]

                # Find the next peak after the low point (other than 0 lag).  This bit is
                # not reliable for long signals, due to the desired peak occurring between
                # samples, and other peaks appearing higher.
                # Should use a weighting function to de-emphasize the peaks at longer lags.
                self.peak = np.argmax(self.corr[self.first:]) + self.first

                f = self.corr
                x = self.peak
                self.px = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
                self.py = f[x] - 1/4. * (f[x-1] - f[x+1]) * (self.px - x)

                self.freqs.append(44100/self.px)

        self.pat = play()
        self.pat = pyo.Pattern(play, self.refreshRate).play()  
        #self.freqs =         

        self.attack = pyo.AttackDetector(self.ctrl, .01, 20, minthresh=-20)
        self.freq = pyo.Sig(400)

        def note():
            self.freq.value = int(random.choice(self.freqs))

        self.trig = note()
        self.trig = pyo.TrigFunc(self.attack, note)
        return self.freq

class FftPit(Amplitude):
    #https://gist.github.com/endolith/255291
    #fft pitch detection
    def __init__(self, ctrl, res=44100, lag=.01, lag2=.03):
        super().__init__(res=44100, lag=.01, lag2=.03)
        self.ctrl = ctrl

    def getPitch(self):
        self.freqs = []
        def play():
            self.refreshTable()
            self.freqs.clear()
            self.ff = np.fft.rfft(self.envAr)
            #self.freq = np.fft.fftfreq(self.ff.size, 1)

            # filter
            self.time   = np.linspace(0,10,2000)
            self.W = np.fft.fftfreq(self.envAr.size, d=self.time[1]-self.time[0])
            self.f_signal = rfft(self.envAr)

            self.cut_f_signal = self.f_signal.copy()
            self.cut_f_signal[(self.W<10)] = 0
            self.cut_signal = irfft(self.cut_f_signal)
            
            self.rfreq = abs(self.cut_signal*44100)

            self.windowLen = 1024
            self.window = np.blackman(self.windowLen)
            self.x = 0
            for i in range(int(self.ff.size/self.windowLen)):
                self.idx = np.argmax((self.ff[self.x:self.x+self.windowLen])*self.window)
                self.x += self.windowLen
                self.f = self.rfreq[self.idx]
                #if f < 4000:
                    #f = f/2
                self.freqs.append(self.f)

        self.pat = play()
        self.pat = pyo.Pattern(play, self.refreshRate).play()    

        self.attack = pyo.AttackDetector(self.ctrl, .01, 20, minthresh=-20)
        self.freq = pyo.Sig(400)

        def note():
            self.freq.value = int(random.choice(self.freqs))

        self.trig = note()
        self.trig = pyo.TrigFunc(self.attack, note)
        return self.freq

class HpsPit(Amplitude):
    #https://gist.github.com/fasiha/957035272009eb1c9eb370936a6af2eb
    #HPS
    def __init__(self, ctrl, res=44100, lag=.01, lag2=.03):
        super().__init__(res=44100, lag=.01, lag2=.03)
        self.ctrl = ctrl
        

    def getPitch(self):
        self.freqs = []
        self.window_length=4096
        self.hop_length=1024
        self.window=np.blackman(self.window_length)
        self.partials=5
        def play():
            self.refreshTable()
            self.freqs.clear()

            self.frequencies = np.fft.rfftfreq(self.window_length, 1 / 44100)
            #self.window = self.window(self.window_length)
            self.pad = lambda a: np.pad(a, (0, self.window_length - len(a)), mode='constant', constant_values=0)
            
            # filter
            self.time = np.linspace(0,10,2000)
            self.W = np.fft.fftfreq(self.envAr.size, d=self.time[1]-self.time[0])
            self.f_signal = np.fft.rfft(self.envAr)
          
            self.cut_f_signal = self.f_signal.copy()
            self.cut_f_signal[(self.W<10)] = 0
            
            self.cut_signal = irfft(self.f_signal)
           
            # Go through audio frame-by-frame.
            for i in range(0, self.envAr.size, self.hop_length):
                # Fourier transform audio frame.
                self.frame = self.window * self.pad(self.envAr[i:self.window_length + i])
                self.spectrum = np.fft.rfft(self.frame)

                # Downsample spectrum.
                self.spectra = []
                for n in range(1, self.partials + 1):
                    s = resample(self.spectrum, len(self.spectrum) // n)
                    self.spectra.append(s)

                # Truncate to most downsampled spectrum.
                l = min(len(s) for s in self.spectra)
                a = np.zeros((len(self.spectra), l), dtype=self.spectrum.dtype)
                for i, s in enumerate(self.spectra):
                    a[i] += s[:l]

                # Multiply spectra per frequency bin.
                self.hps = np.product(np.abs(a), axis=0)

                # TODO Blur spectrum to remove noise and high-frequency content.
                #kernel = sp.signal.gaussian(9, 1)
                #hps = sp.signal.fftconvolve(hps, kernel, mode='same')

                # TODO Detect peaks with a continuous wavelet transform for polyphonic signals.
                #peaks = sp.signal.find_peaks_cwt(np.abs(hps), np.arange(1, 3))

                # Pick largest peak, it's likely f0.
                self.peak = np.argmax(self.hps)
                self.f0 = self.frequencies[self.peak]
                self.freqs.append(self.f0)
                
        self.pat = play()
        self.pat = pyo.Pattern(play, self.refreshRate).play()  
        #self.freqsAr = np.asarray(self.freqs, int)
        
        uni, count = np.unique(self.freqsAr, return_counts=True)
        glitch = np.where(count<5)
        a = np.delete(uni, 0[glitch])
        
        #np.delete(self.freqsNum[a])
        #self. = np.argwhere(self.freqsNum[1]<5)
        #np.delete(self.freqsNum, 1, [0,1])
        
        
        #for i in range(self.freqsNum.size):
        
        self.attack = pyo.AttackDetector(self.ctrl, .01, 20, minthresh=-20)
        self.freq = pyo.Sig(400)

        def note():
            self.freq.value = int(random.choice(self.freqs))

        self.trig = note()
        self.trig = pyo.TrigFunc(self.attack, note)
        return self.freq

'''

if __name__ == "__main__":

    algo = AsAmp()

    #algo.setSound('feu.wav')
    algo.setStartStop(start=20,stop=30)

    mul = algo.amp()
    #algo.out(1)

    osc = pyo.Sine(400, mul=mul).out()


    s.gui(locals())