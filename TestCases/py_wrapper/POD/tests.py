import numpy as np
from sklearn.decomposition import IncrementalPCA
from matplotlib import pyplot as plt
import time
import matplotlib.animation as animation


def animate(i):
    line = ax.tripcolor(test[0:n_of_points,1], test[0:n_of_points,2], un_reduced[:,0,i%n_time_steps])  # update the data.
    
    return line,


n_time_steps = 500
offset = 1500
n_of_modes = 25
n_of_points = 300
n_of_fields = 3
ipca = []
for i in range(n_of_fields):
    ipca.append(IncrementalPCA(n_components=n_of_modes, batch_size=n_of_modes, whiten=False))

for j in range(int(n_time_steps/n_of_modes)):
    fields = np.empty([n_of_modes,n_of_points, n_of_fields])
    for i in range(n_of_modes):
        file_name = "restart_flow_"+str(i*j+offset).zfill(5)+".csv"
        test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
        for k in range(n_of_fields):
            fields[i,:,k] = test[0:n_of_points,k+3].reshape(1, -1)
    print(fields[:,:,k].shape)
    for k in range(n_of_fields):
        ipca[k].partial_fit(fields[:,:,k])

        print(ipca[k].n_samples_seen_)
    

reduced_primal = np.empty([n_of_modes, n_time_steps, n_of_fields])
for i in range(n_time_steps):
    file_name = "restart_flow_"+str(i+offset).zfill(5)+".csv"
    test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
    loaded_primal = np.empty([n_of_points, n_of_fields])
    for j in range(n_of_fields):
        loaded_primal[:,j] = test[0:n_of_points,j+3].reshape(1, -1)
     
        reduced_primal[:,i,j] =ipca[j].transform(loaded_primal[:,j].reshape(1, -1))
    print(i)


un_reduced = np.empty([n_of_points, n_of_fields,n_time_steps])
full_primal = np.empty([n_of_points, n_of_fields,n_time_steps])
for i in range(n_time_steps):
    file_name = "restart_flow_"+str(i+offset).zfill(5)+".csv"
    test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
    print("Time step: " + str(i))
    for j in range(n_of_fields):
        full_primal[:,j,i] = test[0:n_of_points,j+3].reshape(1, -1)
        print(full_primal.shape)
        un_reduced[:,j,i] = ipca[j].inverse_transform(reduced_primal[:,i,j])
        # print(str(np.median(np.divide(np.abs(un_reduced[:,j,i]-full_primal[:,j,i]),np.abs(full_primal[:,j,i]))))+" "+str(np.max((np.divide(np.abs(un_reduced[:,j,i]-full_primal[:,j,i]),np.abs(full_primal[:,j,i]))))))

np.save("x", test[0:n_of_points,1])
np.save("y", test[0:n_of_points:,2]) 
np.save("full",full_primal)
np.save("un_reduced", un_reduced)


fig, ax = plt.subplots()

line = ax.tripcolor(test[0:n_of_points,1], test[0:n_of_points,2],un_reduced[0:n_of_points,0,0])
# plt.colorbar(line, ax=ax.ravel().tolist())

ani = animation.FuncAnimation(fig, animate, interval=20, blit=True, save_count=50)
plt.show()

