import Tkinter as tk     # python 2
import tkFont as tkfont  # python 2
import os

import subprocess
class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # root = tk.Tk()
        label = tk.Label(self, text="CESC traffic analyser", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        labelIP1 = tk.Label(self, text="Enter IP1")
        labelIP2 = tk.Label(self, text="Enter IP2")

        button2 = tk.Button(self, text="View Traffic", command=lambda: self.window_two(entry1.get()))
        button1 = tk.Button(self, text="View Interfaces", command=lambda: self.window_one(entry1.get()))
        button3 = tk.Button(self, text="Traffic Type", command=lambda: self.window_three(entry1.get()))
        button4 = tk.Button(self, text="Traffic Route", command=lambda: self.window_four(entry1.get(),entry2.get()))

        entry1 = tk.Entry(self)
        entry1.focus()
        entry2 = tk.Entry(self)
        
        
        labelIP1.pack(side="left")
        entry1.pack(side="left")
        labelIP2.pack(side="left")
        entry2.pack(side="left")
        # entry2.pack()
        button2.pack()
        button1.pack()
        button3.pack()
        button4.pack()
        # self.bind('<Return>',self.window_two(entry1.get()))
 
        # button2.pack()
    # def helloCallBack(self):
    #     tkMessageBox.showinfo( "Hello Python", "Hello World")    
    
    def window_one(self,str):
        # print str
        # os.system('python ipstatus.py '+str)
        # self.helloCallBack()
        subprocess.Popen('python ipstatus.py '+str)
    def window_two(self,str):
        # print str
        subprocess.Popen('python iptrafficanimatehoriz.py '+str)
        # os.system('python iptraffic(DESC).py '+str)
    def window_three(self,str):
        # print str
        # os.system('python traffictype.py '+str)
        subprocess.Popen('python traffictype.py '+str)
    def window_four(self,str1,str2):
        # print str
        # os.system('python routespan.py '+str1+" "+str2)            
        subprocess.Popen('python routespan.py '+str1+" "+str2)            


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()





if __name__ == "__main__":
    app = SampleApp()

    app.mainloop()