import time
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
def animate(i):
    line  = ax1.tripcolor(x,y,modes[i%10, :,which_field])
    time.sleep(1)
    return line,
x = np.load("x.npy")
y = np.load("y.npy")
full_primal = np.load("full.npy")
un_reduced = np.load("un_reduced.npy")
modes = np.load("modes.npy")
which_field = 1
which_time_step = 350
values =  np.abs(np.divide(np.abs(full_primal[:,which_field,which_time_step]-un_reduced[:,which_field,which_time_step]),np.mean(full_primal[:,which_field,which_time_step])))
print(values)
# print(full_primal[values==np.nan, which_field, which_time_step])
print(x[values==np.inf])
print(y[values==np.inf])
fig1, ax1 = plt.subplots()
ax1.set_aspect('equal')


tpc = ax1.tripcolor(x,y,modes[0, :,which_field])
fig1.colorbar(tpc)
# ax1.set_title('matplotlib.pyplot.tripcolor() Example')

ani = animation.FuncAnimation(fig1, animate, interval=20, blit=True, save_count=50)
plt.show()
     
# plt.plot(values)
# plt.show()


# plt.tripcolor(x,y, np.abs(full_primal[:,0,1500]-un_reduced[:,0,1500]))
# plt.show()