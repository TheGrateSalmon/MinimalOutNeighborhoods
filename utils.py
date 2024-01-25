import functools as ft
import itertools as it

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class TropicalMatrix:
    def __init__(self, data: np.ndarray):
        self._data = data

    def __repr__(self):
        return self._data.__repr__()

    def __getitem__(self, idx):
        submatrix = TropicalMatrix(self._data[idx])
        if not submatrix.shape:
            return submatrix._data.item()
        return TropicalMatrix(submatrix)

    def __add__(self, other):
        if self.shape != other.shape:
            raise ValueError(f'operands could not be broadcast together with shapes {self.shape} {other.shape}')  
        return TropicalMatrix(np.minimum(self._data, other._data))

    def __radd__(self, other):
        return self.__add__(other)

    def __matmul__(self, other):
        prod_matrix = np.empty(shape=(self.shape[0], other.shape[1]))
        for i, j in it.product(range(self.shape[0]), range(other.shape[1])):
            prod_matrix[i, j] = np.min(self._data[i, :] + other._data[:, j])
        return TropicalMatrix(prod_matrix)

    def __rmatmul__(self, other):
        return other.__matmult__(self)
    
    def __pow__(self, n: int):
        if not isinstance(n, int):
            raise TypeError(f'{n} must be an integer.')
        if n < 0:
            raise ValueError(f'{n} must be nonnegative.')
        # NOTE: Taken from NumPy's matrix power function for convenenience.
        # Use binary decomposition to reduce the number of matrix multiplications.
        # Here, we iterate over the bits of n, from LSB to MSB, raise `a` to
        # increasing powers of 2, and multiply into the result as needed.
        z = result = None
        while n > 0:
            z = self if z is None else z @ z
            n, bit = divmod(n, 2)
            if bit:
                result = z if result is None else result @ z
        return result

    @property
    def shape(self):
        return self._data.shape


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
        if not isinstance(r, int):
            raise TypeError(f'{r} must be an integer.')
        if r < 0:
            raise ValueError(f'{r} must be a nonnegative integer.')
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
        return set(ft.reduce(lambda neighborhood, node: neighborhood | dict(self[node]), nodes, {}).keys()) | set(nodes)
        
    def open_out_neighborhood(self, nodes):
        neighborhood = self.closed_out_neighborhood(nodes)
        for node in nodes: neighborhood.pop(node, None)
        return set(neighborhood.keys())

    def hamming_ball(self, r: int):
        """Constructs the Hamming ball of radius n centered at the origin.
        
        The Hamming ball of radius n centered at the origin consists of all 
        vertices which are reachable with a (directed) path of length <= n from
        the origin.

        Yields a warning if the radius exceeds the size of the grid.

        Parameters
        ----------
        r : int
            The radius of the Hamming ball
        """
        if not isinstance(r, int):
            raise TypeError(f'{r} must be an integer.')
        if r < 0:
            raise ValueError(f'{r} must be a nonnegative integer.')
        if r > 2*self.r + 1:
            raise ValueError(f'{r} is too large! Valid range: 1 <= r <= {2*self.r + 1}.')
        # use tropical arithmetic to figure out if there is a walk of length <= r
        # by computing tropical matrix powers
        adj_matrix = nx.adjacency_matrix(self).toarray().astype(float)
        adj_matrix[adj_matrix == 0] = np.inf
        np.fill_diagonal(adj_matrix, 0)
        walks_matrix = TropicalMatrix(adj_matrix)**r
        origin_idx = list(self.nodes()).index((0,0))
        return {(0,0)} | {vertex for idx, vertex in enumerate(self.nodes()) if walks_matrix[origin_idx, idx] < np.inf}

    def plot_graph(self, **kwargs):
        pos = {node: node for node in self.nodes}
        plt.figure(figsize=(8, 8))
        nx.draw(self, pos, with_labels=True, node_size=750, font_size=8, **kwargs)
        plt.show()