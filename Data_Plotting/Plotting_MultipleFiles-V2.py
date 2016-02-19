import numpy as np
import matplotlib.pyplot as plt

for fname in ('file1.txt','file2.txt','file3.txt'):
    data=np.loadtxt(fname)
    X=data[:,1]
    Y=data[:,2]
    plt.plot(X,y,':ro')
plt.ylim((0,55000))
plt.save("plot1.png")
