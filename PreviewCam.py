import cv2
import tkinter as tk
import time
import threading
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as fd

class Application(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.pack()
        self.master.title("Tkinter with Class Template")
        self.create_widgets()

        self.started = threading.Event()
        self.alive   = True
        self.thread  = threading.Thread(target=self.capture)
        self.thread.start()

    def stop(self):
        cv2.destroyAllWindows()
        self.alive = False        
        if self.cap.isOpened() :
            self.cap.release()
        if not self.started.is_set() :
            self.started.set()
        time.sleep(0.1)
        
    def createCamIDFrame(self):
        camIDFrame = ttk.Labelframe(self.frame,text='CameraID',padding=(5),style='My.TLabelframe')
        camIDFrame.grid(row=0,column=0)
        
        self.camID = tk.IntVar()
        self.idRB = []
        for i in [0,1,2,3] :
            self.idRB.append(ttk.Radiobutton(camIDFrame,text= ''+str(i)+' ',value=i,variable=self.camID))
            self.idRB[i].grid(row=0,column=i)
            
        self.bt01 = ttk.Button(camIDFrame,text='Connect')
        self.bt01.grid(row=0,column=5)
        self.bt01.configure(command=self.connectCam)
        
        self.camSize = tk.StringVar()
        self.camSize.set('NotConnected')
        camSizeLabel = ttk.Label(camIDFrame,textvariable=self.camSize)
        camSizeLabel.grid(row=1,column=0,columnspan=4)
        
    def winSizeFrame(self):
        winSizeFrame = ttk.Labelframe(self.frame,text='WindowSize',padding=(5),style='My.TLabelframe')
        winSizeFrame.grid(row=1,column=0)    
        self.ratioList = [12.5,25,50,75,100,125,150,200]
        self.ratioBt = []
        for i in range(8) :
            self.ratioBt.append(tk.Button(winSizeFrame,text=''+str(self.ratioList[i])+'%',width=7,command=self.changeWinSize(i)))
            self.ratioBt[i].grid(row=int((i-i%4)/4),column=i%4)

        self.setWinSize(4)
        self.winSize = tk.StringVar()
        self.winSize.set('NotConnected')
        winSizeLabel = ttk.Label(winSizeFrame,textvariable=self.winSize)
        winSizeLabel.grid(row=2,column=0,columnspan=4)

    def actionFrame(self):
        actionFrame = ttk.Labelframe(self.frame,text='CameraAction',padding=(5),style='My.TLabelframe')
        actionFrame.grid(row=2,column=0)

        self.bt0 = ttk.Button(actionFrame,text='撮影開始',width=9,command=self.previewCam,state="disable")
        self.bt1 = ttk.Button(actionFrame,text='写真保存',width=9,command=self.saveImage,state="disable")
        self.bt2 = ttk.Button(actionFrame,text='録画開始',width=9,command=self.startCapture,state="disable")
        self.bt3 = ttk.Button(actionFrame,text='録画停止',width=9,command=self.stopCapture,state="disable")
        self.bt0.grid(row=0,column=0)
        self.bt1.grid(row=0,column=1)
        self.bt2.grid(row=0,column=2)
        self.bt3.grid(row=0,column=3)
        
        self.changeSize = tk.IntVar()
        self.rb0 = ttk.Radiobutton(actionFrame,text='元サイズで保存' ,value=0,variable=self.changeSize)
        self.rb1 = ttk.Radiobutton(actionFrame,text='拡大縮小して保存',value=1,variable=self.changeSize)
        self.rb0.grid(row=1,column=0,columnspan=2)
        self.rb1.grid(row=1,column=2,columnspan=2)

    def saveImage(self):
        if self.cap.isOpened and self.started.is_set() :
            self.started.clear()
            fType = [("BMP File(*.bmp)",".bmp"),("JPEG File(*.jpg)",".jpg"),("TIFF File(*.tif)",".tif")]
            ret = fd.asksaveasfilename(defaultextension = ".jpg",filetypes=fType)
            if self.changeSize.get() < 1 :
                cv2.imwrite(ret,self.rawFrame)
            else :
                cv2.imwrite(ret,self.frame)
            self.started.set()
        
    def create_widgets(self):
        self.cap = cv2.VideoCapture()
        self.writer = cv2.VideoWriter()
        self.writeFlag = -1
        self.frame = ttk.Frame(self,padding=10)
        self.frame.grid()
        self.createCamIDFrame()
        self.winSizeFrame()
        self.actionFrame()
        
    def changeWinSize(self,sizeID):
        def inner():
            self.setWinSize(sizeID)
        return inner
    
    def setWinSize(self,sizeID):
        for i in range(8):
            self.ratioBt[i].configure(foreground="black")
            self.ratioBt[sizeID].configure(foreground="red")
            self.sizeRatio = self.ratioList[sizeID]
            self.sizeID = sizeID
            if self.cap.isOpened() :
                self.winW = int(self.camW * self.sizeRatio / 100)
                self.winH = int(self.camH * self.sizeRatio / 100)
                self.frameSize = (self.winW,self.winH)
                self.winSize.set('WindowSize : W'+str(self.winW)+'xH'+str(self.winH))
                
    def connectCam(self):
        id = self.camID.get()
        if 0 <= id < 4 :
            self.cap = cv2.VideoCapture(id)
            if self.cap.isOpened() :
                self.bt01.configure(state='disable')
                self.camW = int(self.cap.get(3))                
                self.camH = int(self.cap.get(4))
                self.camSize.set('CamSize : W'+str(self.camW)+' x H'+str(self.camH))
                for i in [0,1,2,3] :
                    self.idRB[i].configure(state='disable')
                self.setWinSize(self.sizeID)
                self.bt0.configure(state="active")
                
    def previewCam(self):
        self.started.set()
        self.bt0.configure(state="disable")
        self.bt1.configure(state="active")
        self.bt2.configure(state="active")

    def capture(self):
        while(self.alive):
            self.started.wait()
            if self.cap.isOpened() :
                ret, self.rawFrame = self.cap.read()    
                self.frame = cv2.resize(self.rawFrame,self.frameSize)
                cv2.imshow('capture',self.frame)
                if self.writeFlag == 0 :
                    self.writer.write(self.rawFrame)
                elif self.writeFlag == 1 :
                    self.writer.write(self.frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    self.started.clear()
                    self.bt0.configure(state="active")
                    self.bt1.configure(state="disable")
                    self.bt2.configure(state="disable")


    def startCapture(self):
        for i in range(8) :
            self.ratioBt[i].configure(state="disable")
        self.bt1.configure(state="disable")
        self.bt2.configure(state="disable")
        self.bt3.configure(state="active")
        self.rb0.configure(state="disable")
        self.rb1.configure(state="disable")
        self.started.clear()
        ret = fd.asksaveasfilename(defaultextension = ".avi",filetypes=[("AVI file","*.avi")])
        if self.changeSize.get() < 1 :
            self.writer.open(ret,0,30.0,(self.camW,self.camH))
            self.writeFlag = 0
        else :
            self.writer.open(ret,0,30.0,(self.winW,self.winH))
            self.writeFlag = 1
        self.started.set()
            
    def stopCapture(self):
        self.started.clear()
        self.writeFlag = -1
        self.writer.release()
        self.started.set()
        for i in range(8) :
            self.ratioBt[i].configure(state="active")
        self.bt1.configure(state="active")
        self.bt2.configure(state="active")
        self.bt3.configure(state="disable")
        self.rb0.configure(state="active")
        self.rb1.configure(state="active")
        self.setWinSize(self.sizeID)


def main():
    root = tk.Tk()
    app = Application(master=root)#Inherit
    app.mainloop()
    app.stop()

if __name__ == "__main__":
    main()
