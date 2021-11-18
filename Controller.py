from Fishbone import Fishbone
from Spiderweb import Spiderweb
from matplotlib import pyplot as plt
import numpy as np
import pickle
import copy
import multiprocessing
import os
import time
import glob
import re

class Controller:
    def __init__(self, graph_path, save_path):
        self.fish = Fishbone(graph_path)
        self.spider = Spiderweb(graph_path)
        self.save_path = save_path
        if not os.path.exists(save_path):
            os.makedirs(save_path+"/graphs")

    def calculate_properties(self):
        fish_dict = dict()
        spi_dict = dict()
        #create the dictionaries to store the calculated values
        spi_dict["efficiency"] = list()
        spi_dict["edges_ratio"] = list()
        spi_dict["diameter"] = list()
        spi_dict["avg_path_len"] = list()
        spi_dict["outer_avg_path"] = list()
        spi_dict["outer_max_path"] = list()
        spi_dict["iterations"] = list()

        fish_dict["efficiency"] = list()
        fish_dict["edges_ratio"] = list()
        fish_dict["diameter"] = list()
        fish_dict["avg_path_len"] = list()
        fish_dict["outer_avg_path"] = list()
        fish_dict["outer_max_path"] = list()
        fish_dict["iterations"] = list()

        #load the global efficiency
        efficiency0 = 0.0
        if os.path.exists(self.save_path+"/globalefficiency.p"):
            efficiency0 = pickle.load(open(self.save_path+"/globalefficiency.p", "rb"))
            print("Global Efficiency loaded:"+str(efficiency0))
        else:
            efficiency0 = self.spider.efficiency(filtered=False)
            pickle.dump(efficiency0, open(self.save_path+"/globalefficiency.p","wb"))
            print("Global efficiency calculated")

        #load graphs generated from the heuristics
        files_fish = glob.glob(self.save_path+"/graphs/fish*.gt")
        files_spider = glob.glob(self.save_path+"/graphs/spider*.gt")
        files_fish = sorted(files_fish,key=lambda x:float(re.findall("([0-9]+?)\.gt",x)[0]))
        files_spider = sorted(files_spider,key=lambda x:float(re.findall("([0-9]+?)\.gt",x)[0]))

        for file in files_fish:
            graph = Fishbone(file, doNotInit=True)
            diam, avgpath =graph.max_and_avg_path()
            out_max, out_avg = graph.max_and_avg_outer_ways()
            fish_dict["diameter"].append(diam)
            fish_dict["avg_path_len"].append(avgpath)
            it = int(''.join(re.findall("([0-9]+?)",file)))
            fish_dict["iterations"].append(it)
            efficiency = float(graph.efficiency())/float(efficiency0)
            fish_dict["efficiency"].append(efficiency)
            ratio = graph.ratio()
            fish_dict["edges_ratio"].append(ratio)
            fish_dict["outer_avg_path"].append(out_avg)
            fish_dict["outer_max_path"].append(out_max)
            print("""iteration:{:d}\nefficiency:{:f}\nedges ratio:{:f}\ndiameter:{:f}
avg path lenght:{:f}\navg outer path:{:f}\nmax outer path:{:f}\n"""
                  .format(it,efficiency,ratio,diam,avgpath,out_avg, out_max))

        pickle.dump(fish_dict, open(self.save_path+"/fish_dict.p","wb"))

        for file in files_spider:
            graph = Spiderweb(file, doNotInit=True)
            out_max, out_avg = graph.max_and_avg_outer_ways()
            diam, avgpath =graph.max_and_avg_path(filtered=True)
            spi_dict["diameter"].append(diam)
            spi_dict["avg_path_len"].append(avgpath)
            it = int(''.join(re.findall("([0-9]+?)",file)))
            spi_dict["iterations"].append(it)
            efficiency = float(graph.efficiency(filtered=True))/float(efficiency0)
            spi_dict["efficiency"].append(efficiency)
            ratio = graph.ratio()
            spi_dict["edges_ratio"].append(ratio)
            spi_dict["outer_avg_path"].append(out_avg)
            spi_dict["outer_max_path"].append(out_max)
            print("""iteration:{:d}\nefficiency:{:f}\nedges ratio:{:f}\ndiameter:{:f}
avg path lenght:{:f}\navg outer path:{:f}\nmax outer path:{:f}\n"""
                  .format(it,efficiency,ratio,diam,avgpath,out_avg, out_max))

        pickle.dump(spi_dict, open(self.save_path+"/spider_dict.p","wb"))

    def compare(self):

        fishbone = pickle.load(open(self.save_path+"/fish_dict.p","rb"))
        spider = pickle.load(open(self.save_path+"/spider_dict.p","rb"))

        map_diam, map_avp = self.fish.max_and_avg_path(filtered=False);

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

        with open(self.save_path+"/fish_table.csv","a+") as f:
            print("iteration,map coverage ratio,droneway efficiency,droneway average shortest path,droneway diameter,ASPOW,maximum shortest path outer ways", file=f)
            for it,ratio,eff,avp,diam,avgo,maxo in zip(fish_it,fish_ratio,fish_eff,fish_avp,fish_diam,fish_avgo,fish_maxo):
                print(str(it)+","+str(ratio)+","+str(eff)+","+str(avp)+","+str(diam)+","+str(avgo)+","+str(maxo),file=f)

        with open(self.save_path+"/spi_table.csv","a+") as f:
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
        plt.savefig(self.save_path+"/plot_fish_spider_eff_avgo.eps")

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
        plt.savefig(self.save_path+"/plot_fish_spider_ratio_avgo.eps")

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
        plt.savefig(self.save_path+"/plot_fish_spider_ratio.eps")

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
        plt.savefig(self.save_path+"/plot_fish_spider_it.eps")


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

        plt.savefig(self.save_path+"/plot_fish_spider_avp.eps")

        fig, ax = plt.subplots()

        ax.set_ylabel("droneway diameter (largest shortest path)")
        ax.set_xlabel("heuristic iteration")
        color='tab:orange'
        ax.plot(fish_it,fish_diam,'-',label="Fishbone", color=color)
        color='tab:blue'
        ax.plot(spi_it,spi_diam,'--',label="Spiderweb",color=color)
        ax.grid(True)
        ax.legend(loc=1)

        plt.savefig(self.save_path+"/plot_fish_spider_diam.eps")

    def executeSpiderweb(self, start=1, ntimes=10, step=3):
        for i in range(start,(start+ntimes*step),step):
            t = time.time()
            divisions = 8
            self.spider.execute(divisions,i)
            self.spider.draw(self.save_path+"/spiderweb"+str(i)+".eps")
            self.spider.save(self.save_path+"/graphs/spiderweb"+str(i)+".gt")
            self.spider.clear_graph()
            print("Done "+str(i)+": "+str(time.time()-t))

    def executeFishbone(self, start=1, ntimes=10, step=3):
        for i in range(start,(start+ntimes*step),step):
            t = time.time()
            self.fish.execute(i)
            self.fish.draw(self.save_path+"/fishbone"+str(i)+".eps")
            self.fish.save(self.save_path+"/graphs/fishbone"+str(i)+".gt")
            self.fish.clear_graph()
            print("Done "+str(i)+": "+str(time.time()-t))

    def draw_graphs(self):
        self.paris.info()
        self.paris.draw("paris.eps")
