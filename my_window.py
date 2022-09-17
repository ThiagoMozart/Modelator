from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from my_canvas import *
from my_model import *


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        self.model = MyModel()
        self.canvas.setModel(self.model)
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.png"), "fit", self)
        tb.addAction(fit)
        rand = QAction(QIcon("icons/icons8-random-64"), "random", self)
        tb.addAction(rand)
        tb.actionTriggered[QAction].connect(self.tbpressed)


    def tbpressed(self, a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "random":
            self.canvas.genRandomPoints()