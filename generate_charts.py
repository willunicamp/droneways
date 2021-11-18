from matplotlib import pyplot as plt
import sys
import numpy as np
import pickle
import copy
import os
import time
import glob
import re

city = sys.argv[1]


fishbone = pickle.load(open(city+"/fish_dict.p","rb"))
spider = pickle.load(open(city+"/spider_dict.p","rb"))

fish_eff = fishbone["efficiency"]
fish_ratio = fishbone["edges_ratio"]
fish_it = fishbone["iterations"]
fish_diam = fishbone["diameter"]
fish_avp = fishbone["avg_path_len"]
fish_avgo = fishbone["outer_avg_path"]
fish_maxo = fishbone["outer_max_path"]


spi_eff = spider["efficiency"]
spi_ratio = spider["edges_ratio"]
spi_it = spider["iterations"]
spi_diam = spider["diameter"]
spi_avp = spider["avg_path_len"]
spi_avgo = spider["outer_avg_path"]
spi_maxo = spider["outer_max_path"]

with open(city+"/fish_table.csv","a+") as f:
    print("iteration,map coverage ratio,droneway efficiency,droneway average shortest path,droneway diameter,ASPOW,maximum shortest path outer ways", file=f)
    for it,ratio,eff,avp,diam,avgo,maxo in zip(fish_it,fish_ratio,fish_eff,fish_avp,fish_diam,fish_avgo,fish_maxo):
        print(str(it)+","+str(ratio)+","+str(eff)+","+str(avp)+","+str(diam)+","+str(avgo)+","+str(maxo),file=f)

with open(city+"/spi_table.csv","a+") as f:
    print("iteration,map coverage ratio,droneway efficiency,droneway average shortest path,droneway diameter,ASPOW,maximum shortest path outer ways", file=f)
    for it,ratio,eff,avp,diam,avgo,maxo in zip(spi_it,spi_ratio,spi_eff,spi_avp,spi_diam,spi_avgo,spi_maxo):
        print(str(it)+","+str(ratio)+","+str(eff)+","+str(avp)+","+str(diam)+","+str(avgo)+","+str(maxo),file=f)


#Efficiency X Average Outer Paths
plt.style.use('tableau-colorblind10')
fig, ax = plt.subplots()

fish_effavgo = [float(b) / float(m) for b,m in zip(fish_eff, fish_avgo)]
spi_effavgo = [float(b) / float(m) for b,m in zip(spi_eff, spi_avgo)]
for ratio, effav in zip(fish_ratio, fish_effavgo):
    print("{:f} - {:f}".format(ratio,effav))
for ratio, effav in zip(spi_ratio, spi_effavgo):
    print("{:f} - {:f}".format(ratio,effav))
ax.set_ylabel("relative efficiency/average outer path length")
ax.set_xlabel("droneway map coverage")
color='tab:orange'
ax.plot(fish_ratio,fish_effavgo,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_ratio,spi_effavgo,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)
#        ax2 = ax.twinx()
#        color='tab:orange'
#        ax2.plot(fish_ratio,fish_maxo,'-.', color=color)
#        color='tab:blue'
#        ax2.plot(spi_ratio,spi_maxo,'-', color=color)
plt.savefig(city+"/plot_fish_spider_eff_avgo.pdf")

#Coverage X Average Outer Paths
plt.style.use('tableau-colorblind10')
fig, ax = plt.subplots()

ax.set_ylabel("average outer path length (meters)")
ax.set_xlabel("droneway map coverage")
color='tab:orange'
ax.plot(fish_ratio,fish_avgo,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_ratio,spi_avgo,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)
#        ax2 = ax.twinx()
#        color='tab:orange'
#        ax2.plot(fish_ratio,fish_maxo,'-.', color=color)
#        color='tab:blue'
#        ax2.plot(spi_ratio,spi_maxo,'-', color=color)
plt.savefig(city+"/plot_fish_spider_ratio_avgo.pdf")

#Efficiency X Coverage
fig, ax = plt.subplots()

ax.set_ylabel("droneway relative efficiency")
ax.set_xlabel("droneway map coverage")
color='tab:orange'
ax.plot(fish_ratio,fish_eff,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_ratio,spi_eff,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=4)
plt.savefig(city+"/plot_fish_spider_ratio.pdf")

#Efficiency X iteration
fig, ax = plt.subplots()

ax.set_ylabel("droneway relative efficiency")
ax.set_xlabel("heuristic iteration")
color='tab:orange'
ax.plot(fish_it,fish_eff,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_it,spi_eff,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=4)
plt.savefig(city+"/plot_fish_spider_it.pdf")


#iteration X avg_path_len + diameter
fig, ax = plt.subplots()

ax.set_ylabel("droneway average path length")
ax.set_xlabel("heuristic iteration")
color='tab:orange'
ax.plot(fish_it,fish_avp,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_it,spi_avp,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)

plt.savefig(city+"/plot_fish_spider_avp.pdf")

fig, ax = plt.subplots()

ax.set_ylabel("droneway diameter (largest shortest path)")
ax.set_xlabel("heuristic iteration")
color='tab:orange'
ax.plot(fish_it,fish_diam,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_it,spi_diam,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)

plt.savefig(city+"/plot_fish_spider_diam.pdf")

#Coverage X Average Paths
plt.style.use('tableau-colorblind10')
fig, ax = plt.subplots()

ax.set_ylabel("average droneway path length (meters)")
ax.set_xlabel("droneway map coverage")
color='tab:orange'
ax.plot(fish_ratio,fish_avp,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_ratio,spi_avp,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)
#        ax2 = ax.twinx()
#        color='tab:orange'
#        ax2.plot(fish_ratio,fish_maxo,'-.', color=color)
#        color='tab:blue'
#        ax2.plot(spi_ratio,spi_maxo,'-', color=color)
plt.savefig(city+"/plot_fish_spider_cov_avp.pdf")


#Coverage X Diameter
plt.style.use('tableau-colorblind10')
fig, ax = plt.subplots()

ax.set_ylabel("network diameter (meters)")
ax.set_xlabel("droneway map coverage")
color='tab:orange'
ax.plot(fish_ratio,fish_diam,'-',label="Fishbone", color=color)
color='tab:blue'
ax.plot(spi_ratio,spi_diam,'--',label="Spiderweb",color=color)
ax.grid(True)
ax.legend(loc=1)
#        ax2 = ax.twinx()
#        color='tab:orange'
#        ax2.plot(fish_ratio,fish_maxo,'-.', color=color)
#        color='tab:blue'
#        ax2.plot(spi_ratio,spi_maxo,'-', color=color)
plt.savefig(city+"/plot_fish_spider_cov_diam.pdf")
