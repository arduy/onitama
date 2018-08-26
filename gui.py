from tkinter import *
from PIL import ImageTk, Image
from math import floor
import onitama as oni

class GUI():
    rows = 5
    columns = 5
    square_size = 100
    inset = 5
    dark = '#f5deb3'
    light = '#ffffe0'
    piece_names = ['redpawn', 'bluepawn', 'redking', 'blueking']
    card_size = 110
    board_size = 5*square_size+2*inset
    def __init__(self, parent, flip=False):
        self.parent = parent
        self.flip = flip
        self.board_canvas = Canvas(
            parent,
            width=self.board_size,
            height=self.board_size,
        )
        self.card_canvas = Canvas(
            parent,
            width=self.card_size*2+3*self.inset,
            height=self.board_size,
        )
        self.card_canvas.pack(side=LEFT, padx=10, pady=10)
        self.card_canvas.bind('<Button-1>', self.card_click)
        self.board_canvas.pack(side=LEFT, padx=10, pady=10)
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

    def set_game(self, game):
        self.game = game
        self.card_names = [card.name() for card in game.start_cards]
        self.update()

    def update(self):
        self.draw_pieces(self.game.board.array)
        self.draw_cards(
            red=self.game.cards[oni.Player.RED],
            blue=self.game.cards[oni.Player.BLUE],
            neutral=self.game.neutral_card
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
                self.board_canvas.create_rectangle(
                    col*self.square_size+self.inset,
                    row*self.square_size+self.inset,
                    (col+1)*self.square_size+self.inset,
                    (row+1)*self.square_size+self.inset,
                    width=2,
                    fill=color
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
                    anchor='s'
                )
            else:
                self.card_canvas.create_text(
                    c[0]+self.card_size/2,
                    c[1]+self.card_size,
                    text=cards[i].name(),
                    anchor='n'
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
                    color = 'darkgrey'
                elif (col, 4-row) in squares:
                    color = '#80ff80'
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
        print('clicked square: ({},{})'.format(floor(x/self.square_size),4 - floor(y/self.square_size)))

    def card_click(self, event):
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        try:
            item = canvas.find_overlapping(x+0,y+0,x+1,y+1)[0]
        except IndexError:
            print('clicked empty')
            return
        tags = canvas.gettags(item)
        card_name = None
        for tag in tags:
            if tag in self.card_names:
                card_name = tag
                break
        if card_name is not None:
            print('clicked card: {}'.format(card_name))
        else:
            print('no card found')


def main():
    root = Tk()
    root.title('Board')
    gui = GUI(root,flip=False)
    game = oni.Game(oni.ALL_CARDS[0:5])
    gui.set_game(game)
    root.mainloop()

if __name__ == '__main__':
    main()
