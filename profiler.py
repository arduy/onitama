import onitama as oni
import timeit
import sys
import ai

game = oni.Game(start_cards=oni.ALL_CARDS[0:5])
ai_copy = ai.create_ai('copy', game)
ai_unmove = ai.create_ai('unmove', game)
depth = int(sys.argv[1])

def compute():
    ai_copy.mock_search(depth=depth, mode=sys.argv[2])

def compute2():
    ai_unmove.mock_search(depth=depth)

time = timeit.timeit(stmt=compute, number=1)
print('{} seconds'.format(time))

time2 = timeit.timeit(stmt=compute2, number=1)
print('{} seconds'.format(time2))


nodes = 0
nodes2 = 0
for i in range(depth+1):
    nodes += len(ai_copy.get_nodes(i))
    nodes2 += len(ai_unmove.get_nodes(i))
print('{} nodes'.format(nodes))
print('{} kilonodes/s'.format(nodes/time/1000))

print('{} nodes'.format(nodes2))
print('{} kilonodes/s'.format(nodes2/time2/1000))
