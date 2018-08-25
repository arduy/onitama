from tkinter import *

class GUI():
    rows = 5
    columns = 5
    square_size = 100
    offset = 5
    dark = '#f5deb3'
    light = '#ffffe0'
    def __init__(self, parent):
        self.parent = parent
        self.canvas = Canvas(
            parent,
            width=self.columns*self.square_size+self.offset*2,
            height=self.rows*self.square_size+self.offset*2,
        )
        self.canvas.pack()
        self.draw_board()

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

def main():
    root = Tk()
    root.title('Board')
    gui = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
