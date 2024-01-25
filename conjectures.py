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
                        key=lambda x: len(G.closed_out_neighborhood(x)),
                        default=0)
        subset_outsizes[k] = vertices

    # Joe's conjecture that ball minimizes neighborhood size
    joe_conj = True
    for r in range(1, 2*(r-1)):
        hamming_ball = G.hamming_ball(r)
        if len(G.closed_out_neighborhood(hamming_ball)) > len(G.closed_out_neighborhood(subset_outsizes[len(hamming_ball)])):
            joe_conj = False
            break        
    print(f'Joe\'s bold conjecture: {joe_conj}')
    if not joe_conj:
        print(f'Counterexample\n'
              f'--------------\n'
              f'Hamming ball vertices: {hamming_ball}\n'
              f'Hamming ball closed out-neighborhood: {G.closed_out_neighborhood(hamming_ball).keys()}'
              f'Hamming ball neighborhoods size: {len(G.closed_out_neighborhood(hamming_ball))}\n'
              f'Subset vertices: {subset_outsizes[len(hamming_ball)]}\n'
              f'Subset closed out-neighborhood: {G.closed_out_neighborhood(subset_outsizes[len(hamming_ball)]).keys()}'
              f'Subset neighborhood size: {len(G.closed_out_neighborhood(subset_outsizes[len(hamming_ball)]))}')
    for k, subset in subset_outsizes.items():
        print(f'{k=}: {subset}')
    # G.plot_graph()
    plt.title('Min Size of (Closed) Out-Neighborhoods')
    plt.xlabel('Size of Subset')
    plt.ylabel('Min Size of (Closed) Out-Neighborhood')
    plt.bar(subset_outsizes.keys(), [len(G.closed_out_neighborhood(subset)) for subset in subset_outsizes.values()])
    plt.xticks(list(subset_outsizes.keys()))
    # plt.savefig(Path(__file__).parent/ 'plots' / f'closed_r-{r}')
    # plt.show()


if __name__ == '__main__':
    main()