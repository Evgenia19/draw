#!/usr/bin/env python3

"""
Simple vector drawing application using PyQt5
© 2018 Raphael Wimmer <raphael.wimmer@ur.de>
Released into the public domain / licensed under the Creative Commons Zero license

Features:
- supports Wacom pens and pressure sensitivity (if Qt recognizes them)
- automatically saves to SVG file

Point format: (x, y, pressure)
Shape format: [points]

TO DO:
- extend shape format with color, line style
- auto-close shapes
- eraser 
- auto-shapes (circle, rectangle) using $1 recognizer
- resample / optimize shapes
"""

from PyQt5 import Qt, QtGui, QtCore, QtWidgets, QtSvg
import sys
import math
from math import sin, cos, pi, sqrt
from pickle import PicklingError, UnpicklingError
import pickle
from numpy import matrix

DRAW_SIMPLE = False
MAX_WIDTH = 10
PEN_STYLES = [QtCore.Qt.SolidLine, QtCore.Qt.DashLine, QtCore.Qt.DotLine]


class QDrawWidget(QtWidgets.QWidget):

    SAVE_FILE = "/tmp/draw.pickle"
    SVG_FILE = "/tmp/draw.svg"

    def __init__(self, width=1920, height=1080):
        super().__init__()
        self.resize(width, height)
        self.showFullScreen()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents)
        self.setMouseTracking(True)  # only get events when button is pressed
        self.setTabletTracking(True)  # only get events when button is pressed
        self.draw_points = False
        self.drawing = False
        self.grid = True
        self.color = QtGui.QColor(0, 155, 0)
        self.pen_style = QtCore.Qt.SolidLine
        try:
            with open(self.SAVE_FILE, "rb") as fd:
                self.shapes = pickle.load(fd)
        except (FileNotFoundError, UnpicklingError, TypeError, EOFError):
            self.shapes = []
        self.points = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Drawable')
        self.setCursor(QtCore.Qt.CrossCursor)
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            pass

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            if len(self.points) > 1:
                # self.points = self.custom_filter(self.points)
                self.shapes.append(self.points[:])
            else:
                self.shapes.append([(ev.x(), ev.y(), 1.0)])
            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y(), 1.0)) #  pressure = 1
            self.update()

    def tabletEvent(self, ev):
        #print(ev.pos(), ev.globalPos(), ev.hiResGlobalX(), ev.hiResGlobalY(), ev.pressure(), ev.tangentialPressure(), ev.device(), ev.pointerType())
        # only happens when pen is pressed
        if ev.pressure() == 0.0: # lift off
            self.drawing = False
            if len(self.points) > 1:
                # self.points = self.custom_filter(self.points)
                self.shapes.append(self.points[:])
            else:
                self.shapes.append([(ev.x(), ev.y(), ev.pressure())])
            self.update()
        else:
            if self.drawing == False:  #press event 
                self.drawing = True
                self.points = []
                self.update()
            else:
                self.points.append((ev.x(), ev.y(), ev.pressure()))
                self.update()


