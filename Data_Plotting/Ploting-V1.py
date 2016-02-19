import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# Reading space deliminated files into a dataframe
df_all = pd.read_csv('Data_2112016415 PM4-1R Hazard INS1.csv',sep='\s+')

#print df_all.head(10)

df_required = pd.read_csv('Data_2112016415 PM4-1R Hazard INS1.csv',sep='\s+',header=None, skiprows=[0,1],usecols=[3, 5, 9], names=['Displacement','Force','Voltage'])


# coverting dataframe to list using .tolist()
displacement = df_required['Displacement'].tolist()
force = df_required['Force'].tolist()
voltage = df_required['Voltage'].tolist()


# making it all positive
# for i in range(len(displacement)):
#     displacement[i] = abs(displacement[i])

# alternatively in list comprehension
displacement =[abs(i) for i in displacement]
force = [abs(j) for j in force]
voltage = [abs(k) for k in voltage]

# --------Plots-------
ax = plt.subplot(1,1,1)



# Plot title
ax.set_title('Force and Voltage versus Displacement Plot',fontsize=22, y=1.03)
# y=1.03 is for spacing between plot title and the Plot


# X-axis
plt.xlabel('Displacement (mm)',fontsize=20)
plt.tick_params(axis="x", pad=8)

# Y-axis Left
plt.ylabel('Force (Nm)', color='b',fontsize=20)
plt.tick_params(axis="y", labelcolor="b",pad=12)

plt.ylim(0,12)
plt.yticks(range(0,13,2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))

plt.plot(displacement, force, linestyle='-', linewidth=2, color='b', label='Force vs Displacement')
# plt.legend(loc='center left',fancybox=True)

# Y-axis Right
plt.twinx()
plt.ylabel('Voltage (Nm)', color='r',fontsize=20)
plt.tick_params(axis="y", labelcolor="r",pad=12)

plt.ylim(0,10)
plt.yticks(range(0,11,2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))

plt.plot(displacement, voltage, linestyle='-', linewidth=2, color='r', label='Voltage vs Displacement')
# plt.legend(loc='center right',fancybox=True)








#Grids
ax.grid(True)
gridlines = ax.get_xgridlines() + ax.get_ygridlines()

for line in gridlines:
    line.set_linestyle('-')
    line.set_color('dimgrey')


plt.subplots_adjust(left=0.1,right=0.9,bottom=0.13)

# saving plots into a files
plt.savefig("Force, Voltage vs Displacement Sample X.png",dpi=100,format="png")




plt.show()
