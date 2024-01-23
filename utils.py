import functools as ft
import itertools as it

import matplotlib.pyplot as plt
import networkx as nx


class FLattice(nx.DiGraph):
    def __init__(self, r: int):
        """Constructs the special graph on a grid of radius r.
        
        Constructs the special graph on a grid of radius r, i.e., consisting of all
        vertices (x, y) with max(x, y) <= r. This is a square of length 2r, or with
        2r+1 vertices per edge.

        A grid of radius r consists of (r+3)^2 points.

        WARNING: The resulting graph does NOT contain all of the edges on the 
        boundary of the grid, so the neighborhood of boundary vertices is NOT 
        correct! In other words, only vertices (x, y) with max(x, y) <= are 
        correct and include all of their neighbors.

        Parameters
        ----------
        r : int
            the radius of the grid
        """
        super(FLattice, self).__init__()
        self.r = r
        
        for (x, y) in it.product(range(r+1), repeat=2):
            # outside of grid limits 
            if max(abs(x), abs(y)) > self.r:
                continue
            if (x + y) % 2 == 0:
                self.add_edges_from([((x,y), (x+1,y)),
                                     ((x,y), (x-1,y)),
                                     ((x,-y), (x+1,-y)),
                                     ((x,-y), (x-1,-y)),
                                     ((-x,y), (-x+1,y)),
                                     ((-x,y), (-x-1,y)),
                                     ((-x,-y), (-x+1,-y)),
                                     ((-x,-y), (-x-1,-y))])
            else:
                self.add_edges_from([((x,y), (x,y+1)),
                                     ((x,y), (x,y-1)),
                                     ((x,-y), (x,-y+1)),
                                     ((x,-y), (x,-y-1)),
                                     ((-x,y), (-x,y+1)),
                                     ((-x,y), (-x,y-1)),
                                     ((-x,-y), (-x,-y+1)),
                                     ((-x,-y), (-x,-y-1))])
    
    @ft.cached_property
    def valid_nodes(self):
        return [node for node in self.nodes if max(abs(node[0]), abs(node[1])) <= self.r]

    def closed_out_neighborhood(self, nodes):
        if not nodes:
            return {}
        return ft.reduce(lambda neighborhood, node: neighborhood | dict(self[node]), nodes, {})
        
    def open_out_neighborhood(self, nodes):
        neighborhood = self.closed_out_neighborhood(nodes)
        for node in nodes: neighborhood.pop(node, None)
        return neighborhood 

    def plot_graph(self, **kwargs):
        pos = {node: node for node in self.nodes}
        plt.figure(figsize=(8, 8))
        nx.draw(self, pos, with_labels=True, node_size=750, font_size=8, **kwargs)
        plt.show()