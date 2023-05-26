from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import (
    Tk, Button, Frame, Checkbutton, Label, Entry, 
    scrolledtext, messagebox, Scale, Menu, IntVar,  
    StringVar, LEFT, RIGHT, HORIZONTAL, END 
)
from DrawingUtility import DrawingCanvas
from tkinter.ttk import Menubutton
from MazeSolvingAlgos import *
from time import time
from PIL import Image
import io

def askWidthAndHeight():
    assigned = False
    root = Tk()
    root.title("Maze Width and Height")
    def labelEntryFrame(labelText, EntryVar):
        frame = Frame(root, padx=10, pady=10)
        Label(frame, text=labelText, padx=3).pack(side=LEFT)
        Entry(frame, textvariable=EntryVar).pack(side=RIGHT)
        return frame
    width = IntVar(value=50)
    height = IntVar(value=50)
    labelEntryFrame('Maze Width', width).pack()
    labelEntryFrame('Maze Height', height).pack()
    def validate(args=None):
        nonlocal assigned
        if width.get() > 1 and height.get() > 1:
            assigned = True
            root.destroy()
        else:
            assigned = False
            messagebox.showerror(title="ERROR!", message="Width and Height must be greater than 1!")
    root.bind("<Return>", validate)
    Button(root, text='Ok', padx=15, command=validate).pack()
    root.mainloop()
    return assigned, width.get(), height.get()

Algorithms = {
    "Depth First Search"   : DepthFirstSearch, 
    "Breadth First Search" : BreadthFirstSearch, 
    "Dijkstra Algorithm"   : DijkstraAlgorithm, 
    "A* (A-Star)"          : AStar, 
    "Bellman-Ford"         : BellmanFord, 
    "Floyd-Warshall"       : FloydWarshall, 
    "Bidirectional Search" : BidirectionalSearch, 
}

