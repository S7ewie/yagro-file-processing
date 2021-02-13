class Table:

    def __init__(self, root, lst):
        total_rows = len(lst)
        total_columns = len(lst[0])
        # code for creating table
        for i in range(total_rows):
            for j in range(total_columns):

                if i == 0:
                    self.e = Label(root, font=("", 14, 'bold'))
                else:
                    self.e = Label(root, font=("", 12))

                self.e.grid(row=i, column=j)
                self.e.configure(text=lst[i][j])


class ImageLabel(Label):
    """a label that displays images, and plays them if they are gifs"""

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)