#    def event(self, ev):
#        if ev.type() in [QtCore.QEvent.TouchBegin,
#                         QtCore.QEvent.TouchUpdate,
#                         QtCore.QEvent.TouchCancel,
#                         QtCore.QEvent.TouchEnd]:
#            ev.accept()
#            print(ev.touchPoints())
#            return True
#        else:
#            return super().event(ev)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.save()
            self.close()
        elif ev.key() == QtCore.Qt.Key_F:
            self.toggle_fullscreen()
        elif ev.key() == QtCore.Qt.Key_C:
            self.color = QtWidgets.QColorDialog.getColor()
        elif ev.key() == QtCore.Qt.Key_Comma:
            self.pen_style = QtCore.Qt.SolidLine
        elif ev.key() == QtCore.Qt.Key_Period:
            self.pen_style = QtCore.Qt.DotLine
        elif ev.key() == QtCore.Qt.Key_Minus:
            self.pen_style = QtCore.Qt.DashLine
        elif ev.key() == QtCore.Qt.Key_Delete:
            self.points = []
            self.shapes = []
            self.update()
        elif ev.key() == QtCore.Qt.Key_Backspace:
            if len(self.points) > 0:
                self.points = []
            self.shapes = self.shapes[:-1]
            self.update()
        #else:
            #print("Unknown key: %s" % QtGui.QKeySequence(ev.key()).toString())

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def save(self):
        try:
            with open(self.SAVE_FILE, "wb") as fd:
                pickle.dump(self.shapes, fd)
        except PicklingError:
            print("Error saving drawing")
        svg_gen = QtSvg.QSvgGenerator()
        svg_gen.setFileName(self.SVG_FILE)
        svg_gen.setSize(QtCore.QSize(self.width(), self.height()))
        svg_gen.setViewBox(QtCore.QRect(0, 0, self.width(), self.height()))
        svg_gen.setTitle("draw.py export")
        svg_gen.setDescription("a test...")
        painter = QtGui.QPainter()
        painter.begin(svg_gen)
        self.paint(painter, grid=False, black_background=False)
        painter.end()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*(p[0:2])), pts))

    def paintEvent(self, ev):
        self.paint(grid=self.grid, black_background=True)

    # allow painting to  existing painter (for SVG export)
    def paint(self, painter=None, grid=False, black_background=True):
        if painter is None:
            qp = QtGui.QPainter() # draw on screen
        else:
            qp = painter
        qp.begin(self)
        if black_background:
            qp.setBrush(QtGui.QColor(0, 0, 0))
            qp.drawRect(QtCore.QRect(0, 0, self.width(), self.height()))
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(self.color)
        for shape in self.shapes:
            if DRAW_SIMPLE:
                qp.drawPolyline(self.poly(shape))
            else:
                for pair in zip(shape, shape[1:]):
                    p = qp.pen()
                    p.setWidth(pair[0][2] * MAX_WIDTH)
                    p.setStyle(self.pen_style)
                    qp.setPen(p)
                    qp.drawLine(pair[0][0], pair[0][1], pair[1][0], pair[1][1])
            for point in shape:
                if self.draw_points:
                    qp.drawEllipse(point[0] - 1, point[1] - 1, 2, 2)
        qp.setPen(QtGui.QColor(155, 0, 0))
        if DRAW_SIMPLE:
            qp.drawPolyline(self.poly(self.points))
        else:
            for pair in zip(self.points, self.points[1:]):
                p = qp.pen()
                p.setWidth(pair[0][2] * MAX_WIDTH)
                p.setStyle(self.pen_style)
                qp.setPen(p)
                qp.drawLine(pair[0][0], pair[0][1], pair[1][0], pair[1][1])
        for point in self.points:
            if self.draw_points:
                qp.drawEllipse(point[0] - 1, point[1] - 1, 2, 2)
        if grid:
            qp.setPen(QtGui.QColor(255, 100, 100, 50))  # semi-transparent
            for x in range(0, self.width(), 20):
                qp.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 20):
                qp.drawLine(0, y, self.width(), y)
        qp.end()


# stuff for the $1 recognizer

def distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt(dx * dx + dy * dy)


def total_length(point_list):
    p1 = point_list[0]
    length = 0.0
    for i in range(1, len(point_list)):
        length += distance(p1, point_list[i])
        p1 = point_list[i]
    return length


def resample(point_list, step_count=24):
    newpoints = []
    length = total_length(point_list)
    stepsize = length / step_count
    curpos = 0
    newpoints.append(point_list[0])
    i = 1
    while i < len(point_list):
        p1 = point_list[i - 1]
        d = distance(p1, point_list[i])
        if curpos + d >= stepsize:
            nx = p1[0] + ((stepsize - curpos) / d) * (point_list[i][0] - p1[0])
            ny = p1[1] + ((stepsize - curpos) / d) * (point_list[i][1] - p1[1])
            newpoints.append([nx, ny])
            point_list.insert(i, [nx, ny])
            curpos = 0
        else:
            curpos += d
        i += 1
    return newpoints


def rotate(points, center, angle_degree):
    new_points = []
    angle_rad = angle_degree * (pi / 180)  # degrees multmat
    rot_matrix = matrix([
        [cos(angle_rad), -sin(angle_rad), 0],  # clockwise
        [sin(angle_rad), cos(angle_rad), 0],
        [0, 0, 1]
    ])
    t1 = matrix([[1, 0, -center[0]], [0, 1, -center[1]], [0, 0, 1]])
    t2 = matrix([[1, 0, center[0]], [0, 1, center[1]], [0, 0, 1]])
    transform = t2 @ rot_matrix @ t1
    for point in points:
        hom_point = matrix([[point[0]], [point[1]], [1]])
        rotated_point = transform @ hom_point
        new_points.append((float(rotated_point[0]), float(rotated_point[1])))
    return new_points


def centroid(points):
    xs, ys = zip(*points)
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def angle_between(point1, point2):  # point2 is our centroid
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.atan2(dy, dx) * 180 / math.pi  # degree


assert (angle_between((-10, -10), (0, 0)) == 45.0)


def scale(points):
    size = 100
    xs, ys = zip(*points)
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_range = x_max - x_min
    y_range = y_max - y_min
    points_new = []
    for p in points:
        p_new = ((p[0] - x_min) * size / x_range,
                 (p[1] - y_min) * size / y_range)
        points_new.append(p_new)
    return points_new


def normalize(points):  # put everything together
    print("normalizing")
    points_new = resample(points)
    print("resampled!!")
    angle = -angle_between(points_new[0], centroid(points_new))
    points_new = rotate(points_new, centroid(points_new), angle)
    print("rotated!!")
    points_new = scale(points_new)
    print("normalized!!")
    return points_new


def custom_filter(points):
    print("filtering...")
    return (normalize(points))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dw = QDrawWidget()  # a new window should open - draw into it!
    dw.custom_filter = custom_filter
    sys.exit(app.exec_())
