# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

# See read the https://floris.readthedocs.io for documentation

# Compare 3 turbine results to SOWFA in 8 m/s, higher TI case

import matplotlib.pyplot as plt
import floris.tools as wfct
import numpy as np
import pandas as pd

# HIGH TI


# Low TI


# Write out SOWFA results
layout_x = (1000.0, 1756.0, 2512.0, 3268.0, 4024.0)
layout_y = (1000.0, 1000.0, 1000.0, 1000.0, 1000.0)
sowfa_results = np.array([
[1940,843.9,856.9,893.1,926.2,0,0,0,0,0],
[1575.3,1247.3,1008.4,955.4,887.1,25,0,0,0,0],
[1576.4,1065,1147.5,1185.2,1198.5,25,20,15,10,0],
[1577,986.9,1338.7,1089.4,999.8,25,25,0,0,0],
[1941.1,918.6,945.3,948,968.2,0,0,0,0,0]
])
df_sowfa = pd.DataFrame(sowfa_results, 
                        columns = ['p0','p1','p2','p3','p4','y0','y1','y2','y3','y4'] )

## SET UP FLORIS AND MATCH TO BASE CASE
wind_speed = 8.38
TI = 0.09

# Initialize the FLORIS interface fi, use default gauss model
fi = wfct.floris_interface.FlorisInterface("example_input.json")
fi.reinitialize_flow_field(wind_speed=[wind_speed],turbulence_intensity=[TI],layout_array=(layout_x, layout_y))

# Setup blonel
fi_b = wfct.floris_interface.FlorisInterface("example_input.json")
fi_b.floris.farm.set_wake_model('blondel')
fi_b.reinitialize_flow_field(wind_speed=[wind_speed],turbulence_intensity=[TI],layout_array=(layout_x, layout_y))

# Compare yaw combinations
yaw_combinations = [
    (0,0,0,0,0), (25,0,0,0,0), (25,25,0,0,0)
]
yaw_names = ['%d/%d/%d/%d/%d' % yc for yc in yaw_combinations]

# Plot individual turbine powers
fig, axarr = plt.subplots(1,3,sharex=True,sharey=True,figsize=(12,5))

total_sowfa = []
total_gauss = []
total_blondel = []

for y_idx, yc in enumerate(yaw_combinations):

    # Collect SOWFA DATA
    s_data = df_sowfa[(df_sowfa.y0==yc[0]) & (df_sowfa.y1==yc[1]) & (df_sowfa.y2==yc[2]) & (df_sowfa.y2==yc[3]) & (df_sowfa.y2==yc[4])]
    s_data = [s_data.p0.values[0], s_data.p1.values[0],s_data.p2.values[0],s_data.p3.values[0],s_data.p4.values[0]]
    total_sowfa.append(np.sum(s_data))

    # Collect Gauss data
    fi.calculate_wake(yaw_angles=yc)
    g_data = np.array(fi.get_turbine_power())/ 1000. 
    total_gauss.append(np.sum(g_data))

    # Collect Blondel data
    fi_b.calculate_wake(yaw_angles=yc)
    b_data = np.array(fi_b.get_turbine_power())/ 1000. 
    total_blondel.append(np.sum(b_data))

    ax = axarr[y_idx]
    ax.set_title(yc)
    ax.plot(['T0','T1','T2','T3','T4'], s_data,'k',marker='s',label='SOWFA')
    ax.plot(['T0','T1','T2','T3','T4'], g_data,'g',marker='o',label='Gauss')
    ax.plot(['T0','T1','T2','T3','T4'], b_data,'b',marker='*',label='Blondel')

axarr[-1].legend()

# Calculate totals and normalized totals
total_sowfa = np.array(total_sowfa)
nom_sowfa = total_sowfa/total_sowfa[0]

total_gauss = np.array(total_gauss)
nom_gauss = total_gauss/total_gauss[0]

total_blondel = np.array(total_blondel)
nom_blondel = total_blondel/total_blondel[0]

fig, axarr = plt.subplots(1,2,sharex=True,sharey=False,figsize=(8,5))

# Show results
ax  = axarr[0]
ax.set_title("Total Power")
ax.plot(yaw_names,total_sowfa,'k',marker='s',label='SOWFA',ls='None')
ax.axhline(total_sowfa[0],color='k',ls='--')
ax.plot(yaw_names,total_gauss,'g',marker='o',label='Gauss',ls='None')
ax.axhline(total_gauss[0],color='g',ls='--')
ax.plot(yaw_names,total_blondel,'b',marker='*',label='Blondel',ls='None')
ax.axhline(total_blondel[0],color='b',ls='--')
ax.legend()

# Normalized results
ax  = axarr[1]
ax.set_title("Normalized Power")
ax.plot(yaw_names,nom_sowfa,'k',marker='s',label='SOWFA',ls='None')
ax.axhline(nom_sowfa[0],color='k',ls='--')
ax.plot(yaw_names,nom_gauss,'g',marker='o',label='Gauss',ls='None')
ax.axhline(nom_gauss[0],color='g',ls='--')
ax.plot(yaw_names,nom_blondel,'b',marker='*',label='Blondel',ls='None')
ax.axhline(nom_blondel[0],color='b',ls='--')



plt.show()
