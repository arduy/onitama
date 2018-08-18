import onitama as oni
import timeit
import sys
from ai import AI

game = oni.Game(start_cards=oni.ALL_CARDS[0:5])
ai = AI(game=game)
depth = int(sys.argv[1])

def compute():
    ai.generate_search_space(depth=depth)

print(timeit.timeit(stmt=compute, number=1))

print(sum(map(lambda x: sys.getsizeof(x), ai.get_nodes(depth=depth))))
print(len(ai.get_nodes(depth=depth)))
