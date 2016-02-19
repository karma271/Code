import re
import numpy as np
import matplotlib.pyplot as plt
import os

rootdir = '/Users/prasoon/Desktop/KOSTAL_Sample_Data/test_data'

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        f=open(os.path.join(subdir,file),'r')
        print file
        data=np.loadtxt(f)
#plot data
        plt.plot(data[:,1],data[:,2],'gs')
        plt.axvline(0,linestyle='--',color='k')
        plt.axhline(0,linestyle='--',color='k')
        plt.show()
        f.close()
