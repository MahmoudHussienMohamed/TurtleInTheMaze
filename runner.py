from GUI import askWidthAndHeight, Window
assigned, width, height = askWidthAndHeight()
if not assigned:
    exit(0)
win = Window(width, height)
win.show()