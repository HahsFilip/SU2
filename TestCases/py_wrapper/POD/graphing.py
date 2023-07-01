import numpy as np
from matplotlib import pyplot as plt
x = np.load("x.npy")
y = np.load("y.npy")
full_primal = np.load("full.npy")
un_reduced = np.load("un_reduced.npy")
values =  np.abs(np.divide(np.abs(full_primal[:,2,400]-un_reduced[:,0,400]),full_primal[:,2,400]))
print(values)
fig1, ax1 = plt.subplots()
ax1.set_aspect('equal')
tpc = ax1.tripcolor(x,y,values)
fig1.colorbar(tpc)
# ax1.set_title('matplotlib.pyplot.tripcolor() Example')
plt.show()
plt.plot(values)
plt.show()
# plt.tripcolor(x,y, np.abs(full_primal[:,0,1500]-un_reduced[:,0,1500]))
# plt.show()