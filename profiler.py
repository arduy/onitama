import onitama as oni
import timeit
import sys
from ai import AI
import ai2

game = oni.Game(start_cards=oni.ALL_CARDS[0:5])
ai = AI()
ai.set_game_as_root(game)
ai2 = ai2.AI()
ai2.set_game_as_root(game)
depth = int(sys.argv[1])

def compute():
    ai.mock_search(depth=depth)

def compute2():
    ai2.mock_search(depth=depth)

time = timeit.timeit(stmt=compute, number=1)
print('{} seconds'.format(time))

time2 = timeit.timeit(stmt=compute2, number=1)
print('{} seconds'.format(time2))


nodes = 0
nodes2 = 0
for i in range(depth+1):
    nodes += len(ai.get_nodes(i))
    nodes2 += len(ai2.get_nodes(i))
print('{} nodes'.format(nodes))
print('{} kilonodes/s'.format(nodes/time/1000))

print('{} nodes'.format(nodes2))
print('{} kilonodes/s'.format(nodes2/time2/1000))
