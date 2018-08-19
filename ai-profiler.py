import onitama as oni
import timeit
import sys
import ai
import ai_alt

game = oni.Game(start_cards=oni.ALL_CARDS[0:5])
ai = ai.AI(game=game)
alt_ai = ai_alt.AI(game=game)
depth = int(sys.argv[1])

def compute():
    ai.generate_search_space(depth=depth)

def compute_alt():
    alt_ai.generate_search_space(depth=depth)

time = timeit.timeit(stmt=compute, number=1)
alt_time = timeit.timeit(stmt=compute_alt, number=1)
print('AI: {} seconds'.format(time))
print('Alt: {} seconds'.format(alt_time))


# print(sum(map(lambda x: sys.getsizeof(x), ai.get_nodes(depth=depth))))

nodes = 0
for i in range(depth+1):
    nodes += len(ai.get_nodes(i))
alt_nodes = 0
for i in range(depth+1):
    alt_nodes += len(alt_ai.get_nodes(i))

print('AI stats:')
print('{} nodes'.format(nodes))
print('{} kilonodes/s'.format(nodes/time/1000))

print('\nAlternate AI stats:')
print('{} nodes'.format(alt_nodes))
print('{} kilonodes/s'.format(alt_nodes/alt_time/1000))
