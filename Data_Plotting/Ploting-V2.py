import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# Reading space deliminated files into a dataframe
df_all = pd.read_csv('Data_2112016415 PM4-1R Hazard INS1.csv',sep='\s+')

# print df_all.head(10)

df_required = pd.read_csv('Data_2112016415 PM4-1R Hazard INS1.csv',sep='\s+',header=None, skiprows=[0,1],usecols=[3, 5, 9], names=['Displacement','Force','Voltage'])

#print df_required.head(10)

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


#plots
fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.plot(displacement, force, linestyle='-', linewidth=2, color='b', label='Force vs Displacement')

ax2 = ax1.twinx()
ax2.plot(displacement, voltage, linestyle='-', linewidth=2, color='r', label='Voltage vs Displacement')


# Labels
# x-Axis label
ax1.set_xlabel('Displacement (mm)',fontsize=20)

# y-Axis Left
ax1.set_ylabel('Force (Nm)', color='b',fontsize=20)
plt.tick_params(axis="y", labelcolor="b",pad=12)


# y-Axis Right
ax2.set_ylabel('Voltage (Nm)', color='r',fontsize=20)
plt.tick_params(axis="y", labelcolor="r",pad=12)

#ask matplotlib for the plotted objects and their labels
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines +lines2, labels +labels2,loc=6)


# Plot title
ax1.set_title('Force and Voltage versus Displacement Plot',fontsize=22, y=1.03)
# y=1.03 is for spacing between plot title and the Plot


ax1.grid()

plt.show()

plt.save()
