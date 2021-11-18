from Heuristic import Heuristic

import graph_tool.all as gt
import sympy as sym
import shapely.geometry as spy
import time
import math
import gc

class Spiderweb(Heuristic):
    def __init__(self,path, doNotInit=False):
        Heuristic.__init__(self,path,doNotInit)

    #get a point and return the farthest point from it, searching
    #inside the other_points list
    def _most_distant_point(self,point,other_points=None):
        distance = prev_distance = 0
        the_point = None
        if other_points is None:
            other_points = list(spy.Point(self.g.vp.lon[n],self.g.vp.lat[n]) for n in self.g.vertices())

        for other_point in other_points:
            distance = point.distance(other_point)
            if distance >= prev_distance:
                the_point = other_point
                prev_distance = distance
        return the_point


    #overrides
    def execute(self):
        self.execute(5)

    def execute(self, pieces, circles):
        #find the highest betweeenness node, i.e., the central one
        central_node = self._central_bt_node()
        mid = spy.Point(self.g.vp.lon[central_node],self.g.vp.lat[central_node])
        #find the radius of the map (most distant point from the center)
        farthest_point = self._most_distant_point(mid)
        radius = float(mid.distance(farthest_point))
        radius_step = radius/float(circles)
        #actual_radius is the radius of the circle actually drawing
        actual_radius = 0
        previous_node = None
        first_node = None

        map_hull = self.map_convex_hull()
        #print("Hull found")
        for i in range(0,pieces):
            x = math.cos(math.radians(360/pieces*i))*radius+mid.x
            y = math.sin(math.radians(360/pieces*i))*radius+mid.y
            point = spy.Point(x,y)
            border_point = spy.LineString([mid,point]).intersection(map_hull.boundary)
            border_node = self._nearest_node(border_point)
            self._add_path(central_node,border_node,astar=True)
            gc.collect()


        for j in range(0,circles):
            actual_radius += radius_step
            #divide the circle in n parts
            for i in range(0,pieces):
                #find points at equally distant angles around the circle
                x = math.cos(math.radians(360/pieces*i))*actual_radius+mid.x
                y = math.sin(math.radians(360/pieces*i))*actual_radius+mid.y
                actual_point = spy.Point(x,y)

                #check if the point is inside the map
                #if not, ignore the point
#                if not map_hull.contains(actual_point):
#                    actual_point = spy.LineString([mid,actual_point]).intersection(map_hull.boundary)

                #find the closest node to the point
                actual_node = self._nearest_node(actual_point)

                if(i==0):
                    first_node = actual_node

                #find path from actual node to center
                #if(actual_node is not None and central_node is not None):
                #    self._add_path(actual_node, central_node, astar=True)

                #find path from node to previous node; if do not have previous, ignore;
                if(actual_node is not None and previous_node is not None):
                    self._add_path(actual_node, previous_node, astar=True)

                #if it is the last one, find path to the first node
                if(i==(pieces-1) and actual_node is not None and first_node is not None):
                    self._add_path(actual_node, first_node, astar=True)

                #store previous node for the next iteration
                previous_node = actual_node
                gc.collect()
            gc.collect()
        #change the color for the main path
        self._highlight_path("#000099", 2.0)


