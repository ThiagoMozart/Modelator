from PyQt5 import QtOpenGL, QtCore
from OpenGL.GL import *
from PyQt5.QtCore import Qt

from he.hecontroller import HeController
from he.hemodel import HeModel
from geometry.segments.line import Line
from geometry.point import Point
from compgeom.tesselation import Tesselation
from random import random, randint


class MyCanvas(QtOpenGL.QGLWidget):

    def __init__(self):
        super(MyCanvas, self).__init__()
        self.color_v = 1.0
        self.m_model = None
        self.m_w = 0
        self.m_h = 0
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPointF(0.0, 0.0)
        self.m_pt1 = QtCore.QPointF(0.0, 0.0)
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)

    def resizeGL(self, _width, _height):
        self.m_w = _width
        self.m_h = _height

        if (self.m_model is None) or (self.m_model.isEmpty()):
            self.scaleWorldWindow(1.0)

        else:
            self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)

        glViewport(0, 0, self.m_w, self.m_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def genRandomPoints(self):
        for i in range(12):
            value = randint(1, 5)
            p0 = Point(randint(-400 * value, 0), randint(0, 400 * value))
            p1 = Point(randint(-400 * value, 0), randint(0, 400 * value))
            segment = Line(p0, p1)
            self.m_controller.insertSegment(segment, 0.01)
            self.update()
            self.repaint()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        if self.m_hmodel and not self.m_hmodel.isEmpty():
            patches = self.m_hmodel.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                triangs = Tesselation.tessellate(pts)
                for j in range(len(triangs)):
                    r = random()
                    b = random()
                    g = random()
                    glColor3f(r, 0, g) #
                    glBegin(GL_TRIANGLES)
                    glVertex2d(pts[triangs[j][0]].getX(), pts[triangs[j][0]].getY())
                    glVertex2d(pts[triangs[j][1]].getX(), pts[triangs[j][1]].getY())
                    glVertex2d(pts[triangs[j][2]].getX(), pts[triangs[j][2]].getY())
                    glEnd()

            segments = self.m_hmodel.getSegments()
            for seg in segments:
                ptc = seg.getPointsToDraw()
                r = random()
                b = random()
                g = random()
                glColor3f(r, b, g) #
                glBegin(GL_LINES)
                for i in range(2):
                    glVertex2f(ptc[i].getX(), ptc[i].getY())
                glEnd()
        glEndList()

    def setModel(self, _model):
        self.m_model = _model

    def fitWorldToViewport(self):
        if not self.m_model:
            return
        self.m_L, self.m_R, self.m_B, self.m_T = self.m_hmodel.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()

    def scaleWorldWindow(self, _scaleFac):
        vpr = self.m_h / self.m_w
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac

        if sizey > (vpr * sizex):
            sizex = sizey / vpr

        else:
            sizey = sizex * vpr

        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def panWorldWindow(self, _panFacX, _panFacY):
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY

        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            pos = event.pos()
            self.m_L += pos.x()
            self.m_R -= pos.x()
            self.m_B += pos.y()
            self.m_T -= pos.y()
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
            self.update()
        else:
            self.m_buttonPressed = True
            self.m_pt0 = event.pos()

    def mouseMoveEvent(self, event):
        if event.button() == Qt.RightButton:
            return

        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            return

        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        # self.m_model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())
        p0 = Point(pt0_U.x(), pt0_U.y())
        p1 = Point(pt1_U.x(), pt1_U.y())
        segment = Line(p0, p1)
        self.m_controller.insertSegment(segment, 0.01)
        self.update()
        self.repaint()
        self.m_buttonPressed = False
        self.m_pt0.setX(0)
        self.m_pt0.setY(0)
        self.m_pt1.setX(0)
        self.m_pt1.setY(0)
