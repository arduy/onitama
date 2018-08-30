from tkinter import *
from PIL import ImageTk, Image
from math import floor
import onitama as oni
from ai import create_ai

class GUI():
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
        self.status_label.pack(side=BOTTOM)
        self.top_frame.pack(side=TOP, fill='x')
        self.bottom_frame.pack(side=BOTTOM, fill='x')
        self.analysis_label.pack(side=LEFT, padx=10, pady=10)
        self.center_frame.pack(side=BOTTOM)
        self.card_canvas.pack(side=LEFT, padx=self.padding, pady=self.padding)
        self.card_canvas.bind('<Button-1>', self.card_click)
        self.board_canvas.pack(side=LEFT, padx=self.padding, pady=self.padding)
        self.board_canvas.bind('<Button-1>', self.board_click)
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


    def set_game(self, game, user):
        self.game = game
        self.user = user
        self.card_names = [card.name() for card in game.start_cards]
        self.ai.set_game_as_root(game)
        self.update()

    def update(self):
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
        for col in range(self.columns):
            for row in range(self.rows):
                if blue_home(row, col):
                    color = '#b3e0ff'
                elif red_home(row, col):
                    color = '#ffcccc'
                else:
                    color = colors[(col+row)%2]
                coord_tag = '{},{}'.format(str(col),str(4-row))
                self.board_canvas.create_rectangle(
                    col*self.square_size+self.inset,
                    row*self.square_size+self.inset,
                    (col+1)*self.square_size+self.inset,
                    (row+1)*self.square_size+self.inset,
                    width=2,
                    fill=color,
                    tags=(coord_tag,color)
                )

    def draw_pieces(self, pieces):
        def coordinate(i):
            if self.flip:
                col = i % 5
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
            (self.inset + self.card_size/2, self.board_size/2 - self.card_size/2),
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
            if i >= 2:
                self.card_canvas.create_text(
                    c[0]+self.card_size/2,
                    c[1],
                    text=cards[i].name(),
                    anchor='s',
                    tags=('card',)
                )
            else:
                self.card_canvas.create_text(
                    c[0]+self.card_size/2,
                    c[1]+self.card_size,
                    text=cards[i].name(),
                    anchor='n',
                    tags=('card',)
                )


    def draw_card(self, x, y, card, player):
        unit = self.card_size/5
        if self.flip:
            squares = [(c[0]+2, c[1]+2) for c in card.moves[player.other()]]
        else:
            squares = [(c[0]+2, c[1]+2) for c in card.moves[player]]
        for col in range(5):
            for row in range(5):
                if (col, row) == (2,2):
                    color = '#80ff80'
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

    def board_click(self, event):
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        coord = (floor(x/self.square_size), 4 - floor(y/self.square_size))
        self.select_square(coord)

    def card_click(self, event):
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

    def highlight_square(self, coordinate, color):
        coord_tag = '{},{}'.format(str(coordinate[0]), str(coordinate[1]))
        item = self.board_canvas.find_withtag(coord_tag)
        tags = self.board_canvas.gettags(item)[0:2]
        self.board_canvas.itemconfig(item, fill=color, tags=tags+('highlight',))

    def highlight_targets(self):
        if self.selected is not None:
            legal_targets = [
                target
                for moves in self.game.legal_moves().values()
                for target in moves.get(self.selected)
            ]
            for target in self.game.legal_move_targets(self.selected):
                self.highlight_square(target, 'yellow')

    def undo_highlights(self):
        highlighted = self.board_canvas.find_withtag('highlight')
        for item in highlighted:
            tags = self.board_canvas.gettags(item)[0:2]
            old_color = tags[1]
            self.board_canvas.itemconfig(item, fill=old_color)

    def select_square(self, coordinate):
        if self.selected is None:
            if coordinate in self.game.legal_move_starts():
                self.selected = coordinate
                self.highlight_square(coordinate, '#80ff80')
                self.highlight_targets()
        elif self.target is None:
            if coordinate in self.game.legal_move_targets(self.selected):
                self.target = coordinate
                card_choices = self.game.get_card_choices_for_move(self.selected, self.target)
                if len(card_choices) == 2:
                    # Player needs to choose a card
                    self.highlight_square(coordinate, 'red')
                    self.status_label.config(text='Choose a card')
                else:
                    self.select_card(card_choices[0].name())
            elif coordinate == self.selected:
                self.undo_highlights()
                self.selected = None
            elif coordinate in self.game.legal_move_starts():
                self.undo_highlights()
                self.selected = coordinate
                self.highlight_square(coordinate, '#80ff80')
                self.highlight_targets()
            else:
                self.undo_highlights()
                self.selected = None

    def select_card(self, card_name):
        if self.selected is not None and self.target is not None:
            card = oni.NAME_TO_CARD[card_name]
            if card in self.game.cards[self.game.active_player]:
                move = oni.Move(
                    player=self.game.active_player,
                    start=self.selected,
                    end=self.target,
                    card=oni.NAME_TO_CARD[card_name],
                )
            else:
                # Bad card selection
                return
            try:
                self.game.do_move(move)
                self.undo_highlights()
                # highlight most recent move
                self.highlight_square(self.selected, self.lightgreen)
                self.highlight_square(self.target, self.lightgreen)
            except oni.IllegalMoveError:
                print('Illegal move')
                self.undo_highlights()
            self.selected, self.target = None, None
            self.update()
            self.do_ai_move(4)

    def do_ai_move(self, depth):
        self.ai.set_game_as_root(self.game)
        move = self.ai.find_move(depth)
        onimove = self.ai.create_game_move(move)
        try:
            self.game.do_move(onimove)
        except Exception:
            print('Illegal move')
        self.update()

def main():
    root = Tk()
    root.title('Board')
    gui = GUI(root)
    game = oni.Game(oni.ALL_CARDS[1:6])
    gui.set_game(game, oni.Player.RED)
    gui.update_analysis("Show analysis here\n1 ...\n2 ...\n3 ...")
    root.mainloop()

if __name__ == '__main__':
    main()
