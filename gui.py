from tkinter import *
from PIL import ImageTk, Image
from math import floor
import onitama as oni
from ai import create_ai
from collections import defaultdict
import random

class GUI:
    rows = 5
    columns = 5
    square_size = 100
    inset = 5
    dark = '#f5deb3'
    light = '#ffffe0'
    blue = '#33adff'
    red = '#ff4d4d'
    green = '#80ff80'
    lightgreen = '#ccffcc'
    piece_names = ['redpawn', 'bluepawn', 'redking', 'blueking']
    card_size = 110
    board_size = 5*square_size+2*inset
    padding = 10
    card_canvas_width = card_size*2+3*inset
    card_canvas_height = board_size
    center_frame_width = board_size + card_canvas_width + 4*padding
    center_frame_height = board_size + padding*2
    def __init__(self, parent, flip=False):
        self.parent = parent
        self.flip = flip
        self.center_frame = Frame(
            parent,
            width=self.center_frame_width,
            height=self.center_frame_height,
        )
        self.board_canvas = Canvas(
            self.center_frame,
            width=self.board_size,
            height=self.board_size,
        )
        self.card_canvas = Canvas(
            self.center_frame,
            width=self.card_size*2+3*self.inset,
            height=self.board_size,
        )
        self.top_frame = Frame(
            parent,
        )
        self.status_label = Label(
            self.top_frame,
            text="Welcome",
        )
        self.bottom_frame = Frame(
            parent,
        )
        self.analysis_label = Label(
            self.bottom_frame,
            justify='left',
        )
        self.menubar = Menu(parent)
        self.menubar.add_command(label="New Game", command=self.new_game)
        self.menubar.add_command(label="Flip Board", command=self.flip_board)
        self.parent.config(menu=self.menubar)
        self.status_label.pack(side=BOTTOM)
        self.top_frame.pack(side=TOP, fill='x')
        self.bottom_frame.pack(side=BOTTOM, fill='x')
        self.analysis_label.pack(side=LEFT, padx=10, pady=10)
        self.center_frame.pack(side=BOTTOM)
        self.card_canvas.pack(side=LEFT, padx=self.padding, pady=self.padding)
        self.card_canvas.bind('<Button-1>', self.card_click)
        self.board_canvas.pack(side=LEFT, padx=self.padding, pady=self.padding)
        self.board_canvas.bind('<Button-1>', self.board_click)
        self.highlights = HighlightManager()
        self.draw_board()
        images = {
            name: Image.open('./pieces/{}.png'.format(name)).resize((self.square_size, self.square_size), Image.ANTIALIAS)
            for name in self.piece_names
        }
        self.images = {
            name: ImageTk.PhotoImage(image)
            for name, image in images.items()
        }
        self.selected = None
        self.target = None
        self.ai = create_ai()
        self.ai_depth = 4
        self.ai_wait = 20
        self.new_game()

    def new_game(self):
        cards = random.sample(oni.ALL_CARDS, 5)
        game = oni.Game(cards)
        self.set_game(game=game, user=oni.Player.RED)

    def set_game(self, game, user):
        self.game = game
        self.user = user
        self.card_names = [card.name() for card in game.start_cards]
        self.undo_highlights('all')
        self.update()
        if not self.game.active_player is self.user:
            self.parent.after(self.ai_wait, self.do_ai_move)

    def flip_board(self):
        self.flip = not self.flip

        self.update()

    def update(self):
        self.draw_board()
        self.draw_pieces(self.game.board.array)
        self.draw_cards(
            red=self.game.cards[oni.Player.RED],
            blue=self.game.cards[oni.Player.BLUE],
            neutral=self.game.neutral_card
        )
        self.update_status()

    def update_status(self):
        if self.game.check_victory() is None:
            if self.game.active_player == oni.Player.RED:
                self.status_label.config(
                    text='Red to move',
                    fg=self.red,
                )
            elif self.game.active_player == oni.Player.BLUE:
                self.status_label.config(
                    text='Blue to move',
                    fg=self.blue,
                )
        else:
            winner = 'Red' if self.game.check_victory() == oni.Player.RED else 'Blue'
            color = self.red if winner == 'Red' else self.blue
            self.status_label.config(
                text='{} wins'.format(winner),
                fg=color
            )

    def update_analysis(self, text):
        self.analysis_label.config(
            text=text,
        )

    def draw_board(self):
        def red_home(row, col):
            if self.flip:
                return row == 0 and col == 2
            else:
                return row == 4 and col == 2
        def blue_home(row, col):
            if self.flip:
                return row == 4 and col == 2
            else:
                return row == 0 and col == 2
        colors = [self.dark, self.light]
        self.board_canvas.delete('square')
        for col in range(self.columns):
            for row in range(self.rows):
                if blue_home(row, col):
                    color = '#b3e0ff'
                elif red_home(row, col):
                    color = '#ffcccc'
                else:
                    color = colors[(col+row)%2]
                if self.flip:
                    coord = 4-col, row
                    coord_tag = '{},{}'.format(coord[0],coord[1])
                else:
                    coord = col, 4-row
                    coord_tag = '{},{}'.format(coord[0],coord[1])
                rect = self.board_canvas.create_rectangle(
                    col*self.square_size+self.inset,
                    row*self.square_size+self.inset,
                    (col+1)*self.square_size+self.inset,
                    (row+1)*self.square_size+self.inset,
                    width=2,
                    fill=color,
                    tags=(coord_tag,color,'square')
                )
                if self.highlights.get_color(coord) is not None:
                    self.board_canvas.itemconfig(rect,fill=self.highlights.get_color(coord))

    def draw_pieces(self, pieces):
        def coordinate(i):
            if self.flip:
                col = 4 - (i % 5)
                row = i // 5
                return (col*self.square_size+self.inset, row*self.square_size+self.inset)
            else:
                col = i % 5
                row = 4 - (i // 5)
                return (col*self.square_size+self.inset, row*self.square_size+self.inset)
        self.board_canvas.delete('piece')
        for i, piece in enumerate(pieces):
            if piece.name() != 'empty':
                self.board_canvas.create_image(
                    coordinate(i),
                    anchor='nw',
                    image=self.images[piece.name()],
                    tags=('piece', piece.name())
                )

    def draw_cards(self, red, blue, neutral):
        self.card_canvas.delete('card')
        coords = [
            (self.inset, self.inset),
            (self.inset*2 + self.card_size, self.inset),
            (self.card_canvas_width/2 - self.card_size/2, self.board_size/2 - self.card_size/2),
            (self.inset, self.board_size - self.card_size - self.inset),
            (self.inset*2 + self.card_size, self.board_size - self.card_size - self.inset)
        ]
        r = oni.Player.RED
        b = oni.Player.BLUE
        if self.flip:
            cards = red+[neutral]+blue
            players = [r,r,b,b,b]
        else:
            cards = blue+[neutral]+red
            players = [b,b,r,r,r]
        for i in range(5):
            c = coords[i]
            self.draw_card(c[0], c[1], cards[i], players[i])
            if cards[i] != neutral:
                color = self.red if players[i].color() == 'red' else self.blue
            else:
                color = 'black'
            if i >= 2:
                self.card_canvas.create_text(
                    c[0]+self.card_size/2,
                    c[1],
                    text=cards[i].name().upper(),
                    anchor='s',
                    fill=color,
                    tags=('card',)
                )
            else:
                self.card_canvas.create_text(
                    c[0]+self.card_size/2,
                    c[1]+self.card_size,
                    text=cards[i].name().upper(),
                    anchor='n',
                    fill=color,
                    tags=('card',)
                )

    def draw_card(self, x, y, card, player):
        unit = self.card_size/5
        if self.flip:
            squares = [(c[0]+2, c[1]+2) for c in card.moves[player.other()]]
            bot_right_corner = (0,0) if player.color() == 'red' else (4,4)
        else:
            squares = [(c[0]+2, c[1]+2) for c in card.moves[player]]
            bot_right_corner = (4,4) if player.color() == 'red' else (0,0)
        for col in range(5):
            for row in range(5):
                if (col, row) == (2,2):
                    color = self.lightgreen
                elif (col, 4-row) in squares:
                    color = 'yellow'
                else:
                    color = 'white'
                self.card_canvas.create_rectangle(
                    x+col*unit,
                    y+row*unit,
                    x+(col+1)*unit,
                    y+(row+1)*unit,
                    fill=color,
                    tags=('card', card.name())
                )
                if (col, row) == bot_right_corner:
                    gap = unit/3.0
                    self.card_canvas.create_oval(
                        x+col*unit+gap,
                        y+row*unit+gap,
                        x+(col+1)*unit-gap,
                        y+(row+1)*unit-gap,
                        fill='black'
                    )

    def board_click(self, event):
        if self.game.active_player is self.user:
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            items = canvas.find_overlapping(x,y,x+1,y+1)
            coord = None
            for item in items:
                tags = canvas.gettags(item)
                if 'square' in tags:
                    coord = tags[0]
                    break
            if coord is not None:
                coord = parse_str_coord(coord)
            self.select_square(coord)

    def card_click(self, event):
        if self.game.active_player is self.user:
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            try:
                item = canvas.find_overlapping(x+0,y+0,x+1,y+1)[0]
            except IndexError:
                return
            tags = canvas.gettags(item)
            for tag in tags:
                if tag in self.card_names:
                    self.select_card(tag)
                    break

    def highlight_square(self, coordinate, type):
        self.highlights.set(coordinate, type)
        self.update()

    def highlight_targets(self):
        if self.selected is not None:
            legal_targets = [
                target
                for moves in self.game.legal_moves().values()
                for target in moves.get(self.selected)
            ]
            for target in self.game.legal_move_targets(self.selected):
                self.highlight_square(target, 'candidate')

    def undo_highlights(self, *args):
        for arg in args:
            if arg == 'all':
                self.highlights.remove_all_types()
            else:
                self.highlights.remove_all(arg)
        self.update()

    def select_square(self, coordinate):
        if self.game.active_player is not self.user:
            return
        if self.selected is None:
            if coordinate in self.game.legal_move_sources():
                self.selected = coordinate
                self.highlight_square(coordinate, 'source')
                self.highlight_targets()
        elif self.target is None:
            if coordinate in self.game.legal_move_targets(self.selected):
                # Player has selected a target for his/her move
                # Complete move or prompt for card selection
                self.target = coordinate
                card_choices = self.game.get_card_choices_for_move(self.selected, self.target)
                if len(card_choices) == 2:
                    # Player needs to choose a card
                    self.highlight_square(coordinate, 'target')
                    self.status_label.config(text='Choose a card')
                else:
                    self.undo_highlights('source', 'candidate')
                    self.select_card(card_choices[0].name())
            elif coordinate == self.selected:
                # Unselect current selection
                self.undo_highlights('source', 'candidate')
                self.selected = None
            elif coordinate in self.game.legal_move_sources():
                # Change current selection
                self.undo_highlights('source', 'candidate')
                self.selected = coordinate
                self.highlight_square(coordinate, 'source')
                self.highlight_targets()
            else:
                # Clicked on a non move source, non target square
                self.undo_highlights('source', 'candidate')
                self.selected = None

    def select_card(self, card_name):
        if self.game.active_player is not self.user:
            return
        if self.selected is not None and self.target is not None:
            card = oni.NAME_TO_CARD[card_name]
            if card in self.game.cards[self.game.active_player]:
                self.do_game_move(self.selected, self.target, card)
                self.selected, self.target = None, None

    def do_game_move(self, source, target, card):
        move = oni.Move(
            player=self.game.active_player,
            start=source,
            end=target,
            card=card,
        )
        self.game.do_move(move)
        self.undo_highlights('all')
        self.highlight_square(source, 'previous')
        self.highlight_square(target, 'previous')
        self.update()
        if not self.game.active_player is self.user:
            self.parent.after(self.ai_wait, self.do_ai_move)

    def do_ai_move(self):
        self.ai.set_game_as_root(self.game)
        move = self.ai.find_move(self.ai_depth)
        card_name = self.ai.card_data[move.card].name
        card = oni.NAME_TO_CARD[card_name]
        start = move.start % 5, move.start // 5
        end = move.end % 5, move.end // 5
        self.do_game_move(start, end, card)

class HighlightManager:
    types = ['previous', 'source', 'candidate', 'target']
    color = {
        'previous': '#ccffcc',
        'source': '#80ff80',
        'candidate': 'yellow',
        'target': 'red',
    }
    def __init__(self):
        self.type_map = defaultdict(list)
        self.coord_map = dict()

    def remove_all_types(self):
        self.coord_map = dict()
        self.type_map = defaultdict(list)

    def remove_all(self, type):
        if type in self.types:
            all = self.type_map[type]
            for coord in all:
                try:
                    del self.coord_map[coord]
                except KeyError:
                    pass
            del self.type_map[type]

    def remove(self, coordinate):
        type = self.coord_map.get(coordinate)
        if type is not None:
            self.type_map[type].remove(coordinate)
            del self.coord_map[coordinate]

    def set(self, coordinate, type):
        if type in self.types:
            self.coord_map[coordinate] = type
            if coordinate not in self.type_map[type]:
                self.type_map[type].append(coordinate)

    def get(self, coordinate):
        return self.coord_map.get(coordinate)

    def get_all(self, type):
        return self.type_map[type]

    def get_color(self, coordinate):
        type = self.coord_map.get(coordinate)
        if type is not None:
            return self.color[type]


def parse_str_coord(coord):
    # String format: 'x,y'
    try:
        x = int(coord[0])
        y = int(coord[2])
        return (x,y)
    except:
        return None

def main():
    root = Tk()
    root.title('Onitama')
    gui = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
