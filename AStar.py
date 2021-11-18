import graph_tool.all as gt
import shapely.geometry as spy
import math

class Visitor(gt.AStarVisitor):

    def __init__(self, touched_v, touched_e, target):
        self.touched_v = touched_v
        self.touched_e = touched_e
        self.target = target

    def discover_vertex(self, u):
        self.touched_v[u] = True

    def examine_edge(self, e):
        self.touched_e[e] = True

    def edge_relaxed(self, e):
        if e.target() == self.target:
            raise gt.StopSearch()

class AStar(object):
    def __init__(self, g):
        self.g = g

#    def h(self, source, target):
#        p1 = spy.Point(self.g.vp.lon[source],self.g.vp.lat[source])
#        p2 = spy.Point(self.g.vp.lon[target],self.g.vp.lat[target])
#        return p1.distance(p2)
    def h(self, source,target, main_line):
        p1 = spy.Point(self.g.vp.lon[source],self.g.vp.lat[source])
        p2 = spy.Point(self.g.vp.lon[target],self.g.vp.lat[target])
        base1 = p1.distance(main_line)
        base2 = p2.distance(main_line)
        a = p1.distance(p2)
        b = math.fabs(base1-base2)
        c = math.sqrt(math.pow(a,2)-math.pow(b,2))
        area = ((base1+base2)*c)/2.0
        return area

        #return float(float(main_line.distance(p1))+float(main_line.distance(p2)))/2.0

    def path(self,source, target):
        source_point = spy.Point(self.g.vp.lon[source],self.g.vp.lat[source])
        target_point = spy.Point(self.g.vp.lon[target],self.g.vp.lat[target])
        main_line = spy.LineString([source_point,target_point])
        self.g.ep.line_distance = self.g.new_edge_property("float")
        for e in self.g.edges():
            p1 = spy.Point(self.g.vp.lon[e.source()],self.g.vp.lat[e.source()])
            p2 = spy.Point(self.g.vp.lon[e.target()],self.g.vp.lat[e.target()])

            base1 = p1.distance(main_line)
            base2 = p2.distance(main_line)
            a = p1.distance(p2)
            b = math.fabs(base1-base2)
            c2 = math.pow(a,2)-math.pow(b,2)
            if(c2 > 0):
                c = math.sqrt(c2)
            else:
                c = 0
            area = ((base1+base2)*c)/2.0
            #line = spy.LineString([p1,p2])
            self.g.ep.line_distance[e] = area #main_line.distance(line)
        touch_v = self.g.new_vertex_property("bool")
        touch_e = self.g.new_edge_property("bool")
        dist, pred = gt.astar_search(self.g, source, weight=self.g.ep.line_distance,
                        visitor=Visitor(touch_v, touch_e, target),
                        heuristic=lambda v: self.h(v,target, main_line))
        it = target
        while it != source:
            p = self.g.vertex(pred[it])
            for e in it.all_edges():
                if e.target() == p:
                    break
            yield p,e
            it = p
