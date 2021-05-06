import hou
import sys

from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QMainWindow, QWidget, QGraphicsView, QGraphicsScene, QFrame, QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem)

from PySide2.QtGui import QScreen, QPixmap, QBrush, QPen, QMouseEvent, QPainter, QColor, QFont, QCursor, QPainterPath, QImage

from PySide2.QtCore import Qt, QRect, QRectF, QPoint, QPointF

import numpy as np

form = None

SHARP_PRECISION = 0.01
TOLERANCE = 0.0001

def is_color_ramp(parms):
    if not parms:
        return False
    parm = parms[0] # type: hou.Parm
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if parm_template.type() == hou.parmTemplateType.Ramp and parm_template.parmType() == hou.rampParmType.Color:
        return True
    
    return False

def is_color_parm(parms):
    if not parms:
        return False

    parm = parms[0] # type: hou.Parm
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if (parm_template.type() == hou.parmTemplateType.Float and
            parm_template.numComponents() == 3 and
            parm_template.namingScheme() == hou.parmNamingScheme.RGBA):
        return True
    
    return False

def is_float_ramp(parms):
    if not parms:
        return False
    parm = parms[0] # type: hou.Parm
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if parm_template.type() == hou.parmTemplateType.Ramp and parm_template.parmType() == hou.rampParmType.Float:
        return True
    
    return False


class ColorInformation(QGraphicsItem):
    def __init__(self, parent=None):
        super(ColorInformation, self).__init__(parent)
        self.color = QColor(255, 255, 0)
        self.font = QFont("courier", 10)
        self.font.setBold(True)
        self.pos = QPoint()

    def boundingRect(self):
        return QRectF(0, 0, 130, 100)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setFont(self.font)
        
        painter.drawRoundedRect(12, 12, 30, 74, 5, 5)

        painter.setBrush(QColor(0, 0, 0, 55))
        painter.setPen(QPen(Qt.transparent))
        painter.drawRect(44, 12, 74, 74)

        painter.setPen(QPen(Qt.red))        
        painter.drawText(50, 26, "R: "+str(self.color.red()))

        painter.setPen(QPen(Qt.green))        
        painter.drawText(50, 52, "G: "+str(self.color.green()))

        painter.setPen(QPen(Qt.blue))        
        painter.drawText(50, 80, "B: "+str(self.color.blue()))

