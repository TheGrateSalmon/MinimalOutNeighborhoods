import itertools as it
from pathlib import Path

import matplotlib.pyplot as plt
plt.style.use('ggplot')

from utils import FLattice


def main():
    r = 1
    G = FLattice(r)

    # find minimum size out-neighbor set for each k
    subset_outsizes = {}
    for k in range(len(G.valid_nodes)+1):
        vertices = min((subset for subset in it.combinations(G.valid_nodes, r=k)), 
                        key=lambda x: len(G.open_out_neighborhood(x)),
                        default=0)
        subset_outsizes[k] = vertices

    # Joe's conjecture that ball minimizes neighborhood size
    hamming_ball = [(0,0), (1,0), (-1,0), (-1,1), (1,1), (1,-1), (-1,-1)]
    joe_conj = len(G.open_out_neighborhood(hamming_ball)) <= len(G.open_out_neighborhood(subset_outsizes[len(hamming_ball)]))
    print(f'Joe\'s bold conjecture: {joe_conj}')
    
    # G.plot_graph()
    plt.title('Minimum Size of Neighborhoods vs Subset Size')
    plt.xlabel('Size of Subset')
    plt.ylabel('Minimum Size of Neighborhood')
    plt.bar(subset_outsizes.keys(), [len(G.open_out_neighborhood(subset)) for subset in subset_outsizes.values()])
    plt.xticks(list(subset_outsizes.keys()))
    plt.savefig(Path(__file__).parent/ 'plots' / f'r-{r}')
    plt.show()


if __name__ == '__main__':
    main()