# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:14:50 2019

@author: Asif Towheed
"""

import wx
import os
import time 
import threading
import AD_Functions as ad

SUBJECTNAME = ""

KILL_THREAD = False
TRAINEDNUMBER = []
TRAINED = False

################################################################################
## BEGIN NEW TRAINING SET --> SECOND WINDOW
################################################################################
class ADThread(threading.Thread):
    def __init__(self, index):    
        threading.Thread.__init__(self)
        self.i = 0
        self.index = index
    
    def run(self):
        if self.index == 0:
            global SUBJECTNAME
            ad.AD_RESET()
            ad.AD_Begin(SUBJECTNAME)

        ad.AD_GetWalk(self.index)
#        ad.AD_GenerateDiffs()

#        global TRAINED, TRAINEDMUTEX
#        TRAINED = True
#        ad.AD_GetDCT()
#        while not TRAINEDMUTEX:
#            dummy = 0
        ad.MID_AD_RESET()
        TRAINEDMUTEX = False
            

#        while True:
#            self.i += 1
#            #print(self.i)
#            
#            global TRAINEDNUMBER
#            if TRAINEDNUMBER[self.index]:
#                break
        

################################################################################
## BEGIN NEW TRAINING SET --> SECOND WINDOW
################################################################################
class TrainFrame(wx.Frame):
    """
    Class used for creating frames other than the main one
    """
    def __init__(self, title, parent=None):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.count = 0 
        panel = wx.Panel(self) 
                
        vbox = wx.BoxSizer(wx.VERTICAL) 
        
        self.hboxlist = []
        self.gaugelist = []
        self.btnlist = []
        
        
        for i in range(10):
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            self.hboxlist.append(hbox)
            gauge = wx.Gauge(panel, range = 20, size = (250, 25), style =  wx.GA_HORIZONTAL) 
            self.gaugelist.append(gauge)
            btn = wx.ToggleButton(panel, i*10, label = "Start " + str(i)) 
            self.btnlist.append(btn)
            self.Bind(wx.EVT_TOGGLEBUTTON, self.OnStart, self.btnlist[i]) 

            self.hboxlist[i].Add(self.gaugelist[i], proportion = 1, flag = wx.ALIGN_CENTRE) 
            self.hboxlist[i].Add(self.btnlist[i], proportion = 1, flag = wx.RIGHT, border = 10) 
            
            global TRAINEDNUMBER
            TRAINEDNUMBER.append(False)
            
            vbox.Add(self.hboxlist[i], proportion = 1, flag = wx.ALIGN_CENTRE) 
             
        self.btn = wx.Button(panel, label = "Done!")
        self.Bind(wx.EVT_BUTTON, self.FinishedTraining, self.btn)
        vbox.Add(self.btn, proportion = 1, flag = wx.ALIGN_CENTRE)
        
        vbox.SetSizeHints(self)    # Resize the window to fit the buttons ONLY
        self.SetSizer(vbox)

        self.Centre() 
        self.Show()   
    		
    def FinishedTraining(self, e): 
        print('finished!!!')
        self.Close()
        
    def OnStart(self, e): 
        global TRAINED
        TRAINED = False
        self.e = e
        label = e.GetEventObject().GetLabel()
        print(label)
        state = e.GetEventObject().GetValue() 
        if state == True: 
            e.GetEventObject().SetLabel("Stop " + label[-1]) 
            a = ADThread(int(label[-1]))
            a.start()
            for btn in self.btnlist:
                if btn.GetLabel()[-1] != label[-1]:
                    print(btn.GetLabel())
#                    print(label)
                    btn.Disable()
        else: 
            ad.TerminateCapture()
#            e.GetEventObject().SetLabel("Training Walk " + label[-1])
            e.GetEventObject().Disable()            

            def statusfunc(x):
#                global TRAINEDMUTEX
#                while not TRAINED:
#                    self.gaugelist[x].SetValue(ad.AD_GetStatus())
                self.gaugelist[x].SetValue(20)
#                TRAINEDMUTEX = True
                print('TRAINING FINISH')
                for btn in self.btnlist:
                    if btn.GetLabel()[-1] != label[-1] and not TRAINEDNUMBER[int(btn.GetLabel()[-1])]:
                        btn.Enable()
                    else:
                        TRAINEDNUMBER[int(btn.GetLabel()[-1])] = True
            t1 = threading.Thread(target = statusfunc, args = (int(label[-1]),))
            t1.start()
            e.GetEventObject().SetLabel("Trained Walk " + label[-1])

##-------------------------------------------------------------------------------



################################################################################
## BEGIN NEW TRAINING SET --> FIRST WINDOW
################################################################################
class NewRecognitionSet(wx.Frame):
    """
    Class used for creating frames other than the main one
    """
    def __init__(self, title, parent=None):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.Show()
        panel = wx.Panel(self) 
                
        vbox = wx.BoxSizer(wx.VERTICAL) 
        
        hbox_fortext = wx.BoxSizer(wx.HORIZONTAL) 
        label1 = wx.StaticText(panel, 1234, "Enter the name of the subject")
        hbox_fortext.Add(label1, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t1 = wx.TextCtrl(panel, size = (300, 24))         
        self.t1.SetFocus()
        hbox_fortext.Add(self.t1,0,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t1.Bind(wx.EVT_TEXT,self.OnKeyTyped)        


        nm = wx.StaticBox(panel, -1, 'Please Select the Algorithm:') 
        nmSizer = wx.StaticBoxSizer(nm, wx.VERTICAL) 
        
        nmbox = wx.BoxSizer(wx.HORIZONTAL)         
        self.rb1 = wx.RadioButton(panel,-1, label = 'Accumulated Differences', style = wx.RB_GROUP)
        self.rb2 = wx.RadioButton(panel,-1, label = 'Gait Energy Image')
        self.rb3 = wx.RadioButton(panel,-1, label = 'SURF')        
        nmbox.Add(self.rb1, 0, wx.ALL|wx.CENTER, 5) 
        nmbox.Add(self.rb2, 0, wx.ALL|wx.CENTER, 5) 
        nmbox.Add(self.rb3, 0, wx.ALL|wx.CENTER, 5) 
    		
        nmSizer.Add(nmbox, 0, wx.ALL|wx.CENTER, 10)  
    		
        hbox = wx.BoxSizer(wx.HORIZONTAL) 
        okButton = wx.Button(panel, -1, 'ok')     		
        hbox.Add(okButton, 0, wx.ALL|wx.LEFT, 10) 
        cancelButton = wx.Button(panel, -1, 'cancel')     		
        hbox.Add(cancelButton, 0, wx.ALL|wx.LEFT, 10) 

        vbox.Add(hbox_fortext,0, wx.ALL|wx.CENTER, 5) 
        vbox.Add(nmSizer,0, wx.ALL|wx.CENTER, 5) 
        vbox.Add(hbox,0, wx.ALL|wx.CENTER, 5) 
        panel.SetSizer(vbox) 
        self.Centre() 
             
        panel.Fit() 
        vbox.SetSizeHints(self)    # Resize the window to fit the buttons ONLY
        self.Show()  
        
        # Binding the cancel and ok buttons to their events        
        self.Bind(wx.EVT_BUTTON, self.cancelOp, cancelButton)
        self.Bind(wx.EVT_BUTTON, self.TrainingAlgOp, okButton)

        # Binding the radio group to its event
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadiogroup)
        self.selectedAlg = "Accumulated Differences"

        
    # If the cancel button is pressed --> go back to the previous GUI screen
    def cancelOp(self, event):
        MyForm().Show()
        self.Close()

    # If the OK button is pressed --> Start the selected algorithm ***********
    def TrainingAlgOp(self, event):
        global SUBJECTNAME
        if SUBJECTNAME is '':
            print('Please enter a subject name')
        else:
            ad.AD_RESET()
            TrainFrame(title=self.selectedAlg)
            self.Close()

        
    # If a radio button is selected
    def OnRadiogroup(self, e):
       rb = e.GetEventObject()
       self.selectedAlg = rb.GetLabel()

    def OnKeyTyped(self, e):
        print(e.GetString())
        global SUBJECTNAME
        SUBJECTNAME = e.GetString()
#-------------------------------------------------------------------------------





################################################################################
## MAIN FRAME --> START WINDOW
################################################################################
class MyForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Gait Recognition Software!')
        
        # Create the buttons contained within the class itself with their titles
        self.NewTrainingBtn = wx.Button(self, -1, 'Begin new Training Set')
        self.NewRecogBtn = wx.Button(self, -1, 'Run New Recognition')
        self.NewVerifyBtn = wx.Button(self, -1, 'Run New Verification')
        self.ViewTrainedBtn = wx.Button(self, -1, 'View Trained Sets')
        self.ViewHistoryBtn = wx.Button(self, -1, 'View History')
        
        # Create the sizer object to add the buttons to
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.NewTrainingBtn, 0, wx.EXPAND, 0)
        sizer.Add(self.NewRecogBtn, 0, wx.EXPAND, 0)
        sizer.Add(self.NewVerifyBtn, 0, wx.EXPAND, 0)
        sizer.Add(self.ViewTrainedBtn, 0, wx.EXPAND, 0)
        sizer.Add(self.ViewHistoryBtn, 0, wx.EXPAND, 0)
        sizer.SetSizeHints(self)    # Resize the window to fit the buttons ONLY
        self.SetSizer(sizer)
        
        # Create the action listeners for the buttons
        self.Bind(wx.EVT_BUTTON, self.newTraining, self.NewTrainingBtn)
        self.Bind(wx.EVT_BUTTON, self.newRecognition, self.NewRecogBtn)
        self.Bind(wx.EVT_BUTTON, self.newTraining, self.NewVerifyBtn)
        self.Bind(wx.EVT_BUTTON, self.newTraining, self.ViewTrainedBtn)
        self.Bind(wx.EVT_BUTTON, self.newTraining, self.ViewHistoryBtn)

        self.Centre() 


    def newTraining(self, event):
        print(os.getcwd())
        title = 'Begin New Training Set'
        frame = NewRecognitionSet(title=title)
        self.Close()

        
    def newRecognition(self, event):
        # Do something
        print ('onOK handler')
        import GEI_Algorithm
        GEI_Algorithm.mainrun()
#-------------------------------------------------------------------------------








################################################################################
## DRIVER --> RUN PROGRAM
################################################################################
if __name__ == '__main__':
    print (wx.ART_INFORMATION)
    app = wx.App()
    frame = MyForm().Show()
    app.MainLoop()
    del app
#-------------------------------------------------------------------------------