class ScreenshotView(QGraphicsView):
    def __init__(self, parent, screen, parm, gradient_edit, ramp_sketch):
        super(ScreenshotView, self).__init__(parent)

        self.scene = QGraphicsScene(parent)
        self.setScene(self.scene)

        self.parm = parm # type: hou.Parm
        self.screen = screen

        geometry = screen.geometry()

        if sys.platform == "darwin":
            self.screen_pixmap = screen.grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())
        else:
            self.screen_pixmap = screen.grabWindow(0)

        self.screen_image = self.screen_pixmap.toImage() # type: QImage

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameStyle(QFrame.NoFrame)
        self.scene.clear()
        self.setGeometry(screen.geometry())
        
        self.setSceneRect(0, 0, self.screen_pixmap.width(), self.screen_pixmap.height())
        self.scene.addPixmap(self.screen_pixmap)

        self.setMouseTracking(True)
        self.color_info = ColorInformation()
        self.scene.addItem(self.color_info)

        self.gradient_edit = gradient_edit
        self.ramp_sketch = ramp_sketch

        self.path = QPainterPath()
        self.draw_path = False

        self.path_item = QGraphicsPathItem()
        if not self.ramp_sketch:
            self.path_item.setPen(QPen(QColor(0, 200, 100, 200), 2))
        else:
            self.path_item.setPen(QPen(QColor(200, 200, 50, 255), 4))
        self.scene.addItem(self.path_item)

        self.colors = [] # type: list[QColor]
        self.positions = [] # type: list[QPoint]
        self.picked_color = QColor()

        self.disable_gamma_correction = False

        if self.underMouse():
            self.color_info.show()
        else:
            self.color_info.hide()

        self.is_macos = sys.platform == "darwin"

        # TODO: ???
        if self.is_macos:
            self.color_info.show()

        if self.ramp_sketch:
            self.color_info.hide()

    def update_info(self, pos):
        image_pos = pos * self.screen.devicePixelRatio()
        if self.screen_image.rect().contains(image_pos):
            self.color_info.color = QColor(self.screen_image.pixel(image_pos.x(), image_pos.y()))
        self.color_info.setPos(pos)
        self.color_info.pos = pos

    def write_ramp_sketch(self):
        if len(self.positions) < 2:
            return

        positions = np.array([
            (float(p.x()), float(-p.y())) 
            for p in self.positions
        ]) 

        min_point = positions.min(axis=0)
        max_point = positions.max(axis=0)

        ramp_range = max_point - min_point

        if not np.any((ramp_range == 0.0)):
            norm_positions = (positions - min_point) / ramp_range

            geo_points = []
            geo_points.append(hou.Vector3(norm_positions[0][0], norm_positions[0][1], 0.0))
            left = 0.0
            for pt in norm_positions[1:-1]:
                if pt[0] >= left:
                    left = pt[0]
                    geo_points.append(hou.Vector3(pt[0], pt[1], 0.0))
                
            geo_points.append(hou.Vector3(norm_positions[-1][0], norm_positions[-1][1], 0.0))

            ramp_geo = hou.Geometry() # type: hou.Geometry
            ramp_points = ramp_geo.createPoints(geo_points)
            ramp_geo.createPolygons((ramp_points,), False)

            resample_verb = hou.sopNodeTypeCategory().nodeVerb("resample") # type: hou.SopVerb
            resample_verb.setParms({
                "length": 0.04
            })

            resample_verb.execute(ramp_geo, [ramp_geo])

            facet_verb = hou.sopNodeTypeCategory().nodeVerb("facet") # type: hou.SopVerb
            facet_verb.setParms({
                "inline": 1,
                "inlinedist": 0.003
            })

            facet_verb.execute(ramp_geo, [ramp_geo])

            ramp_poly = ramp_geo.prim(0)
            ramp_points = ramp_poly.points()

            ramp_basis = hou.rampBasis.BSpline if self.disable_gamma_correction else hou.rampBasis.Linear

            basis = []
            keys = []
            values = []

            for point in ramp_points: # type: hou.Point
                basis.append(ramp_basis)
                pos = point.position()
                keys.append(pos.x())
                values.append(pos.y())

            ramp = hou.Ramp(basis, keys, values)
            self.parm.set(ramp)
            self.parm.pressButton()
        

    def write_color_ramp(self):
        if len(self.colors) < 2:
            return

        color_points = []

        vlast_color = hou.Vector3(hou.qt.fromQColor(self.colors[0])[0].rgb())
        last_color_index = 0

        color_points.append((vlast_color, 0))

        # remove same keys in a row
        for index, color in enumerate(self.colors[1:]):
            color_index = index + 1
            vcolor = hou.Vector3(hou.qt.fromQColor(color)[0].rgb())
            dist = vcolor.distanceTo(vlast_color)

            if dist > TOLERANCE:
                # if color_index - last_color_index > 1 and dist > SHARP_PRECISION:
                #     color_points.append((hou.Vector3(vlast_color), color_index - 1))
                color_points.append((hou.Vector3(vcolor), color_index))
                vlast_color = vcolor
                last_color_index = color_index
       
        if color_points[-1][1] < (len(self.colors) - 1):
            color_points.append((hou.Vector3(hou.qt.fromQColor(self.colors[-1])[0].rgb()), len(self.colors) - 1))

        # Create a polyline representing ramp and remove inline points with Facet SOP
        points = [color_point[0] for color_point in color_points]
        pos = [color_point[1] for color_point in color_points]

        ramp_geo = hou.Geometry()

        pos_attrib = ramp_geo.addAttrib(hou.attribType.Point, "ramp_pos", 0.0, create_local_variable=False)

        ramp_points = ramp_geo.createPoints(points)
        fnum_points = float(len(self.colors) - 1)

        for ptnum, point in enumerate(ramp_points): # type: (int, hou.Point)
            point.setAttribValue(pos_attrib, float(pos[ptnum]) / fnum_points)

        ramp_poly = ramp_geo.createPolygons(
            (ramp_points,), False
        ) [0] # type: hou.Face

        facet_verb = hou.sopNodeTypeCategory().nodeVerb("facet") # type: hou.SopVerb

        facet_verb.setParms({
            "inline": 1,
            "inlinedist": 0.02
        })
        

        facet_verb.execute(ramp_geo, [ramp_geo])

        ramp_poly = ramp_geo.prim(0)
        ramp_points = ramp_poly.points()

        linear = hou.rampBasis.Linear

        basis = []
        keys = []
        values = []

        pos_attrib = ramp_geo.findPointAttrib("ramp_pos")

        for point in ramp_points: # type: hou.Point
            basis.append(linear)
            keys.append(point.attribValue(pos_attrib))
            values.append(tuple(point.position()))

        if not self.disable_gamma_correction:
            values = [np.power(v, 2.2) for v in values]

        ramp = hou.Ramp(basis, keys, values)
        self.parm.set(ramp)
        self.parm.pressButton()


    def enterEvent(self, event):
        if not self.ramp_sketch:
            self.color_info.show()
    
    def leaveEvent(self, event):
        self.color_info.hide()

    def mouseMoveEvent(self, event):
        pos = event.pos() #* self.screen.devicePixelRatio()
        self.update_info(pos)

        # TODO: ???
        if self.is_macos and not self.ramp_sketch:
            self.color_info.show()

        if self.draw_path:
            path = self.path_item.path()
            path.lineTo(pos)
            self.path_item.setPath(path)
            self.colors.append(self.color_info.color)
            self.positions.append(pos)

        return QGraphicsView.mouseMoveEvent(self, event)
    
    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.ShiftModifier:
            self.disable_gamma_correction = True

        if self.gradient_edit or self.ramp_sketch:
            self.draw_path = True
            self.path.moveTo(event.pos())
            self.path_item.setPath(self.path)
        else:
            self.picked_color = self.color_info.color

    def mouseReleaseEvent(self, event):
        if self.gradient_edit and self.draw_path:
            self.write_color_ramp()
        elif self.ramp_sketch and self.draw_path:
            self.write_ramp_sketch()
        elif not self.gradient_edit:
            out_color = hou.qt.fromQColor(self.picked_color)[0].rgb()
            if not self.disable_gamma_correction:
                out_color = np.power(out_color, 2.2)

            self.parm.set(out_color)

        if self.parent() is not None:
            self.parent().mouseReleaseEvent(event)

