import numpy as np

list_1 =[ 1,3,4,5,6,7,9]
list_2 =[ 2,4,5,2,6,12,2]

tuple_1 = zip(list_1,list_2)

list_3 = [1,2,3,4,5,6]
list_4 = [2,3,1,5,12,1]

tuple_2 = zip(list_3,list_4)
print tuple_1
print tuple_2

x  = (100, 0, 10,10,10)
yL = (50, 50, 10,10,11)
yR = (12, 10, 12, 10,11)



for i in range(len(x)):
    if (x[i],yL[i])==(x[i],yR[i]):
        print i
