import Heuristic
import graph_tool.all as gt
import sympy as sym
import shapely.geometry as spy
import time

class Fishbone(Heuristic.Heuristic):
    def __init__(self,path,doNotInit=False):
        super(Fishbone,self).__init__(path,doNotInit)
        self.g.ep.line_distance = self.g.new_edge_property("float")

    def _slice_line(self, point1, point2, n_slices):
        line_distance = spy.LineString([point1,point2])
        splitter_points = spy.MultiPoint([line_distance.interpolate((float(i)/n_slices),
                    normalized=True) for i in range(1, n_slices)])
        return splitter_points


    def _add_path_area(self, start, end):
        source_point = spy.Point(self.g.vp.lon[start],self.g.vp.lat[start])
        target_point = spy.Point(self.g.vp.lon[end],self.g.vp.lat[end])
        main_line = spy.LineString([source_point,target_point])
        for e in self.g.edges():
            p1 = spy.Point(self.g.vp.lon[e.source()],self.g.vp.lat[e.source()])
            p2 = spy.Point(self.g.vp.lon[e.target()],self.g.vp.lat[e.target()])
            line = spy.LineString([p1,p2])
            self.g.ep.line_distance[e] = line.hausdorff_distance(main_line)

        nodes, edges = gt.shortest_path(self.g,start,end,
                negative_weights=False,weights=self.g.ep.line_distance)
        self._nodes += nodes
        self._edges += edges


    def _getThresholds(self):
        #will return [min_lon, min_lat], [max_lon, max_lat], [mid_lon, mid_lat]
        positions = {'min_lon':float("inf"), 'min_lat':float("inf"),'max_lon':
                     float("-inf"), 'max_lat':float("-inf"), 'mid_lon':0,
                     'mid_lat': 0}
        for v in self.g.vertices():
            if positions['min_lon'] > self.g.vp.lon[v]:
                positions['min_lon'] = self.g.vp.lon[v]

            if positions['min_lat'] > self.g.vp.lat[v]:
                positions['min_lat'] = self.g.vp.lat[v]

            if positions['max_lon'] < self.g.vp.lon[v]:
                positions['max_lon'] = self.g.vp.lon[v]

            if positions['max_lat'] < self.g.vp.lat[v]:
                positions['max_lat'] = self.g.vp.lat[v]

        positions['mid_lon'] = (positions['min_lon']+positions['max_lon'])/2
        positions['mid_lat'] = (positions['min_lat']+positions['max_lat'])/2

        return positions
#    def _most_distant_points(self, multipoint):
#        centroid = multipoint.centroid
#        dist1 = dist2 = 0
#        point1 = None
#        point2 = None
#        for point in multipoint:
#            distance = centroid.distance(point)
#            if distance >= dist2:
#                dist2 = dist1
#                point2 = point1
#                dist1 = distance
#                point1 = point
#        return point1, point2

    #overrides
    def execute(self):
        self.execute(5)

    def execute(self, n_slices):
        #find the most distant points using diameter
        dist, ends = gt.pseudo_diameter(self.g, weights=self.g.ep.distance)
        #find the bwetweenness, using<F9> the distance as weight
        central_node = self._central_bt_node()
        #find the shortest path from the border points to the center
        self._add_path(ends[0], central_node, astar=True)
        self._add_path(central_node, ends[1], astar=True)
        main_path = list(self._nodes)
        #divide the path in N parts
        p1 = spy.Point(self.g.vp.lon[ends[0]],self.g.vp.lat[ends[0]])
        p2 = spy.Point(self.g.vp.lon[ends[1]],self.g.vp.lat[ends[1]])
        slices = self._slice_line(p1,p2,n_slices)

        #add the lines to a list, for future drawing it
        #self._add_edge(p1,p2)

        for point in slices:
            #use sym to find perpendicular lines
            sp1 = sym.Point(p1.x,p1.y)
            sp2 = sym.Point(p2.x,p2.y)
            sline_distance = sym.Line(sp1,sp2)
            #find the splitter points in the main line
            sp3 = sym.Point(point.x, point.y)
            sline_perp = sline_distance.perpendicular_line(sp3)
            #convert to shapely
            latlon = self._getThresholds()
            a,b,c = sline_perp.coefficients
            minx = latlon['min_lon']
            miny = (-a*minx-c)/b
            maxx = latlon['max_lon']
            maxy = (-a*maxx-c)/b
            line_perp = spy.LineString([spy.Point(minx,miny),spy.Point(maxx,maxy)])

            short_distance = float("inf")
            p3 = spy.Point(point.x, point.y)
            n_center = self._nearest_node(p3, main_path)
            #find the node in the border of the map, perpendicular to the main line
            border_node = None
            t = time.time()
            intersection_points = list()
            for e in self.g.edges():
                pseg1 = spy.Point(self.g.vp.lon[e.source()],self.g.vp.lat[e.source()])
                pseg2 = spy.Point(self.g.vp.lon[e.target()],self.g.vp.lat[e.target()])
                seg = spy.LineString([pseg1,pseg2])
                if seg.intersects(line_perp):
                    intersection = seg.intersection(line_perp)
                    intersection_points.append(intersection)
            multipoint = spy.MultiPoint(intersection_points)
            distant_point1, distant_point2 = self._most_distant_points(multipoint)
            distant_node1 = self._nearest_node(distant_point1)
            distant_node2 = self._nearest_node(distant_point2)
            #add the lines to a list, for future drawing it
            #self._add_edge(distant_point1,distant_point2)
            if distant_node1 is not None and n_center is not None and distant_node2 is not None:
                self._add_path(n_center,distant_node1, astar=True)
                self._add_path(n_center,distant_node2, astar=True)

        #change the color for the main path
        self._highlight_path("#a40000", 3.0)

