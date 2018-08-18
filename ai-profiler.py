import onitama as oni
import timeit
import sys
from ai import AI

game = oni.Game(start_cards=oni.ALL_CARDS[0:5])
ai = AI(game=game)
depth = int(sys.argv[1])

def compute():
    ai.generate_search_space(depth=depth)

time = timeit.timeit(stmt=compute, number=1)
print('{} seconds'.format(time))

# print(sum(map(lambda x: sys.getsizeof(x), ai.get_nodes(depth=depth))))

nodes = 0
for i in range(depth+1):
    nodes += len(ai.get_nodes(i))
print('{} nodes'.format(nodes))
print('{} kilonodes/s'.format(nodes/time/1000))
