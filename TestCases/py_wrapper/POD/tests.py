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
n_of_modes = 10
n_of_points = 4789
n_of_fields = 11
ipca = []
const_fields = [0]*n_of_fields
is_const = [False]*n_of_fields
header = ["\"PointID\"","\"x\"","\"y\"","\"Pressure\"","\"Velocity_x\"","\"Velocity_y\"","\"Nu_Tilde\"","\"Pressure_Coefficient\"","\"Density\"","\"Laminar_Viscosity\"","\"Heat_Capacity\"","\"Thermal_Conductivity\"","\"Skin_Friction_Coefficient_x\"","\"Skin_Friction_Coefficient_y\"","\"Heat_Flux\"","\"Y_Plus\"","\"Eddy_Viscosity\""]

for i in range(n_of_fields):
    ipca.append(IncrementalPCA(n_components=n_of_modes, batch_size=n_of_modes, whiten=False))

for j in range(int(n_time_steps/n_of_modes)):
    fields = np.empty([n_of_modes,n_of_points, n_of_fields])
    for i in range(n_of_modes):
        file_name = "restart_flow_"+str(i*j+offset).zfill(5)+".csv"
        test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
        for k in range(n_of_fields):
            fields[i,:,k] = test[0:n_of_points,k+3].reshape(1, -1)
            # print(np.mean(fields[i,:,k]))
            # print(fields[i,:,k])
            if np.count_nonzero(fields[i,:,k])> 0.05*n_of_points:
                
                const_fields[k] = np.mean(fields[i,:,k])
                is_const[k] = True
            # print(is_const)

    for k in range(n_of_fields):
        if is_const[k] == False:
            
            ipca[k].partial_fit(fields[:,:,k])


print(is_const)
    

reduced_primal = np.empty([n_of_modes, n_time_steps, n_of_fields])
for i in range(n_time_steps):
    file_name = "restart_flow_"+str(i+offset).zfill(5)+".csv"
    test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
    loaded_primal = np.empty([n_of_points, n_of_fields])
    for j in range(n_of_fields):
        loaded_primal[:,j] = test[0:n_of_points,j+3].reshape(1, -1)
        # print(loaded_primal.shape)
        if is_const[j] == False:
            reduced_primal[:,i,j] =ipca[j].transform(loaded_primal[:,j].reshape(1, -1))
    
    print(i) 


un_reduced = np.empty([n_of_points, n_of_fields,n_time_steps])
full_primal = np.empty([n_of_points, n_of_fields,n_time_steps])
modes = np.empty([ n_of_modes,n_of_points, n_of_fields])
title = ""
for i in range(len(is_const)):
    
    title = title + header[i] + " "
for i in range(n_time_steps):
    un_reduced_file = open("un_reduced_flow_"+str(i+offset).zfill(5)+".csv", "w+")
    un_reduced_file.write(title+"\n")
    file_name = "restart_flow_"+str(i+offset).zfill(5)+".csv"
    test = np.loadtxt(file_name, comments="\"", delimiter=",", dtype=float)
    print("Time step: " + str(i))
    for j in range(n_of_fields):
        full_primal[:,j,i] = test[0:n_of_points,j+3].reshape(1, -1)
        print(full_primal.shape)
        if is_const[j] == False:
            un_reduced[:,j,i] = ipca[j].inverse_transform(reduced_primal[:,i,j])
            
        else:
            un_reduced[:,j,i] = np.ones(n_of_points)*const_fields[j]
    np.savetxt(un_reduced_file,np.vstack((np.asarray(range(n_of_points)), test[0:n_of_points, 1].transpose(), test[0:n_of_points,2].transpose(),un_reduced[:,:,i].transpose())).transpose(), delimiter=",")

    un_reduced_file.close()
for i in range(n_of_fields):
    if is_const[i] == False:
        modes[:,:, i] = ipca[i].components_
        # print(str(np.median(np.divide(np.abs(un_reduced[:,j,i]-full_primal[:,j,i]),np.abs(full_primal[:,j,i]))))+" "+str(np.max((np.divide(np.abs(un_reduced[:,j,i]-full_primal[:,j,i]),np.abs(full_primal[:,j,i]))))))

np.save("x", test[0:n_of_points,1])
np.save("y", test[0:n_of_points:,2]) 
np.save("full",full_primal)
np.save("un_reduced", un_reduced)
np.save("modes", modes)

# fig, ax = plt.subplots()

# line = ax.tripcolor(test[0:n_of_points,1], test[0:n_of_points,2],un_reduced[0:n_of_points,0,0])
# # plt.colorbar(line, ax=ax.ravel().tolist())

# ani = animation.FuncAnimation(fig, animate, interval=20, blit=True, save_count=50)
# plt.show()

