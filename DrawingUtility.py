from turtle import *
from tkinter import *
from MazeSolvingAlgos import Index, RandomMazeGenerator
SQR_SIDE_LEN = 10                                   # Side's length of Squared shaped turtle (20 pixels by default)
HALF_SQR_SIDE_LEN = SQR_SIDE_LEN // 2

class Maze:
    #  CellType                     Color on screen     
    ORIFICE = True                      # White
    BLOCK   = False                     # Black
    START   = 'S'                       # Green
    END     = 'E'                       # Red
    
    def __init__(self, left, right, top, bottom):
        self.grid = None
        xlim, ylim = Maze.curb(left, right, top, bottom)
        self.config(xlim, ylim)
        self.setSteps(None, None)

    def curb(left, right, top, bottom):
        return ((left   + HALF_SQR_SIDE_LEN, right  - HALF_SQR_SIDE_LEN), 
                (bottom + HALF_SQR_SIDE_LEN, top    - HALF_SQR_SIDE_LEN))
    
    def config(self, xlim, ylim, start=None, end=None, grid=None, traversed=None, solution=None):
        self.minX, self.maxX = xlim
        self.minY, self.maxY = ylim
        self.start = start
        self.end = end
        if grid is not None:
            self.grid = grid
        elif self.grid is None:
            rowsNo = self.maxY // HALF_SQR_SIDE_LEN
            colsNo = self.maxX // HALF_SQR_SIDE_LEN
            self.grid = [[True for _ in range(colsNo)] for _ in range(rowsNo)]
        if start is not None:
            xs, ys = start
            self[xs][ys] = Maze.START
        if end is not None:
            xe, ye = end
            self[xe][ye] = Maze.END
        if traversed is not None:
            self.setSteps(traversed, solution)
    
    def setSteps(self, traversed = None, solution = None):
        self.traversed = traversed
        self.solution = solution
    
    def __getitem__(self, rowNo):
        return self.grid[rowNo]         # for object `maze`; for using maze[i] instead of maze.grid[i] 
    
    def __len__(self):
        return self.grid.__len__()      # for object `maze`; for using len(maze) instead of len(maze.grid)
    
    def __repr__(self):
        form = lambda tuple_ : ','.join(map(str, tuple_)) if tuple_ is not None else str(None)
        string  = '; '.join((
            "SSL:" + str(SQR_SIDE_LEN),
            "X:" + form((self.minX, self.maxX)),
            "Y:" + form((self.minY, self.maxY)),
            "Start:" + form(self.start),
            "End:" + form(self.end) + '\n'
        ))
        for i in range(len(self)):
            row = (str(int(cell != Maze.BLOCK)) for cell in self[i])
            string += ','.join(row) + "\n"
        def stringfy(cells):
            return '; '.join((str(cell) for cell in cells)) if cells is not None else str(None)
        solsteps = '\n'.join(map(stringfy, (self.traversed, self.solution)))
        string = ''.join((string, solsteps))
        return string
    
    def isValidMove(self, x, y):
        return self.minX < x < self.maxX and self.minY < y < self.maxY
    
    def gridIndexToScreenIndex(self, y, x):
        '''
            Note that y before x and they are swapped 
            because x in screen represents x-coordinate 
            or postition in width (i.e., index of pixel's column), 
            while x in grid represents the index of cell's row.
            Same for y, in screen represents y-coordinate 
            or postition in height (i.e., index of pixel's row), 
            while y in grid represents the index of cell's column.

        '''
        y = self.minX + (y * SQR_SIDE_LEN + HALF_SQR_SIDE_LEN)
        x = self.maxY - (x * SQR_SIDE_LEN + HALF_SQR_SIDE_LEN)
        return y, x
    
    def screenIndexToGridIndex(self, x, y):
        distanceX = x - self.minX
        distanceY = self.maxY - y
        rowIndex  = int(distanceY // SQR_SIDE_LEN)
        colIndex  = int(distanceX // SQR_SIDE_LEN)
        return rowIndex, colIndex
    
    def constituteAndRecord(self, x, y, cellType):
        rowIndex, colIndex = self.screenIndexToGridIndex(x, y)
        self.grid[rowIndex][colIndex] = cellType
        x, y = self.gridIndexToScreenIndex(colIndex, rowIndex)
        return x, y
    
    def startingCell(self, new_start=None):
        prev_start = None
        if self.start is not None:
            prev_start = self.gridIndexToScreenIndex(self.start[1], self.start[0])
        if new_start is not None:
            self.start = self.screenIndexToGridIndex(new_start[0], new_start[1])
        return prev_start
    
    def endingCell(self, new_end=None):
        prev_end = None
        if self.end is not None:
            prev_end = self.gridIndexToScreenIndex(self.end[1], self.end[0])
        if new_end is not None:
            self.end = self.screenIndexToGridIndex(new_end[0], new_end[1])
        return prev_end
    
    def reset(self):
        for i in range(len(self)):
            for j in range(len(self[i])):
                self.grid[i][j] = Maze.ORIFICE
        self.start = None
        self.end = None
    
    def isTraversed(self):
        return self.traversed is not None
    
    def isSolved(self):
        return self.solution is not None and len(self.solution) >= 2


class RGBHandler:
    FULL   = 0xFF
    EMPTY  = 0x00
    PHASE0 = 0
    PHASE1 = 1
    PHASE2 = 2
    PHASE3 = 3
    
    def __init__(self, pathLen):
        self.R   = RGBHandler.EMPTY
        self.G   = RGBHandler.FULL
        self.B   = RGBHandler.EMPTY
        self.inc = 1024 / pathLen
        self.phase = 0
        '''
            Phase 0: Red = 0, Green = 255, Blue is increasing
            Phase 1: Red = 0, Green is decreasing, Blue = 255
            Phase 2: Red is increasing, Green = 0, Blue = 255
            Phase 3: Red = 255, Green = 0, Blue is decreasing
        '''
    
    def _format(self, clr):
        formatted = hex(clr)[2:]
        if len(formatted) == 1:
            formatted = '0' + formatted
        return formatted
    
    def __iter__(self):
        return self
    
    def __next__(self):
        string = self.colorstring()
        self.proceedNextColor()
        return string
    
    def RGB(self):
        return int(self.R), int(self.G), int(self.B)
    
    def colorstring(self):
        r, g, b = map(self._format, self.RGB())
        return ''.join(('#', r, g, b))
    
    def constrict(self, component):
        return RGBHandler.FULL, component - RGBHandler.FULL
    
    def regulate(self, component):
        return RGBHandler.EMPTY, -component
    
    def phase0procedure(self, rem):
        if rem == 0:
            rem = self.inc
        self.B += self.inc
        if self.B > RGBHandler.FULL:
            self.B, rem = self.constrict(self.B)
            self.phase += 1
        if self.B < RGBHandler.EMPTY:               # Reversed RGBHandler case
            self.B, rem = self.regulate(self.B)
            self.phase -= 1
        return rem
    
    def phase1procedure(self, rem):
        if rem == 0:
            rem = self.inc
        self.G -= rem
        if self.G < RGBHandler.EMPTY:
            self.G, rem = self.regulate(self.G)
            self.phase += 1
        elif self.G > RGBHandler.FULL:               # Reversed RGBHandler case
            self.G, rem = self.constrict(self.G)
            self.phase -= 1
        return rem
    
    def phase2procedure(self, rem):
        if rem == 0:
            rem = self.inc
        self.R += rem
        if self.R > RGBHandler.FULL:
            self.R, rem = self.constrict(self.R)
            self.phase += 1
        elif self.R < RGBHandler.EMPTY:               # Reversed RGBHandler case
            self.R, rem = self.regulate(self.R)
            self.phase -= 1
        return rem
    
    def phase3procedure(self, rem):
        if rem == 0:
            rem = self.inc
        self.B -= rem
        if self.B < RGBHandler.EMPTY:
            self.B, rem = self.regulate(self.B)
            self.phase += 1
        elif self.B > RGBHandler.FULL:               # Reversed RGBHandler case
            self.B, rem = self.constrict(self.B)
            self.phase -= 1
        return rem
    
    def proceedNextColor(self):
        rem = 0
        if self.phase is RGBHandler.PHASE0:
            rem = self.phase0procedure(rem)
        if self.phase is RGBHandler.PHASE1:
            rem = self.phase1procedure(rem)
        if self.phase is RGBHandler.PHASE2:
            rem = self.phase2procedure(rem)
        if self.phase is RGBHandler.PHASE3:
            self.phase3procedure(rem)
    

class RevRGBHandler(RGBHandler):
    def __init__(self, pathLen):
        self.R   = RGBHandler.FULL
        self.G   = RGBHandler.EMPTY
        self.B   = RGBHandler.EMPTY
        self.inc = -1024 / pathLen
        self.phase = 3
        '''
            Phase 3: Red = 255, Green = 0, Blue is increasing
            Phase 2: Red is decreasing, Green = 0, Blue = 255
            Phase 1: Red = 0, Green is increasing, Blue = 255
            Phase 0: Red = 0, Green = 255, Blue is decreasing
        '''
    
    def proceedNextColor(self):
        rem = 0
        if self.phase is RGBHandler.PHASE3:
            rem = -self.phase3procedure(rem)
        if self.phase is RGBHandler.PHASE2:
            rem = -self.phase2procedure(rem)
        if self.phase is RGBHandler.PHASE1:
            rem = -self.phase1procedure(rem)
        if self.phase is RGBHandler.PHASE0:
            self.phase0procedure(rem)

class DrawingCanvas:
    class ResetModes:
        Command  = 'command'                        # for reseting DrawingCanvas in demand (Ctrl+R or reset from menubar)
        Complete = 'complete'                       # for clearing DrawingCanvas to replace drawings from loaded one
        Drawings = 'drawings'                       # for updating DrawingCanvas to redraw drawings (for resizing)
    
    def __init__(self, MainWin, MazeWidth, MazeHeight):
        self.MainWin = MainWin                      # Parent Window
        self.animation = BooleanVar()
        self.gridView = BooleanVar()
        self.zoomingPercent = 50
        self.playing = False
        self.maze = None
        self.FPS = 30
        self.setup(MazeWidth, MazeHeight)
    
    def setup(self, MazeW, MazeH):
        frameW = self.MainWin.width * 0.75          # Width that appears in the monitor
        frameH = self.MainWin.height                # Height that appears in the monitor
        screenW = (MazeW + 2) * SQR_SIDE_LEN        # Actual Width that you can draw on [*Note*: `+2` for left and right borders and `*SQR_SIDE_LEN` to convert cells number to pixels]
        screenH = (MazeH + 2) * SQR_SIDE_LEN        # Actual Height that you can draw on [*Note*: `+2` for upper and lower borders and `*SQR_SIDE_LEN` to convert cells number to pixels]
        self.canvas = ScrolledCanvas(self.MainWin, width=frameW, height=frameH, 
                                     canvwidth=screenW, canvheight=screenH)
        self.canvas.pack(side=LEFT)
        self.screen = TurtleScreen(self.canvas)
        self.screen.tracer(False)
        self.drawer = RawTurtle(self.screen, shape='square', visible=False)
        self.drawer.shapesize(SQR_SIDE_LEN / 20, SQR_SIDE_LEN / 20)
        self.drawer.speed('fastest')
        self.drawer.penup()
        self.eraser = self.drawer.clone()
        self.traverser = self.drawer.clone()
        self.speculum = self.drawer.clone()
        self.eraser.color('white')
        self.setupEvents()
        l, r, t, b = self.drawBorders()
        self.maze = Maze(l, r, t, b)
    
    def reshape(self, w, h, resetMode):
        screenW = (w + 2) * SQR_SIDE_LEN        
        screenH = (h + 2) * SQR_SIDE_LEN   
        self.canvas.reset(canvwidth=screenW, canvheight=screenH)
        return self.reset(resetMode=resetMode)
    
    def setupEvents(self):
        self.screen.onclick(self.mark)
        self.screen.onclick(self.erase, 3)
        self.canvas.bind("<B1-Motion>", self.contMarking)
        self.canvas.bind("<B3-Motion>", self.contErasing)
        self.canvas.bind('<Control-Button-1>', self.assignStart)
        self.canvas.bind('<Control-Button-3>', self.assignEnd)
    
    def getActualIndex(self, event):
        return (self.canvas.canvasx(event.x) / self.screen.xscale,
                -self.canvas.canvasy(event.y) / self.screen.yscale)
    
    def seal(turtleObj, x, y):
        turtleObj.setpos(x, y)
        turtleObj.stamp()
    
    def mark(self, x, y):
        if self.maze.isValidMove(x, y):
            x, y = self.maze.constituteAndRecord(x, y, Maze.BLOCK)
            DrawingCanvas.seal(self.drawer, x, y)
    
    def erase(self, x, y, cellType = Maze.ORIFICE):
        if self.maze.isValidMove(x, y):
            x, y = self.maze.constituteAndRecord(x, y, cellType)
            DrawingCanvas.seal(self.eraser, x, y)
            return x, y
    
    def contMarking(self, event):
        x, y = self.getActualIndex(event)
        self.mark(x, y)
    
    def contErasing(self, event):
        x, y = self.getActualIndex(event)
        self.erase(x, y)
    
    def assignUtility(self, index, new_color, cellType, func):
        x, y = index if isinstance(index, tuple) else self.getActualIndex(index)
        color = self.eraser.color()
        self.eraser.color(color[0], new_color)
        new = self.erase(x, y, cellType)
        self.eraser.color(color[0], color[1])
        if new is None:
            return
        prev = func(new)
        if prev is not None and new != prev:
            self.erase(prev[0], prev[1])
    
    def assignStart(self, index):
        self.assignUtility(index, '#00ff00', Maze.START, self.maze.startingCell)
    
    def assignEnd(self, index):
        self.assignUtility(index, '#ff0000', Maze.END, self.maze.endingCell)
    
    def drawBorders(self):
        def drawBorder(_from, _to):
            '''
            _from and _to are tuple(Y_coordinate, X_coordinate) and
            (_from.x <= _to.x), (_from.y <= _to.y)  
            '''
            for x in range(_from[1], _to[1] + 1, SQR_SIDE_LEN):
                for y in range(_from[0], _to[0] + 1, SQR_SIDE_LEN):
                    DrawingCanvas.seal(self.drawer, x, y)
        x, y = self.screen.screensize()
        x = (x - SQR_SIDE_LEN) // 2
        y = (y - SQR_SIDE_LEN) // 2
        left   = -x
        right  =  x
        top    =  y
        bottom = -y
        self.drawer.color('white', 'black')
        drawBorder((top, left), (top, right))       # Upper border
        drawBorder((bottom, left), (top, left))     # Left  border
        drawBorder((bottom, right), (top, right))   # Right border
        drawBorder((bottom, left), (bottom, right)) # Lower border
        return left, right, top, bottom
    
    def drawLayout(self, turtleObj):
        def drawLine(start, distance, turtleObj):
            turtleObj.penup()
            turtleObj.setpos(start)
            turtleObj.pendown()
            turtleObj.forward(distance)
        x0, y0 = self.maze.minX, self.maze.minY
        x1, y1 = self.maze.maxX, self.maze.maxY
        turtleObj.left(90)
        # Horizontal Lines
        for x in range(x0, x1 + 1, SQR_SIDE_LEN):
            drawLine((x, y0), y1 - y0, turtleObj)
        turtleObj.right(90)
        # Vertical Lines
        for y in range(y0, y1 + 1, SQR_SIDE_LEN):
            drawLine((x0, y), x1 - x0, turtleObj)
        turtleObj.penup()
    
    def changeGridView(self):
        self.screen.tracer(False)
        B = 'black'
        W = 'white'
        color = self.traverser.color()[1]
        drawingObj = None
        if self.gridView.get():
            self.drawer.color(B)
            self.eraser.color(B, W)
            self.traverser.color(B, color)
            drawingObj = self.drawer
        else:
            self.eraser.color(W)
            self.drawer.color(W, B)
            self.traverser.color(W, color)
            drawingObj = self.eraser
        self.drawLayout(drawingObj)
        self.screen.tracer(self.animation.get(), 1000/self.FPS)
    
    def changeFPS(self, newFPS):
        self.FPS = int(newFPS)
    
    def reset(self, resetMode=ResetModes.Command):
        self.playing = False
        self.traverser.clear()
        self.speculum.clear()
        if self.maze.isTraversed():
            if resetMode is not DrawingCanvas.ResetModes.Drawings:
                self.maze.setSteps(None, None)
                if resetMode is DrawingCanvas.ResetModes.Command:
                    return
        self.drawer.clear()
        self.eraser.clear()
        self.screen.tracer(False)
        coords = self.drawBorders()
        if resetMode is not DrawingCanvas.ResetModes.Drawings:
            self.maze.reset()
        return coords
    
    def save(self, filename):
        with open(filename, "wt") as output_file:
            output_file.write(str(self.maze))
    
    def adjustRatio(self, newSQR_SIDE_LEN, xlim, ylim):
        ratio = SQR_SIDE_LEN / newSQR_SIDE_LEN
        adjustRatioForTuple = lambda lim : map((lambda x : int(x * ratio)), lim)
        return map(adjustRatioForTuple, (xlim, ylim))
    
    def drawFromGrid(self, grid, withAnimation=False):
        self.changeGridView()
        if withAnimation:
            self.screen.tracer(self.animation.get(), 1000/self.FPS)
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                x, y = self.maze.gridIndexToScreenIndex(j, i)
                if grid[i][j] is Maze.BLOCK:
                    DrawingCanvas.seal(self.drawer, x, y)
                elif grid[i][j] is Maze.START:
                    self.assignStart((x, y))
                elif grid[i][j] is Maze.END:
                    self.assignEnd((x, y))
        if self.maze.isTraversed():
            tmp = self.animation.get()
            self.animation.set(False)
            self.animate()
            self.animation.set(tmp)
        self.screen.tracer(False)
    
    def adjustZooming(self, factor):
        global SQR_SIDE_LEN, HALF_SQR_SIDE_LEN
        DefaultSQR_SIDE_LEN = 20
        factor = float(factor)
        newSSL = int(factor * DefaultSQR_SIDE_LEN)
        self.drawer.shapesize(factor)
        self.eraser.shapesize(factor)
        self.traverser.shapesize(factor)
        xlim, ylim = self.adjustRatio(newSSL, 
                                      (self.maze.minX, self.maze.maxX),
                                      (self.maze.minY, self.maze.maxY))
        SQR_SIDE_LEN = newSSL
        HALF_SQR_SIDE_LEN = newSSL // 2
        l, r, t, b = self.reshape(len(self.maze[0]), len(self.maze), resetMode=DrawingCanvas.ResetModes.Drawings)
        xlim, ylim = Maze.curb(l, r, t, b)
        self.maze.config(xlim, ylim)
        self.drawFromGrid(self.maze.grid)
    
    def zoomingUtility(self, inc):
        if self.playing:
            return
        self.zoomingPercent += inc
        self.adjustZooming(self.zoomingPercent / 100)
    
    def zoomIn(self):
        if self.zoomingPercent < 1000:
            self.zoomingUtility(10)
    
    def zoomOut(self):
        if self.zoomingPercent > 10:
            self.zoomingUtility(-10)
    
    def load(self, filename):
        with open(filename, "rt") as input_file:
            def extract_tuple(string):
                string = string.split(':')[1]
                if 'None' in string:
                    return None
                l, r = map(int, string.split(','))
                return l, r
            mems = input_file.readline().split('; ')
            fileSQR_SIDE_LEN = int(mems[0].split(':')[1])
            xlim, ylim, start, end = map(extract_tuple, mems[1:])
            xlim, ylim = self.adjustRatio(fileSQR_SIDE_LEN, xlim, ylim)
            lines = input_file.readlines()
            grid, traversed, solution = lines[:-2], lines[-2], lines[-1]
            StrtoIntList = lambda string : map(int, string.split(','))
            def StrToIndices(string):
                if 'None' in string:
                    return None
                string = string.split('; ')     
                indices = tuple(Index(x, y) for x, y in map(StrtoIntList, string))
                return indices
            traversed = StrToIndices(traversed)
            solution = StrToIndices(solution)
            StrtoBoolList = lambda row : list(map(bool, StrtoIntList(row)))
            grid = list(map(StrtoBoolList, grid))
            self.reshape(len(grid[0]), len(grid), resetMode=DrawingCanvas.ResetModes.Complete)
            self.maze.config(xlim, ylim, start, end, grid, traversed, solution)
            self.drawFromGrid(grid)
    
    def animate(self):
        if not self.maze.isTraversed():
            return
        self.playing = True
        self.traverser.clear()
        self.speculum.clear()
        color = self.drawer.color()
        self.screen.tracer(self.animation.get(), 1000 / self.FPS)
        def doAnimation(cells, func):
            for cell in cells:
                if not self.playing:
                    return
                func()
                x, y = self.maze.gridIndexToScreenIndex(cell.col, cell.row)
                DrawingCanvas.seal(self.speculum, x, y)
                DrawingCanvas.seal(self.traverser, x, y)
        def doNothing():
            pass
        self.traverser.color(color[0], '#9897a9')
        self.speculum = self.traverser.clone()
        self.speculum.color('orange')
        doAnimation(self.maze.traversed, doNothing)
        self.assignStart(self.maze.startingCell())
        self.assignEnd(self.maze.endingCell())
        if self.maze.isSolved():
            r, c = self.maze.start
            rgbh = (
                RGBHandler(len(self.maze.solution) - 2) if self.maze.solution[0] == Index(r, c)
                else RevRGBHandler(len(self.maze.solution) - 2)
            )
            def handleColors():
                outline = self.traverser.color()[0]
                self.traverser.color(outline, next(rgbh))
            doAnimation(self.maze.solution[1:-1], handleColors)
        self.speculum.clear()
        self.screen.tracer(False)
        self.playing = False
    
    def generateRandMaze(self):
        self.reset(resetMode=DrawingCanvas.ResetModes.Complete)
        rmg = RandomMazeGenerator(len(self.maze), len(self.maze[0]))
        self.maze.grid = rmg.generate()
        self.drawFromGrid(self.maze.grid, withAnimation=True)
    
    def invert(self):
        self.screen.tracer(False)
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                newType = turtleObj = None
                if self.maze[i][j] is Maze.BLOCK:
                    newType = Maze.ORIFICE
                    turtleObj = self.eraser
                elif self.maze[i][j] is Maze.ORIFICE:
                    newType = Maze.BLOCK
                    turtleObj = self.drawer
                else: continue
                x, y = self.maze.gridIndexToScreenIndex(j, i)
                DrawingCanvas.seal(turtleObj, x, y)
                self.maze[i][j] = newType
        self.screen.tracer(self.animation.get(), 1000/self.FPS)