class ScreensMain(QMainWindow):
    def __init__(self, parm, gradient_edit, ramp_sketch, parent=None, screen=None):
        super(ScreensMain, self).__init__(parent)

        app = QApplication.instance() # type: QApplication
        screens = app.screens()
        cursor_pos = QCursor.pos()

        screen_to_attach = screens[0] if screen is None else screen

        view = ScreenshotView(self, screen_to_attach, parm, gradient_edit, ramp_sketch)
        self.view = view
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setCentralWidget(view)
        self.setGeometry(screen_to_attach.geometry())
        self.show()
        view.update_info(cursor_pos)

        self.setMouseTracking(True)
        self.additional_windows = []

        cursor = hou.qt.getCursor("cross")
        self.setCursor(cursor)

        if screen_to_attach.geometry().contains(cursor_pos) and not ramp_sketch:
            view.color_info.show()
        else:
            view.color_info.hide()        

        if screen is None:
            for screen in screens[1:]:
                additional_window = ScreensMain(parm, gradient_edit, ramp_sketch, self, screen)
                self.additional_windows.append(additional_window)

    def close_all(self):
        self.close()
        if self.parent() is not None:
            self.parent().close()

        children = self.findChildren(ScreensMain)
        if children:
            for child in children:
                child.close()

        if sys.platform == "darwin":
            global form
            del form
            
    def mouseReleaseEvent(self, event):
        self.close_all()

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if not modifiers & Qt.ShiftModifier:
            self.close_all()


def show_color_picker(parm):
    parm_tuple = parm.tuple()
    if parm_tuple is not None:
        global form
        form = ScreensMain(parm_tuple, False, False)
        form.show()

def show_gradient_picker(parm):
    global form
    form = ScreensMain(parm, True, False)
    form.show()

def show_ramp_sketch(parm):
    global form
    form = ScreensMain(parm, False, True)
    form.show()