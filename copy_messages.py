import fnmatch
import os
from shutil import copyfile, copy
from tkinter import filedialog, Tk

if __name__ == '__main__':
    window = Tk()
    targetPath = filedialog.askdirectory(parent=window,
                                        initialdir=os.getcwd(),
                                        title="Choose destination")
    try:                                    
        for _, dirs, _ in os.walk(os.curdir):
            for dir in dirs:
                print(dir)
                if not os.path.isdir(targetPath+'/'+dir):
                    os.mkdir(targetPath+'/'+dir)
                #for _,dirs2, filenames in os.walk("%s/%s"%(os.curdir,dir)):
                print("listdir:", os.listdir(dir))
                for filename in os.listdir(dir):
                #for filename in filenames:
                    if fnmatch.fnmatch(filename, 'message*'):
                        print(os.curdir+'/'+dir+'/'+filename)
                        copy(os.curdir+'/'+dir+'/'+filename, targetPath+'/'+dir)
    catch Exception as e:
        print(e)