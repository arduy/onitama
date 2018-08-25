from tkinter import *
from PIL import ImageTk, Image
import onitama as oni

class GUI():
    rows = 5
    columns = 5
    square_size = 100
    offset = 5
    dark = '#f5deb3'
    light = '#ffffe0'
    piece_names = ['redpawn', 'bluepawn', 'redking', 'blueking']
    def __init__(self, parent, flip=False):
        self.parent = parent
        self.flip = flip
        self.canvas = Canvas(
            parent,
            width=self.columns*self.square_size+self.offset*2,
            height=self.rows*self.square_size+self.offset*2,
        )
        self.canvas.pack()
        self.draw_board(self.flip)

        images = {
            name: Image.open('./pieces/{}.png'.format(name)).resize((self.square_size, self.square_size), Image.ANTIALIAS)
            for name in self.piece_names
        }
        self.images = {
            name: ImageTk.PhotoImage(image)
            for name, image in images.items()
        }

    def draw_board(self, flip=False):
        def red_home(row, col):
            if flip:
                return row == 0 and col == 2
            else:
                return row == 4 and col == 2
        def blue_home(row, col):
            if flip:
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
                self.canvas.create_rectangle(
                    col*self.square_size+self.offset,
                    row*self.square_size+self.offset,
                    (col+1)*self.square_size+self.offset,
                    (row+1)*self.square_size+self.offset,
                    width=2,
                    fill=color
                )

    def draw_pieces(self, pieces):
        def coordinate(i):
            if self.flip:
                col = i % 5
                row = i // 5
                return (col*self.square_size+self.offset, row*self.square_size+self.offset)
            else:
                col = i % 5
                row = 4 - (i // 5)
                return (col*self.square_size+self.offset, row*self.square_size+self.offset)
        self.canvas.delete('piece')
        for i, piece in enumerate(pieces):
            if piece.name() != 'empty':
                self.canvas.create_image(
                    coordinate(i),
                    anchor='nw',
                    image=self.images[piece.name()],
                    tags=('piece', piece.name())
                )

def main():
    root = Tk()
    root.title('Board')
    gui = GUI(root,flip=False)
    game = oni.Game(oni.ALL_CARDS[0:5])
    gui.draw_pieces(game.board.array)
    root.mainloop()

if __name__ == '__main__':
    main()