class Window(Tk):
    def __init__(self, MazeWidth, MazeHeight):
        super().__init__()
        self.currentFilename = None
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.title('Turtle In The Maze')
        self.DCanvas = DrawingCanvas(self, MazeWidth, MazeHeight)
        self.setupWidgets()
        self.setupMenubar()
        self.setupAlgosMenu()
        self.setupEvents()

    def show(self):
        self.focus()
        self.mainloop()

    def setupWidgets(self):
        self.gridView = Checkbutton(self, text="Grid View", variable=self.DCanvas.gridView, 
                                    onvalue=True, offvalue=False, command=self.DCanvas.changeGridView)
        self.slider = Scale(self, label=(' ' * 12 + "FPS"), from_=10, to=240, resolution=10, 
                            orient=HORIZONTAL, command=self.DCanvas.changeFPS, tickinterval=110)
        self.slider.set(30)
        self.animation = Checkbutton(self, text="Animation", variable=self.DCanvas.animation, 
                                    onvalue=True, offvalue=False)
        self.solveButt = Button(self, text="Solve", command=self.solve)
        self.randGenButt = Button(self, text="Generate random maze", command=self.DCanvas.generateRandMaze)
        self.eventBox = scrolledtext.ScrolledText(self, state='disabled')
        self.gridView.pack()
        self.slider.pack()
        self.animation.pack()
        self.solveButt.pack()
        self.randGenButt.pack()
        self.eventBox.pack()
    
    def setupEvents(self):
        def bindAndIgnoreEventArgs(sequence, functionToDo):
            func = lambda uselessArgs : functionToDo()
            self.bind(sequence, func)
        bindAndIgnoreEventArgs('<Control-n>', self.newFile)
        bindAndIgnoreEventArgs('<Control-s>', self.save)
        bindAndIgnoreEventArgs('<Control-Shift-S>', self.saveas)
        bindAndIgnoreEventArgs('<Control-o>', self.load)
        bindAndIgnoreEventArgs('<Control-r>', self.DCanvas.reset)
        bindAndIgnoreEventArgs('<Control-=>', self.DCanvas.zoomIn)
        bindAndIgnoreEventArgs('<Control-minus>', self.DCanvas.zoomOut)
        def motion():
            curr = self.DCanvas.animation.get()
            self.DCanvas.animation.set(not curr)
        bindAndIgnoreEventArgs('<Control-m>', motion)
        def changeGridView():
            curr = self.DCanvas.gridView.get()
            self.DCanvas.gridView.set(not curr)
            self.DCanvas.changeGridView()
        bindAndIgnoreEventArgs('<Control-g>', changeGridView)
        bindAndIgnoreEventArgs('<Control-i>', self.DCanvas.invert)

    def setupAlgosMenu(self):
        self.algosMenu = Menubutton(self, text="Select Algorithm", width=20)
        menu = Menu(self.algosMenu, tearoff=0)
        self.selectedAlgo = StringVar()
        for algo in Algorithms.keys():
            menu.add_radiobutton(
                label=algo,
                value=algo,
                variable=self.selectedAlgo
            )
        def alorithmSelected(*args):
            self.algosMenu.config(text=self.selectedAlgo.get())
        self.selectedAlgo.trace_add("write", alorithmSelected)
        self.algosMenu['menu'] = menu
        self.algosMenu.pack(before=self.eventBox)
    
    def newFile(self):
        if self.currentFilename is not None:
            ansr = messagebox.askyesno(title='Notice!', message="Do you want to save maze?\nIt will be erased!")
            if ansr:
                self.save(self.currentFilename)
            self.DCanvas.reset(DrawingCanvas.ResetModes.Complete)
        else:
            self.save()
    
    def save(self, mazefilename = None):
        if mazefilename is None:
            mazefilename = asksaveasfilename(title="Save Maze", initialfile="Maze.titmz", 
                                                                defaultextension=".titmz",
                                                                filetypes=[("Maze Files", "*.titmz")])
        if len(mazefilename) > 0:
            self.DCanvas.save(mazefilename)
            self.currentFilename = mazefilename
            self.updateEventBox(f"Saved as '{mazefilename}' successfully.\n", False)
    
    def saveas(self):
        mazefilename = asksaveasfilename(title="Save Maze", initialfile="Maze", 
                                        defaultextension=".titmz",
                                        filetypes=[("Maze Files", "*.titmz"),
                                                    ("PNG Image", "*.png"),
                                                    ("JPG Image", "*.jpg"),
                                                    ("JPEG Image", "*.jpeg"),
                                                    ("BMP Image", "*.bmp")])
        if len(mazefilename) > 0:
            if mazefilename.find('.titmz') != -1:
                self.save(mazefilename)
            else:
                ps = self.DCanvas.canvas.postscript(colormode='color')
                img = Image.open(io.BytesIO(ps.encode('utf-8')))
                img.save(mazefilename)
                self.updateEventBox(f"Saved as '{mazefilename}' successfully.\n", False)
    
    def load(self):
        if self.currentFilename is not None:
            self.newFile()
        mazefilename = askopenfilename(title="Load Maze", filetypes=[("Maze Files", "*.titmz")])
        if len(mazefilename) > 0:
            self.DCanvas.load(mazefilename)
            self.currentFilename = mazefilename
            self.updateEventBox(f"'{mazefilename}' loaded successfully.\n", False)
    
    def setupMenubar(self):
        menubar = Menu(self)
        file = Menu(menubar, tearoff=0)
        file.add_command(label='New  (Ctrl+N)', command=self.newFile)
        file.add_command(label='Open (Ctrl+O)', command=self.load)
        file.add_command(label='Save (Ctrl+S)', command=self.save)
        file.add_command(label='Save as... (Ctrl+Shift+S)', command=self.saveas)
        file.add_command(label='Close (Ctrl+C)', command=self.newFile)
        file.add_separator()
        file.add_command(label='Exit', command=self.destroy)
        edit = Menu(menubar, tearoff=0)
        edit.add_command(label='Reset (Ctrl+R)', command=self.DCanvas.reset)
        edit.add_command(label='Clear Event Box', command=self.updateEventBox)
        edit.add_command(label='invert (Ctrl+I)', command=self.DCanvas.invert)
        view = Menu(menubar, tearoff=0)
        animation = Menu(menubar, tearoff=0)
        animation.add_checkbutton(label='Motion (Ctrl+M)', variable=self.DCanvas.animation)
        animation.add_checkbutton(label='Grid View (Ctrl+G)', variable=self.DCanvas.gridView, command=self.DCanvas.changeGridView)
        zooming = Menu(menubar, tearoff=0)
        zooming.add_command(label='Zoom in (Ctrl+=)', command=self.DCanvas.zoomIn)
        zooming.add_command(label='Zoom out (Ctrl+-)', command=self.DCanvas.zoomOut)
        view.add_cascade(label = "Animation and Appearance", menu=animation)
        view.add_separator()
        view.add_cascade(label = "Zooming", menu=zooming)
        help = Menu(menubar, tearoff=0)
        help.add_command(label='About')
        menubar.add_cascade(label='File', menu=file)
        menubar.add_cascade(label='Edit', menu=edit)
        menubar.add_cascade(label='View', menu=view)
        menubar.add_cascade(label='Help', menu=help)
        self.config(menu=menubar)
    
    def updateEventBox(self, txt_message='', clear=True):
        self.eventBox.configure(state='normal')
        if clear:
            self.eventBox.delete('1.0', END)
        self.eventBox.insert(END, txt_message)
        self.eventBox.configure(state='disabled')
    
    def solve(self):
        if not self.selectedAlgo.get():
            messagebox.showerror(title="ERROR!", 
                                 message="No Algorithm selected!\nPlease selecet algorithm first.")
            return 
        start, end = self.DCanvas.maze.start, self.DCanvas.maze.end
        if start is None:
            messagebox.showerror(title="ERROR!", 
                                 message="No Enterance point!\n([Ctrl+left mouse click] to mark enterance).")
            return 
        if end is None:
            messagebox.showerror(title="ERROR!", 
                                 message="No Destination point!\n([Ctrl+right mouse click] to mark destination).")
            return 
        algo = Algorithms[self.selectedAlgo.get()]
        grid = self.DCanvas.maze.grid.copy()
        start = Index(start[0], start[1])
        end = Index(end[0], end[1])
        grid[start.row][start.col] = grid[end.row][end.col] = True
        self.updateEventBox("Maze is being transformed to graph...\n", False)
        t = time()
        solver = algo(grid, start, end)
        self.updateEventBox(f"Transformation is done! [took {(time()-t)*1000:07.3f}ms]\n", False)
        self.updateEventBox("Solving Maze....\n", False)
        t = time()
        solver.solve()
        self.updateEventBox(f"Maze is solved! [took {(time()-t)*1000:07.3f}ms]\n", False)
        self.DCanvas.maze.setSteps(solver.TraversedNodes(), solver.SrcToDestPath())
        self.updateEventBox(f"Metrics:\n\t-Total traversed: {solver.TraversedNodesNo()} Nodes\n", False)
        self.updateEventBox(f"\t-Path length: {solver.SrcToDestDistance()} cells\n", False)
        self.updateEventBox("--------------------------------\n\n", False)
        self.DCanvas.animate()
