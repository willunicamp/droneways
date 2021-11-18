from abc import ABCMeta, abstractmethod
import matplotlib as mpl
import numpy as np

mpl.use("cairo")

import sympy as sym
import shapely.geometry as spy
from descartes.patch import PolygonPatch
import multiprocessing
import time
import matplotlib.pyplot as plt
import pickle
import graph_tool.all as gt
import math
from AStar import AStar

class Heuristic(object):
    __metaclass__ = ABCMeta

    def __init__(self, graph_path, doNotInit=False):
        self.g = gt.load_graph(graph_path)
        self.g.set_directed(False)
        self.g.set_edge_filter(None)
        self._v0 = self.g.num_edges()
        self.g.gp.size_km = self.g.new_graph_property("float")
        self.g.gp.size_km = 0
        if doNotInit is False:
            self.g.ep.distance = self.g.new_edge_property("float")
            self.g.gp.efficiency = self.g.new_graph_property("float")
            self.g.gp.efficiency = 0.0
            self.g.ep.line_distance = self.g.new_edge_property("float")
            self.g.ep.color = self.g.new_edge_property("string")
            self.g.ep.width = self.g.new_edge_property("float")
            self.g.ep.filter = self.g.new_edge_property("bool")
            self.g.ep.meters_distance = self.g.new_edge_property("float")
            self.star = AStar(self.g)
            self._nodes = list()
            self._edges = list()
            #calculate the distance for every edge, to use as weight
            for e in self.g.edges():
                p1 = spy.Point(self.g.vp.lon[e.source()],self.g.vp.lat[e.source()])
                p2 = spy.Point(self.g.vp.lon[e.target()],self.g.vp.lat[e.target()])
                self.g.ep.color[e] = "#c3c7bf"
                self.g.ep.width[e] = 1
                self.g.ep.filter[e] = 0
                self.g.ep.distance[e] = p1.distance(p2)
                self.g.ep.meters_distance[e] = self.haversine(p1,p2)
                self.g.gp.size_km += self.g.ep.meters_distance[e]
        else:
            i = 0
            for e in self.g.edges():
                self.g.gp.size_km += self.g.ep.meters_distance[e]
                if(self.g.ep.filter[e] == 1):
                    i+=1
            print(str(i)+" edges")

    def clear_graph(self):
        self.g.set_edge_filter(None)
        self._nodes = list()
        self._edges = list()
        #calculate the distance for every edge, to use as weight
        for e in self.g.edges():
            self.g.ep.color[e] = "#c3c7bf"
            self.g.ep.width[e] = 1
            self.g.ep.filter[e] = 0

    def map_convex_hull(self):
        #create the convex hull of the map
        map_points = list()
        for n in self.g.vertices():
            map_points.append(spy.Point(self.g.vp.lon[n],self.g.vp.lat[n]))
        map_multipoint = spy.MultiPoint(map_points)
        return map_multipoint.convex_hull

    def haversine(self,p1, p2, unit_m = True):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        default unit : km
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [p1.x, p1.y, p2.x, p2.y])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        if (unit_m):
            r *= 1000
        return c * r

    @abstractmethod
    def execute(self):
        pass

    def draw(self,path):
        gt.graph_draw(self.g, pos=self.g.vp.pos,vertex_size=0,edge_pen_width=self.g.ep.width,
                      edge_color=self.g.ep.color,output_size=(3200, 1600),
                      vertex_font_size=8, output=path)

    def _chunks(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def save(self, path):
        self.g.save(path)


    def _max_avg_parallel(self,queue,nodes):
        #print("%s enter" % multiprocessing.current_process().name)
        s = 0.0
        i = 0
        for node in nodes:
            path_length=gt.shortest_distance(self.g, source=node, weights=self.g.ep.meters_distance)
            s += sum(v for v in path_length.a if v not in (0,float("inf")) )
        queue.put(s)
        #print("%s exit" % multiprocessing.current_process().name)

    def _efficiency_parallel(self,queue,nodes):
        #print("%s enter" % multiprocessing.current_process().name)
        s = 0.0
        i = 0
        for node in nodes:
            path_length=gt.shortest_distance(self.g, source=node, weights=self.g.ep.meters_distance)
            s += sum(1.0/v for v in path_length.a if v !=0)
        queue.put(s)
        #print("%s exit" % multiprocessing.current_process().name)

    def ratio(self):
        self.g.set_edge_filter(self.g.ep.filter)
        size_km_droneway = 0
        for edge in self.g.edges():
            size_km_droneway += self.g.ep.meters_distance[edge]
        return float(size_km_droneway)/float(self.g.gp.size_km)

    def local_efficiency(self, filtered=True):
        if filtered == True:
            self.g.set_edge_filter(self.g.ep.filter)
        else:
            self.g.set_edge_filter(None)
        sumall = 0.0
        n = self.g.num_vertices()
        print(str(n)+" iterations")
        i=0
        for node in self.g.vertices():
            self.g.set_edge_filter(self.g.ep.filter)
            neighbors = node.out_neighbors()
            neighmap = self.g.new_vertex_property("bool")
            for neighbor in neighbors:
                neighmap[neighbor] = 1
            self.g.set_vertex_filter(neighmap)
            sumall += self.efficiency2()
            print(self.g.num_vertices())
            self.g.set_vertex_filter(None)
        return sumall*1.0/n

    def efficiency(self, filtered=True):
        self.g.set_vertex_filter(None)
        if filtered == True:
            self.g.set_edge_filter(self.g.ep.filter)
        else:
            self.g.set_edge_filter(None)
        jobs = []
        avg = 0.0
        thenodes = list()
        for n in self.g.vertices():
            thenodes.append(n)
        n = len(thenodes)
        if n != 0:
            parts = int(n/40)
            queue = multiprocessing.Queue()
            node_parts = self._chunks(thenodes, parts)
            for nodes in node_parts:
                p = multiprocessing.Process(target=self._efficiency_parallel, args=(queue,nodes))
                jobs.append(p)
                p.start()

            for j in jobs:
                avg += queue.get() # will block

            for j in jobs:
                j.join()

            avg *= 1.0/(n*(n-1.0))
        self.g.gp.efficiency = avg
        return avg

    def merge_vertices(self,graph,v1,v2):
        for e in graph.vertex(v2).out_edges():
            ne = graph.add_edge(v1,e.target())
            graph.ep.color[ne] = graph.ep.color[e]
            graph.ep.distance[ne] = graph.ep.distance[e]
        for e in graph.vertex(v2).in_edges():
            ne = graph.add_edge(v1,e.source())
            graph.ep.color[ne] = graph.ep.color[e]
            graph.ep.distance[ne] = graph.ep.distance[e]
        graph.remove_vertex(v2)

    def max_and_avg_outer_ways(self):
        graph = gt.Graph(self.g)

        #filter the graph to get the droneway
        graph.set_edge_filter(None)
        #graph.set_vertex_filter(None)
        graph.set_edge_filter(graph.ep.filter)

        the_node = None
        #add the nodes of the droneway to be removed
        for e in graph.edges():
            if(the_node is None):
                the_node = e.source()
            graph.ep.meters_distance[e] = 0

        #remove the filter to get all the neighbors of the droneway
        graph.set_edge_filter(None)
        graph.set_vertex_filter(None)
        print("Num vertex: "+str(graph.num_vertices()))


#        gt.graph_draw(graph, pos=graph.vp.pos,vertex_size=0,edge_pen_width=1,
#                      edge_color=graph.ep.color, output_size=(3200, 1600),
#                      output="images/testgraph.eps")

        #calculate the shortest path from this node to all others
        path_length=gt.shortest_distance(graph, source=the_node, weights=graph.ep.meters_distance)
        n = graph.num_vertices()
        values = list()
        for v in path_length.a:
            if v != float("inf"):
                values.append(v)
        #get the average shortest path
        s = sum(values)/n
        #get the maximum shortest path
        m = max(values)
        return m,s



    def max_and_avg_path(self, filtered=True):
        self.g.set_edge_filter(None)
        if filtered == True:
            self.g.set_edge_filter(self.g.ep.filter)
        else:
            self.g.set_edge_filter(None)
        self.g.set_vertex_filter(gt.label_largest_component(self.g))
        jobs = []
        avg = 0.0
        thenodes = list()
        for n in self.g.vertices():
            thenodes.append(n)
        n = len(thenodes)
        if n != 0:
            parts = int(n/40)
            queue = multiprocessing.Queue()
            node_parts = self._chunks(thenodes, parts)
            for nodes in node_parts:
                p = multiprocessing.Process(target=self._max_avg_parallel, args=(queue,nodes))
                jobs.append(p)
                p.start()

            for j in jobs:
                avg += queue.get() # will block

            for j in jobs:
                j.join()

            avg *= 1.0/(n*(n-1.0))
            maximum, ends = gt.pseudo_diameter(self.g, weights=self.g.ep.meters_distance)
        return maximum, avg

    def efficiency2(self, filtered=True):
        if filtered == True:
            self.g.set_edge_filter(self.g.ep.filter)
        else:
            self.g.set_edge_filter(None)
        avg = 0.0
        n = self.g.num_vertices()
        if n != 0:
            for node in self.g.vertices():
                path_length=gt.shortest_distance(self.g, source=node, weights=self.g.ep.meters_distance)
                avg += sum(1.0/v for v in path_length.a if v !=0)
            avg *= 1.0/(n*(n-1.0))
        return avg

    def _most_distant_points(self,multipoint):
        distance = prev_distance = 0
        point1 = None
        point2 = None
        for pointa in multipoint:
            for pointb in multipoint:
                if not pointa.__eq__(pointb):
                    distance = pointa.distance(pointb)
                    if distance >= prev_distance:
                        point1 = pointa
                        point2 = pointb
                        prev_distance = distance
        return point1, point2

    def _add_path(self, start, end, astar=False):
        if astar is True:
            for n,e in self.star.path(start,end):
                self._nodes.append(n)
                self._edges.append(e)
        else:
            nodes, edges = gt.shortest_path(self.g,start,end,
                    negative_weights=False,weights=self.g.ep.meters_distance)
            self._nodes += nodes
            self._edges += edges

    def _highlight_path(self, color, width):
        for e in self._edges:
            self.g.ep.color[e] = color
            self.g.ep.width[e] = width
            self.g.ep.filter[e] = 1

    def _nearest_node(self,point,node_list=None):
        short_distance = float("inf")
        node = None
        node_list = node_list if node_list is not None else self.g.vertices()
        for n in node_list:
            distance = point.distance(spy.Point(self.g.vp.lon[n],self.g.vp.lat[n]))
            if distance < short_distance:
                short_distance = distance
                node = n
        return node

    #find the central node using betweennness
    def _central_bt_node(self):
        centrality, e_centrality= gt.betweenness(self.g,
                weight=self.g.ep.meters_distance)
        central = None
        #find the highest betweeenness node, i.e., the central one
        for v in self.g.vertices():
            if(central is None):
                central = v
            if(centrality[central] < centrality[v]):
                central = v
        return central

    def info(self):
        print("Vertices "+str(self.g.num_vertices()))
        print("Edges "+str(self.g.num_edges()))
