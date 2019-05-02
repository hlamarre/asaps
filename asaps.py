import pyo
import numpy as np
import wx
import process as pro
import synth as syn

s = pyo.Server().boot()


class Audio:
    def __init__(self, mode=pro.LiveIn()):
        self.algo = pro.AsAmp()
        self.table = self.algo.table
        self.snd = self.algo.snd

    def refresh(self):
        self.snd = self.algo.snd
        self.snd.refresh()
        self.algo = self.algo
        self.algo.refresh()
        self.table = self.algo.table
        

class AsFrame(wx.Frame):
    def __init__(self, parent, title, pos, size, audio):
        wx.Frame.__init__(self, parent, id=-1, title=title, pos=pos, size=size)
        self.parent = parent
        self.audio = audio
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#555558")
        s.start()

        self.sound = 'feu.wav' 
        
        self.osc = syn.WvGd()
        self.osc.out()
        self.mode = pro.SndReader()

        self.amps = ['as is', 'average', 'deviation', 'histogram', 'sections']
        self.popup = wx.Choice(self.panel, id=-1, pos=(5,5), choices=self.amps)
        self.popup.SetSelection(0)
        self.popup.Bind(wx.EVT_CHOICE, self.changeAlgo)

        self.modes = ['file', 'live']
        self.popup2 = wx.Choice(self.panel, id=-1, pos=(95,5), choices=self.modes)
        self.popup2.SetSelection(0)
        self.popup2.Bind(wx.EVT_CHOICE, self.changeMode) 

        self.synChoice = ['waveguide', 'FM', 'wavetable'] 
        self.popupSyn = wx.Choice(self.panel, id=-1, pos=(870,240), choices=self.synChoice)
        self.popupSyn.SetSelection(0)
        self.popupSyn.Bind(wx.EVT_CHOICE, self.changeSynth)  

        self.res = pyo.PyoGuiControlSlider(self.panel, 1, 100, init=50, pos=(130,140), size=(25,300), log=False, integer=True, powoftwo=False, orient=wx.VERTICAL)
        self.resText = wx.StaticText(self.panel, id=-1, label="res", pos=(135,440))
        self.res.Bind(wx.EVT_LEFT_UP, self.setRes) 

        self.floorA = pyo.PyoGuiControlSlider(self.panel, .001, 100, init=.001, pos=(210,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.floorAText = wx.StaticText(self.panel, id=-1, label="floorA", pos=(200,440))
        self.floorA.Bind(wx.EVT_LEFT_UP, self.changeFloorA) 

        self.ampA = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=100, pos=(260,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ampTextA = wx.StaticText(self.panel, id=-1, label="ampA", pos=(250,440))
        self.ampA.Bind(wx.EVT_LEFT_UP, self.changeAmp)

        self.lagA = pyo.PyoGuiControlSlider(self.panel, 0, 100, init=0, pos=(310,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.lagTextA = wx.StaticText(self.panel, id=-1, label="lagA", pos=(310,440))
        self.lagA.Bind(wx.EVT_LEFT_UP, self.setSmooth) 

        self.floorB = pyo.PyoGuiControlSlider(self.panel, .001, 100, init=.001, pos=(390,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.floorBText = wx.StaticText(self.panel, id=-1, label="floorB", pos=(380,440))
        self.floorB.Bind(wx.EVT_LEFT_UP, self.changeFloorB) 

        self.ampB = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=100, pos=(440,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ampTextB = wx.StaticText(self.panel, id=-1, label="ampB", pos=(430,440))
        self.ampB.Bind(wx.EVT_LEFT_UP, self.changeAmpB)

        self.lagB = pyo.PyoGuiControlSlider(self.panel, 0, 100, init=0, pos=(490,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.lagTextB = wx.StaticText(self.panel, id=-1, label="lagB", pos=(490,440))
        self.lagB.Bind(wx.EVT_LEFT_UP, self.setSmoothB) 

        self.chooseButton = wx.Button(self.panel, id=-1, label="load sound", pos=(625,110))
        self.chooseButton.Bind(wx.EVT_BUTTON, self.loadSnd) 

        self.freeze = wx.Button(self.panel, id=-1, label='freeze', pos=(5,35), size=(82,20))
        self.freeze.Bind(wx.EVT_BUTTON, self.freezeBuff)  
        self.freeze.Hide()

        '''
        self.ctrl = pyo.PyoGuiControlSlider(self.panel, 1, 100, init=50, pos=(10,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ctrlText = wx.StaticText(self.panel, id=-1, label="", pos=(0,440))
        '''
        self.ctrl = wx.Slider(self.panel, id=-1, value=50, minValue=1, maxValue=100, pos=(10,133), size=(-1,310), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.ctrlText = wx.StaticText(self.panel, id=-1, label="", pos=(0,440)) 

        self.ogVol = pyo.PyoGuiControlSlider(self.panel, .001, 1, init=1, pos=(310,10), size=(25,100), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ogVolText = wx.StaticText(self.panel, id=-1, label="", pos=(160,15))
        self.ogVol.Bind(wx.EVT_LEFT_UP, self.setOGVol)        
        
        self.SndVSizer = wx.BoxSizer(wx.VERTICAL)
        self.sndview = pyo.PyoGuiSndView(parent=self.panel, pos=(370,30), size=(300,200), style=0, )
        self.sndview.setTable(self.audio.algo.tableOG)
        self.sndview.setSelection(0, 1)
        self.sndview.Bind(pyo.EVT_PYO_GUI_SNDVIEW_SELECTION, self.setStSp)
        self.SndVSizer.Add(self.sndview, 1, wx.VERTICAL | wx.EXPAND, 5)

        self.memSize = pyo.PyoGuiControlSlider(self.panel, 1, 60, init=1, pos=(400,30), size=(440,10), log=False, integer=False, powoftwo=False, orient=wx.HORIZONTAL)
        self.memText = wx.StaticText(self.panel, id=-1, label="memory time", pos=(300,25))
        self.memSize.Bind(wx.EVT_LEFT_UP, self.setMem)  
        self.memSize.Hide() 
        self.memText.Hide()     
        
        self.checkTextA = wx.StaticText(self.panel, id=-1, label="A", pos=(570,220))
        self.checkTextB = wx.StaticText(self.panel, id=-1, label="B", pos=(570,270))        

        self.checkText1 = wx.StaticText(self.panel, id=-1, label="amp", pos=(600,180))
        self.checkText2 = wx.StaticText(self.panel, id=-1, label="pitch", pos=(670,180))
        self.checkText3 = wx.StaticText(self.panel, id=-1, label="filter", pos=(750,180))
        self.checkText4 = wx.StaticText(self.panel, id=-1, label="extra", pos=(810,180))


        self.checkAmpA = wx.CheckBox(self.panel, id=-1, label="", pos=(610,220), size=(-1, 20), style=0)
        self.checkAmpA.Bind(wx.EVT_CHECKBOX, self.setAmpA) 
    
        self.checkPitchA = wx.CheckBox(self.panel, id=-1, label="", pos=(680,220), size=(-1, 20), style=0)
        self.checkPitchA.Bind(wx.EVT_CHECKBOX, self.setPitchA) 

        self.checkFilterA = wx.CheckBox(self.panel, id=-1, label="", pos=(750,220), size=(-1, 20), style=0)
        self.checkFilterA.Bind(wx.EVT_CHECKBOX, self.setFilterA) 

        self.checkExtraA = wx.CheckBox(self.panel, id=-1, label="", pos=(820,220), size=(-1, 20), style=0)
        self.checkExtraA.Bind(wx.EVT_CHECKBOX, self.setExtraA) 


        self.checkAmpB = wx.CheckBox(self.panel, id=-1, label="", pos=(610,270), size=(-1, 20), style=0)
        self.checkAmpB.Bind(wx.EVT_CHECKBOX, self.setAmpB) 
    
        self.checkPitchB = wx.CheckBox(self.panel, id=-1, label="", pos=(680,270), size=(-1, 20), style=0)
        self.checkPitchB.Bind(wx.EVT_CHECKBOX, self.setPitchB) 

        self.checkFilterB = wx.CheckBox(self.panel, id=-1, label="", pos=(750,270), size=(-1, 20), style=0)
        self.checkFilterB.Bind(wx.EVT_CHECKBOX, self.setFilterB) 

        self.checkExtraB = wx.CheckBox(self.panel, id=-1, label="", pos=(820,270), size=(-1, 20), style=0)
        self.checkExtraB.Bind(wx.EVT_CHECKBOX, self.setExtraB) 
        
        vmainsizer = wx.BoxSizer()

        sizer7 = self.SndVSizer

        vmainsizer.Add(sizer7, 1, wx.BOTTOM | wx.LEFT, 350)
        self.panel.SetSizerAndFit(vmainsizer)
 
        self.Change()
        self.audio.algo.out()


    def Change(self):
        self.param1 = self.audio.algo.amp()
        self.param2 = self.audio.algo.amp2()

        if self.checkAmpA.IsChecked():
            self.osc.setAmp(self.param1) 
        if self.checkPitchA.IsChecked():
            self.osc.setPitch(self.param1) 
        if self.checkFilterA.IsChecked(): 
            self.osc.setFilter(self.param1) 
        if self.checkExtraA.IsChecked():
            self.osc.setExtra(self.param1) 
        if self.checkAmpB.IsChecked():
            self.osc.setAmp(self.param2) 
        if self.checkPitchB.IsChecked():
            self.osc.setPitch(self.param2) 
        if self.checkFilterB.IsChecked():
            self.osc.setFilter(self.param2) 
        if self.checkExtraB.IsChecked():
            self.osc.setExtra(self.param2) 

        if self.popup2.GetSelection() == 1 :
            self.audio.algo.stop()             
 
        self.audio.algo.sig.mul = self.ampA.getValue()
        self.audio.algo.sig2.mul = self.ampB.getValue()

   
   
    def setOGVol(self, evt):
        if evt.LeftUp(): 
            x = self.ogVol.getValue() 
            self.audio.algo.out(x)
        evt.Skip()        



    '''
    def changeAlgo(self, evt):
        self.ctrl.Unbind(wx.EVT_LEFT_UP)            

            
        if self.popup.Selection == 0 :
            self.audio.algo = pro.AsAmp()
            
        elif self.popup.Selection == 1 :
            self.audio.algo = pro.AvgAmp()
            self.ctrl.SetValue(10)
            self.ctrl.SetRange(1,60)
            self.ctrlText.SetLabel("period")
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changePeriod)

        elif self.popup.Selection == 2 :
            self.audio.algo = pro.DevAmp()

        elif self.popup.Selection == 3 :
            self.audio.algo = pro.HistAmp()
            self.ctrl.SetValue(50)
            self.ctrl.SetRange(1,100)
            self.ctrlText.SetLabel('density')
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeDens) 

        elif self.popup.Selection == 4 :
            self.audio.algo = pro.SectAmp()
            self.ctrl.SetValue(3)
            self.ctrl.SetRange(1,100)
            self.ctrlText.SetLabel('length')
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeLength) 

        elif self.popup.Selection == 5 :
            self.audio.algo = pro.MarkAmp()
            self.ctrl.SetValue(1)
            self.ctrl.SetRange(1,5)
            self.ctrlText.SetLabel("order")
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeOrder)   

        self.Change()    
        self.Refresh()
    '''

    def changeAlgo(self, evt):
        self.audio.algo.stop()

        if self.popup.Selection == 0 :
            self.audio.algo = pro.AsAmp()
            self.ctrlText.SetLabel('')    
                    
        elif self.popup.Selection == 1 :
            self.audio.algo = pro.AvgAmp()
            self.ctrl.SetValue(10)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(60)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel("period 10")
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changePeriod)

        elif self.popup.Selection == 2 :
            self.audio.algo = pro.DevAmp()
            self.ctrlText.SetLabel('')

        elif self.popup.Selection == 3 :
            self.audio.algo = pro.HistAmp()
            self.ctrl.SetValue(50)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(100)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel('density 50')
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeDens) 

        elif self.popup.Selection == 4 :
            self.audio.algo = pro.SectAmp()
            self.ctrl.SetValue(3)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(100)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel('length .03')
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeLength) 

        elif self.popup.Selection == 5 :
            self.audio.algo = pro.MarkAmp()
            self.audio.refresh
            self.ctrl.SetValue(1)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(5)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel("order 1")
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeOrder)   


        if self.popup2.GetSelection() == 0 :
            self.mode = pro.SndReader()
            self.audio.algo.setMode(self.mode)
        elif self.popup2.GetSelection() == 1 :
            self.mode = pro.LiveIn()
            self.audio.algo.setMode(self.mode)
            self.audio.algo.stop()          
        

        self.audio.algo.setSound(self.sound)     
        self.Change()
        
        self.tempOGVol = self.ogVol.getValue() 
        self.audio.algo.out(self.tempOGVol)

        xA = self.floorA.getValue()* 100
        self.param1 += xA 
        xB = self.floorB.getValue()* 100
        self.param2 += xB

        self.Refresh()
    

    def changeMode(self, evt):
        self.audio.algo.stop()
        if self.popup2.Selection == 0 :
            self.mode = pro.SndReader()
            self.sndview.Show()
            self.chooseButton.Show()
            self.memSize.Hide()
            self.memText.Hide()
            self.freeze.Hide()
            self.ogVol.setValue(0)
            self.ogVol.Show()
            self.audio.algo.setMode(self.mode)
            self.audio.refresh()
            self.Change()

        elif self.popup2.Selection == 1 :
            self.mode = pro.LiveIn()
            self.sndview.Hide()
            self.chooseButton.Hide()
            self.memSize.Show()
            self.memText.Show()
            self.freeze.Show()
            self.ogVol.Hide()
            self.audio.algo.setMode(self.mode)
            self.audio.refresh()
            self.Change()        
            self.audio.algo.stop()

        xA = self.floorA.getValue()* 100
        self.param1 += xA 
        xB = self.floorB.getValue()* 100
        self.param2 += xB
  
        self.Refresh()


    def changeSynth(self, evt):
        self.osc.stop()
        if self.popupSyn.Selection == 0 :
            self.osc = syn.WvGd()

        if self.popupSyn.Selection == 1 :
            self.osc = syn.FM()

        if self.popupSyn.Selection == 2 :
            self.osc = syn.WT()

        self.osc.out()
        self.Change()

        xA = self.floorA.getValue()* 100
        self.param1 += xA 
        xB = self.floorB.getValue()* 100
        self.param2 += xB



    def freezeBuff(self, evt):
        self.audio.algo.freeze()
        self.freeze.Label = 'unfreeze'
        self.freeze.Bind(wx.EVT_BUTTON, self.unFreezeBuff)

    def unFreezeBuff(self, evt):
        self.audio.algo.unFreeze()
        self.freeze.Label = 'freeze'
        self.freeze.Bind(wx.EVT_BUTTON, self.freezeBuff)


    ''' 
    def changePeriod(self, evt):
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue()) 
        self.audio.algo.setPeriod(x)
        evt.Skip()

    def changeDens(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setDensity(x)
        evt.Skip()

    def changeLength(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setLength(x)
        evt.Skip()

    def changeOrder(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setOrder(x)
        evt.Skip()
    '''

    def changePeriod(self, evt):
        x = evt.GetInt()
        self.audio.algo.setPeriod(x)
        self.ctrlText.SetLabel("period %d" % x) 

    def changeDens(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setDensity(x)
        self.ctrlText.SetLabel("density %d" % x)

    def changeLength(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setLength(x)
        self.ctrlText.SetLabel("length %d" % x)

    def changeOrder(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setOrder(x)
        self.ctrlText.SetLabel("order %d" % x)
    

    def setRes(self, evt): 
        if evt.LeftUp(): 
            x = self.res.getValue()
            self.audio.algo.setRes(x)
            self.Change()
        evt.Skip()

    def changeFloorA(self, evt):  
        if evt.LeftUp(): 
            x = self.floorA.getValue()* 100
            self.param1 += x
        evt.Skip()

    def changeAmp(self, evt): 
        if evt.LeftUp(): 
            x = self.ampA.getValue() * 1
            self.audio.algo.sig.mul = x
        evt.Skip()

    def setSmooth(self, evt): 
        if evt.LeftUp(): 
            x = self.lagA.getValue() * .01
            self.audio.algo.sig.time = x
        evt.Skip()


    def changeFloorB(self, evt):  
        if evt.LeftUp(): 
            x = self.floorB.getValue()* 100
            self.param2 += x
        evt.Skip()

    def changeAmpB(self, evt):
        if evt.LeftUp(): 
            x = self.ampB.getValue() * 1
            self.audio.algo.sig2.mul = x
        evt.Skip()

    def setSmoothB(self, evt):  
        if evt.LeftUp(): 
            x = self.lagB.getValue() * .01
            self.audio.algo.sig2.time = x
        evt.Skip()


    def setMem(self,evt):
        if evt.LeftUp(): 
            x = self.memSize.getValue()
            self.audio.algo.setDur(x)
 
            self.audio.refresh()
            self.Change()

            xA = self.floorA.getValue()* 100
            self.param1 += xA 
            xB = self.floorB.getValue()* 100
            self.param2 += xB 

        evt.Skip()


    def loadSnd(self, evt):
        wildcard = "All files|*.*|" \
               "AIFF file|*.aif;*.aiff;*.aifc;*.AIF;*.AIFF;*.Aif;*.Aiff|" \
               "Wave file|*.wav;*.wave;*.WAV;*.WAVE;*.Wav;*.Wave"
        self.dlg = wx.FileDialog(self, message="Choose a new soundfile...", wildcard=wildcard, style=wx.FD_OPEN)
        if self.dlg.ShowModal() == wx.ID_OK:
            path = self.dlg.GetPath()
            if path != "":
                self.sound = path
                self.audio.algo.setSound(self.sound)

        self.dlg.Destroy()
        self.Change()
        self.sndview.setTable(self.audio.algo.tableOG)

        xA = self.floorA.getValue()* 100
        self.param1 += xA 
        xB = self.floorB.getValue()* 100
        self.param2 += xB

        self.Refresh()    


    def setStSp(self, evt):
        self.audio.algo.setStartStop((evt.value[0]*self.audio.algo.durOG), (evt.value[1]*self.audio.algo.durOG))
        self.Change()

        xA = self.floorA.getValue()* 100
        self.param1 += xA 
        xB = self.floorB.getValue()* 100
        self.param2 += xB

        self.Refresh() 


    def setAmpA(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setAmp(self.param1)
        else:
            self.osc.defAmp()  

    def setFilterA(self, evt):
        x = evt.IsChecked() 
        if x: 
            self.osc.setFilter(self.param1)  
        else:
            self.osc.defFilter() 

    def setPitchA(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setPitch(self.param1)  
        else:
            self.osc.defPitch() 

    def setExtraA(self, evt):
        x = evt.IsChecked() 
        if x:   
            self.osc.setExtra(self.param1)  
        else:
            self.osc.defExtra() 


    def setAmpB(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setAmp(self.param2)
        else:
            self.osc.defAmp()  

    def setFilterB(self, evt):
        x = evt.IsChecked() 
        if x: 
            self.osc.setFilter(self.param2)  
        else:
            self.osc.defFilter() 

    def setPitchB(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setPitch(self.param2)  
        else:
            self.osc.defPitch() 

    def setExtraB(self, evt):
        x = evt.IsChecked() 
        if x:   
            self.osc.setExtra(self.param2)  
        else:
            self.osc.defExtra() 



app = wx.App()

aud = Audio()
mainFrame = AsFrame(None, title='asaps', pos=(100,100), size=(1000,500), audio=aud)
mainFrame.Show()

app.MainLoop()



