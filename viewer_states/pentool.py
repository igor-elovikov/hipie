"""
State:          Pen
State type:     ie::pen_tool
Description:    Pen Tool
Author:         elovikov
Date Created:   August 17, 2020 - 14:07:37
"""

import hou
import json
import string
import math
import numpy as np
import functools as ft
import itertools as it
import viewerstate.utils as su

from collections import Iterable
from collections import namedtuple
from copy import deepcopy

ONE_THIRD = 0.333333333333333333

pen_tool_type = hou.nodeType(hou.sopNodeTypeCategory(), "ie::pen_tool::1.0")
phm = pen_tool_type.hdaModule()  

pcontrol_params = {
    "num_rings": 2,
    "radius": 9,
    "color1": (1.0,1.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.RingsSquare,
    "falloff_range": (0.35, 0.95),
    "num_rings": 1,
    "fade_factor": 1.0,
}
 
pcontrol_hover_params = {
    "radius": 14,
    "color1": (1.0,1.0,0.0,1.0),
    "falloff_range": (0.15, 0.99),
}

pcontrol_selected_params = {
    "radius": 4,
    "color1": (0.0,1.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.SmoothSquare,
    "falloff_range": (0.95, 0.95),
}

handle_params = {
    "num_rings": 2,
    "radius": 6,
    "color1": (1.0,1.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.SmoothCircle,
    "falloff_range": (0.95, 0.95),
    "num_rings": 1,
    "fade_factor": 1.0,
}

handle_hover_params = {
    "radius": 8,
    "color1": (1.0,1.0,0.0,1.0),
    "falloff_range": (0.95, 0.99),
}

handle_selected_params = {
    "radius": 6,
    "color1": (1.0,1.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.SmoothCircle
}

handle_line_params = {
    "color1": (1.0,1.0,0.0,1.0),
    "line_width": 1.0,
    "glow_width": 0.0,
    "fade_factor": 1.0,
}

def lerp(fr, to, f):
    return fr + (to - fr) * f

# expecting normalized 
def look_at(to, up):
    # type: (hou.Vector3, hou.Vector3) -> hou.Matrix3
    right = up.cross(to) # type: hou.Vector3
    right = right.normalized()
    up = to.cross(right)

    return hou.Matrix3((right.x(), right.y(), right.z(), up.x(), up.y(), up.z(), to.x(), to.y(), to.z()))

def node_input(node, input_idx):
    # type: (hou.Node, int) -> hou.Node
    version = hou.applicationVersion()

    if version[0] == 18 and version[1] == 5:
        return  node.input(input_idx)

    elif version[0] == 18 and version[1] == 0:
        input_node = None # type: hou.SopNode
        connections = node.inputConnections() # type: list[hou.InputConnection]

        for connection in connections: # type: hou.InputConnection
            if connection.inputIndex() == 0:
                input_node = connection.inputNode()

        return input_node
    
    return None




text_styles = {
    "bold": ("<b>", "</b>"),
    "italic": ("<i>", "</i>"),
    "subscript": ("<sub>", "</sub>"),
    "superscript": ("<sup>", "</sup>")
}

class ProjectionType:
    FREE = 0
    PLANE_XY = 1
    PLANE_XZ = 2
    PLANE_YZ = 3

    plane_normal = [
        None, hou.Vector3(0, 0, 1), hou.Vector3(0, 1, 0), hou.Vector3(1, 0, 0)
    ]

    plane_transform = [
        None, hou.hmath.identityTransform(), hou.hmath.buildRotateAboutAxis(hou.Vector3(1, 0, 0), 90), hou.hmath.buildRotateAboutAxis(hou.Vector3(0, 1, 0), 90)
    ]

# Drawable Group for Texts
class TextDrawableGroup(object):

    class Text(object):

        def __init__(self, text="", position=hou.Vector3(0.0, 0.0, 0.0), size=3, color="cyan", font="Source Code Pro"):
            # type: (str, hou.Vector3) -> None
            self.text = text
            self.position = position
            self.drawable = None # type: hou.TextDrawable
            self.styles = ["bold"]
            self.font = font
            self.color = color
            self.size = size

        def format_text(self):
            text_open = "<font size={} color={} face='{}'>".format(self.size, self.color, self.font) + "".join([text_styles[s][0] for s in self.styles] )
            text_close = "".join([text_styles[s][1] for s in reversed(self.styles)]) + "</font>"
            formatted_text = text_open + self.text + text_close
            self.drawable.setParams({"text": formatted_text})

        def format_text_nocolor(self):
            text_open = "<font size={} face='{}'>".format(self.size, self.font) + "".join([text_styles[s][0] for s in self.styles] )
            text_close = "".join([text_styles[s][1] for s in reversed(self.styles)]) + "</font>"
            formatted_text = text_open + self.text + text_close
            self.drawable.setParams({"text": formatted_text})

        def set_text(self, text):
            self.text = text
            self.format_text_nocolor()

        def set_colored_text(self, text):
            self.text = text
            self.format_text()

        def add_style(self, style):
            if style not in self.styles:
                self.styles.append(style)

    def __init__(self, scene_viewer):
        self.texts = [] # type: list[TextDrawableGroup.Text]
        self.params = {}
        self.scene_viewer = scene_viewer # type: hou.SceneViewer
        self.global_size = 3
        self.global_color = hou.Color(1.0, 1.0, 1.0)
        self.visible = False

    def create_text_drawable(self, text):
        text_id = "Text_" + str(hash(self)) + "_" + str(hash(text))
        text.drawable = hou.TextDrawable(self.scene_viewer, text_id)
        text.drawable.setParams(self.params)
        text.drawable.show(self.visible)

    def add_text(self, text):
        # type: (TextDrawableGroup.Text) -> None
        self.texts.append(text)
        self.create_text_drawable(text)
        text.format_text()

    def allocate_texts(self, length):
        self.texts = []
        for _ in range(length):
            text = TextDrawableGroup.Text()
            text.size = self.global_size
            self.texts.append(text)
            self.create_text_drawable(text)
            text.drawable.setParams({"color1": self.global_color})
    
    def set_color(self, color):
        for text in self.texts:
            text.color = color

    def set_size(self, size):
        for text in self.texts:
            text.size = size

    def set_params(self, params, index=None):
        self.params = params

        if index is None:
            for text in self.texts:
                text.drawable.setParams(params)
        elif index >= 0 and index < len(self.texts):
            self.texts[index].setParams(params)

    def draw(self, handle):

        for text in self.texts:
            text.drawable.setParams({"translate": text.position})
            text.drawable.draw(handle)

    def show(self, visible):
        self.visible = visible
        for text in self.texts:
            text.drawable.show(visible)



# Simple point control with callbacks on moving
class PointControl(object):

    def __init__(self, position = hou.Vector3(0, 0, 0), drawable_index=0, tag=""):
        self.world_position = position
        self.drawable_index = drawable_index
        self.is_visible = True
        self._on_move = None
        self._on_select = None
        self.tag = tag

    def move_to(self, position):
        self.world_position = position
        if self._on_move:
            self._on_move(position)

# Drawable container for point cotrols
class PointControlDrawable(object):

    def __init__(self, name, scene_viewer):
        self.name = name
        self.scene_viewer = scene_viewer

        self._points_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, name + "_points_geo_drawable") # type: hou.GeometryDrawable
        self._hovered_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, name + "_hovered_drawable") # type: hou.GeometryDrawable
        self._selected_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, name + "_hovered_drawable") # type: hou.GeometryDrawable

    def set_drawing_params(self, params):
        self._points_drawable.setParams(params)
        self._hovered_drawable.setParams(params)
        self._selected_drawable.setParams(params)

    def set_hovered_params(self, params):
        self._hovered_drawable.setParams(params)

    def set_selected_params(self, params):
        self._selected_drawable.setParams(params)

    def draw(self, handle):
        self._points_drawable.draw(handle)
        self._hovered_drawable.draw(handle)
        self._selected_drawable.draw(handle)


# Container of point controls. Handling drawing, dragging etc
class PointControlGroup(object):

    def __init__(self, scene_viewer, projection_mode=ProjectionType.FREE):
        self.scene_viewer = scene_viewer # type: hou.SceneViewer
       
        self.point_controls = [] # type: list[PointControl]
        self.drawables = [] # type: list[PointControlDrawable]

        self.selected_controls = [] # type: list[PointControl]
        self.hovered_control = None # type: PointControl
        self.dragged_control = None # type: PointControl
        self.hover_tolerance = 100.0

        self._points_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, "points_geo_drawable") # type: hou.GeometryDrawable
        self._hovered_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, "hovered_drawable") # type: hou.GeometryDrawable
        self._selected_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, "hovered_drawable") # type: hou.GeometryDrawable

        self.dragging = False
        self.plane_point = hou.Vector3()

        self.projection_mode = projection_mode
        self.enable_snapping = True
        self.surface_geo = None # type: hou.Geometry
        self.surface_normal_attrib = False # hou.Attrib
        self.surface_normal = None # type: hou.Vector3

    def clear_controls(self):
        self.point_controls = []
        self.selected_controls = []
        self.dragged_control = None
        self.hovered_control = None
        self.dragging = False
        self.update_points_geo()
        self.update_hovered_geo()
        self.update_selected_geo()

    def add_drawable(self, name):
        self.drawables.append(PointControlDrawable(name, self.scene_viewer))

    def get_drawable(self, name):
        # type: (str) -> PointControlDrawable
        return next((d for d in self.drawables if d.name == name))
    
    def get_drawable_index(self, name):
        # type: (str) -> int
        return next(i for i, d in enumerate(self.drawables) if d.name == name)

    def set_drawing_params(self, name, params):
        drawable = self.get_drawable(name)
        drawable.set_drawing_params(params)
        
    def set_hovered_params(self, name, params):
        drawable = self.get_drawable(name)
        drawable.set_hovered_params(params)

    def set_selected_params(self, name, params):
        drawable = self.get_drawable(name)
        drawable.set_selected_params(params)

    def update_points_geo(self):
        for index, drawable in enumerate(self.drawables):
            geo = hou.Geometry()
            point_positions = [control.world_position for control in self.point_controls if control.drawable_index == index and control.is_visible]
            geo.createPoints(point_positions)
            drawable._points_drawable.setGeometry(geo)

    def update_hovered_geo(self):
        for index, drawable in enumerate(self.drawables):
            geo = hou.Geometry()
            if self.hovered_control and index == self.hovered_control.drawable_index:
                geo.createPoints([self.hovered_control.world_position])
            drawable._hovered_drawable.setGeometry(geo) 

    def show_hovered(self, show):
        for drawable in self.drawables:
            drawable._hovered_drawable.show(show)

    def update_selected_geo(self):
        for index, drawable in enumerate(self.drawables):
            point_positions = [c.world_position for c in self.selected_controls if c.drawable_index == index and c.is_visible]
            geo = hou.Geometry()
            if point_positions:
                geo.createPoints(point_positions)
            drawable._selected_drawable.setGeometry(geo)

    def add_control(self, position, drawable_index=0, tag=""):
        # type: (hou.Vector3) -> PointControl
        control = PointControl(position, drawable_index, tag)
        self.point_controls.append(control)
        return control
 
    def hover_points(self, ui_event):
        # type: (hou.UIEvent) -> None

        max_distance = self.hover_tolerance + 0.1
        prev_control = self.hovered_control

        self.hovered_control = None
        for point_control in self.point_controls: # type: int, PointControl
            if not point_control.is_visible:
                continue

            viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport
            point_screen_pos = viewport.mapToScreen(point_control.world_position * viewport.modelToGeometryTransform().inverted()) # type: hou.Vector2

            dev = ui_event.device() # type: hou.UIEventDevice

            mouse_pos = hou.Vector3(dev.mouseX(), dev.mouseY(), 0.0)
            mouse_pos *= viewport.windowToViewportTransform()
            mouse_pos = hou.Vector2(mouse_pos.x(), mouse_pos.y())

            distance_to_cursor = (point_screen_pos - mouse_pos).lengthSquared()

            if distance_to_cursor < self.hover_tolerance and distance_to_cursor < max_distance:
                self.hovered_control = point_control
                max_distance = distance_to_cursor

        if self.hovered_control and self.hovered_control is not prev_control:
            self.update_hovered_geo()
            self.show_hovered(True)
        
        if not self.hovered_control:
            self.show_hovered(False)

    def select_point(self):
        # type: () -> PointControl
        if self.hovered_control:
            if self.hovered_control._on_select:
                self.hovered_control._on_select()
            return self.hovered_control
        else:
            return None

    def select_control(self, point_control):
        # type (PointControl) -> None
        self.selected_controls[:] = []
        self.selected_controls.append(point_control)
        self.dragged_control = point_control
        self.update_selected_geo()

    def unselect_control(self, point_control):
        if point_control in self.selected_controls:
            self.selected_controls.remove(point_control)

    def add_control_to_selection(self, point_control, update_geo=True):
        if point_control not in self.selected_controls:
            self.selected_controls.append(point_control)
            if update_geo:
                self.update_selected_geo()

    def clear_selection(self):
        self.selected_controls[:] = []
        self.update_selected_geo()
    
    def on_mouse_move(self, ui_event):
        # type: (hou.UIEvent) -> None
        if not self.dragging:
            self.hover_points(ui_event)
        else:
            self.on_mouse_drag(ui_event)

    def get_construction_point(self, ui_event):
        # type (hou.UIEvent) -> hou.Vector3

        self.surface_normal = None
        snapping_ray = None
        if self.enable_snapping:
            snapping_ray = ui_event.snappingRay()
            origin, direction = snapping_ray["origin_point"], snapping_ray["direction"] # type: hou.Vector3, hou.Vector3
        else:
            origin, direction = ui_event.ray()

        # construction_point = su.cplaneIntersection(self.scene_viewer, origin, direction) # type: hou.Vector3

        viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport
        view_transform = viewport.viewTransform() # type: hou.Matrix4

        plane_point = self.plane_point # hou.Vector3(0, 0, 0)
        plane_normal = ProjectionType.plane_normal[self.projection_mode]

        if self.projection_mode == ProjectionType.FREE:

            camera_pos = hou.Vector3(0, 0, 0) * view_transform # type: hou.Vector3
            camera_look =  hou.Vector3(0, 0, -1) * view_transform - camera_pos # type: hou.Vector3

            plane_point = self.plane_point
            plane_normal = camera_look

            cplane = self.scene_viewer.constructionPlane() # type: hou.ConstructionPlane

            if cplane.isVisible():
                cplane_transform = cplane.transform() # type: hou.Matrix4
                plane_point = hou.Vector3(0, 0, 0) * cplane_transform
                plane_normal = hou.Vector3(0, 0, 1) * cplane_transform.inverted().transposed()

        try:
            construction_point = hou.hmath.intersectPlane(plane_point, plane_normal, origin, direction)
        except TypeError:
            construction_point = None

            version = hou.applicationVersion()
            if version[0] == 18 and version[1] == 5:
                self.scene_viewer.flashMessage("NETVIEW_error_badge", "Construction plane is not reachable!", 2.0)

        if snapping_ray is not None:
            try:

                snapped = snapping_ray["snapped"]

                if snapped:
                    geo_type = snapping_ray["geo_type"] # type: hou.snappingPriority
                    if geo_type == hou.snappingPriority.GridPoint:
                        construction_point = snapping_ray["grid_pos"]
                    if geo_type == hou.snappingPriority.GeoPoint:
                        geo = hou.nodeBySessionId(snapping_ray["node_id"]).geometry()
                        geo_point = geo.point(snapping_ray["point_index"])
                        construction_point = geo_point.position()
                    if geo_type == hou.snappingPriority.GeoPrim:
                        geo = hou.nodeBySessionId(snapping_ray["node_id"]).geometry()
                        prim_index = snapping_ray["prim_index"]
                        geo_prim = geo.prim(prim_index) # type: hou.Prim

                        position = hou.Vector3()
                        normal = hou.Vector3()
                        uvw = hou.Vector3()

                        intersect_prim = geo.intersect(origin, direction, position, normal, uvw, str(geo_prim))
                        if intersect_prim == prim_index:
                            construction_point = position # geo_prim.positionAtInterior(uvw.x(), uvw.y(), uvw.z())
            except TypeError:
                construction_point = None

        if self.surface_geo is not None and self.enable_snapping:

            gi = su.GeometryIntersector(self.surface_geo, tolerance=0.02)
            gi.intersect(origin, direction)

            if gi.prim_num > -1:
                
                hit_prim = self.surface_geo.prim(gi.prim_num) # type: hou.Prim
                construction_point = hit_prim.positionAtInterior(gi.uvw[0], gi.uvw[1], gi.uvw[2])

                if self.surface_normal_attrib is not None:
                    self.surface_normal = hou.Vector3(hit_prim.attribValueAtInterior(self.surface_normal_attrib, gi.uvw[0], gi.uvw[1], gi.uvw[2]))
                

        return construction_point

    def on_mouse_drag(self, ui_event):
        # type: (hou.UIEvent) -> None
        if not self.selected_controls or self.dragged_control is None:
            return

        construction_point = self.get_construction_point(ui_event)

        if construction_point is not None:

            self.dragged_control.move_to(construction_point)

            self.update_points_geo()
            self.update_hovered_geo()
            self.update_selected_geo()

    def on_mouse_down(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.dragging = True
        
    def on_mouse_up(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.dragging = False
        
    def draw(self, handle):
        for drawable in self.drawables:
            drawable._points_drawable.draw(handle)
            drawable._hovered_drawable.draw(handle)
            drawable._selected_drawable.draw(handle)

    def show(self, visible):
        for drawable in self.drawables:
            drawable._points_drawable.show(visible)
            drawable._selected_drawable.show(visible)
        self.show_hovered(self.hovered_control is not None)
       


class AnchorType:
    SMOOTH = 0
    CORNER = 1
    UNTIED = 2

class AnchorAttributeType:
    PSCALE_AND_ROLL = -1
    INTEGER_LADDER = 0
    FLOAT_LADDER = 1
    FLOAT_ROLL = 2
    FLOAT_SCALE = 3
    VECTOR_UP = 4
    VECTOR_ARBITRARY = 5
    ORIENTATION = 6

    # attributes metadata (default, parm type, size, handle name, formatter)
    meta = {
        PSCALE_AND_ROLL: ([1.0, 0.0], "attrib_float_value{}", 2, ("pscale_handle", "spin_handle"), "({:.2f}, {:.2f})"),
        INTEGER_LADDER: (0, "attrib_int_value{}", 1, ("None",), "{}"),
        FLOAT_LADDER: (1.0, "attrib_float_value{}", 1, ("None",), "{:.2f}"),
        FLOAT_ROLL: (0.0, "attrib_float_value{}", 1, ("spin_handle",), "{:.2f}"),
        FLOAT_SCALE: (1.0, "attrib_float_value{}", 1, ("pscale_handle",), "{:.2f}"),
        VECTOR_UP: (0.0, "attrib_float_value{}", 1, ("spin_handle",), "{:.2f}"),
        VECTOR_ARBITRARY: ([0.0, 1.0, 0.0], "attrib_vector_value{}", 3, ("vector_handle",), "({:.2f}, {:.2f}, {:.2f})"),
        ORIENTATION: ([0.0, 0.0, 0.0], "attrib_vector_value{}", 3, ("angle_handle",), "({:.2f}, {:.2f}, {:.2f})")
    }

    parm_names = ["attrib_vector2_value{}", "attrib_int_value{}", "attrib_vector_value{}", "attrib_float_value{}"]

    @staticmethod
    def default_value(attribute_type):
        default_value = AnchorAttributeType.meta[attribute_type][0]
        tuple_size = AnchorAttributeType.meta[attribute_type][2]
        return list(default_value) if tuple_size > 1 else default_value

class AnchorAttribute(object):
    def __init__(self, attr_type):
        self.type = attr_type
        self.value = AnchorAttributeType.meta[attr_type][0]

    def interpolate(self, fr, to, factor):
        if self.type == AnchorAttributeType.PSCALE_AND_ROLL:
            return [lerp(fr[0], to[0], factor), lerp(fr[1], to[1], factor)]

        if self.type == AnchorAttributeType.VECTOR_ARBITRARY:
            dihedral = hou.Quaternion()
            frv = hou.Vector3(fr)
            tov = hou.Vector3(to)
            dihedral.setToVectors(frv, tov)

            rotation = hou.Quaternion()
            rotation = rotation.slerp(dihedral, factor) # type: hou.Quaternion
            
            return list(rotation.rotate(frv))

        if self.type == AnchorAttributeType.ORIENTATION:
            frq = hou.Quaternion()
            frq.setToEulerRotates(fr)

            toq = hou.Quaternion()
            toq.setToEulerRotates(to)

            rotation = frq.slerp(toq, factor) # type: hou.Quaternion
           
            return list(rotation.extractEulerRotates())

        if isinstance(fr, float):
            return lerp(fr, to, factor)
        else:
            return int(np.round(lerp(fr, to, factor)))

#TODO: this one duplicates state export (not sure what to do but at least remove interpolating duplicate)
def rebuild_geo_from_json(data):
    # type: (str) -> hou.Geometry
    
    anchors = data["anchors"]
    attrib_meta = data["attrib_meta"]
    prims = data["prims"]

    curve_geo = hou.Geometry()

    attrib_types = {}

    for attrib_data in attrib_meta:
        attrib_name = attrib_data[0]
        attrib_type = attrib_data[1]
        curve_geo.addAttrib(hou.attribType.Point, attrib_name, AnchorAttributeType.meta[attrib_type][0], create_local_variable=False)
        attrib_types[attrib_name] = attrib_type

    roll_attribs = [attrib_name for attrib_name in attrib_types if attrib_types[attrib_name] == AnchorAttributeType.VECTOR_UP]
    orient_attribs = [attrib_name for attrib_name in attrib_types if attrib_types[attrib_name] == AnchorAttributeType.ORIENTATION]

    if roll_attribs:
        curve_geo.addAttrib(hou.attribType.Global, "roll_attribs", "", create_local_variable=False)
        curve_geo.setGlobalAttribValue("roll_attribs", " ".join(roll_attribs))

    if orient_attribs:
        curve_geo.addAttrib(hou.attribType.Global, "orient_attribs", "", create_local_variable=False)
        curve_geo.setGlobalAttribValue("orient_attribs", " ".join(orient_attribs))

    curve_geo.addAttrib(hou.attribType.Prim, "name", "", create_local_variable=False)


    for prim_num, prim in enumerate(prims):

        prim_points = [anchor["controls"][index] for anchor in anchors[prim[0]:prim[1]] for index in range(3)]
        prim_attribs = [(anchor_index, attrib_index) for anchor_index in range(prim[0], prim[1]) for attrib_index in range(3)]

        for anchor_index in range(prim[0], prim[1]):
            
            prev_index = anchor_index - 1 if anchor_index > prim[0] else prim[1] - 1 if prim[2] else None
            next_index = anchor_index + 1 if anchor_index < prim[1] - 1 else prim[0] if prim[2] else None

            anchors[anchor_index]["interp_attribs"] = {}
            
            for attrib_name in attrib_types:

                attribute = AnchorAttribute(attrib_types[attrib_name])
                attrib_value = anchors[anchor_index]["attribs"][attrib_name]
                attribute.value = attrib_value

                if attribute.type != AnchorAttributeType.INTEGER_LADDER:
                    prev_value = attribute.interpolate(attrib_value, anchors[prev_index]["attribs"][attrib_name], ONE_THIRD) if prev_index is not None else attrib_value
                    next_value = attribute.interpolate(attrib_value, anchors[next_index]["attribs"][attrib_name], ONE_THIRD) if next_index is not None else attrib_value
                else:
                    prev_value = anchors[prev_index]["attribs"][attrib_name] if prev_index is not None else attrib_value
                    next_value = attrib_value
                
                anchors[anchor_index]["interp_attribs"][attrib_name] = (prev_value, attrib_value, next_value)


        if (prim[1]-prim[0]) > 1:
            prim_export_points = prim_points[1:-1]
            prim_export_attribs = prim_attribs[1:-1]

            # if closed
            if prim[2]:
                prim_export_points.extend((prim_points[-1], prim_points[0]))
                prim_export_attribs.extend((prim_attribs[-1], prim_attribs[0]))
            
            bezier_prim = curve_geo.createBezierCurve(len(prim_export_points), prim[2], 4) # type: hou.Face
            bezier_prim.setAttribValue("name", prim[3])

            for ptnum, point in enumerate(bezier_prim.points()): # type: int, hou.Point
                point.setPosition(prim_export_points[ptnum])
                
                anchor_index = prim_export_attribs[ptnum][0]
                control_index = prim_export_attribs[ptnum][1]

                for attrib_name in attrib_types:
                    attrib_value = anchors[anchor_index]["interp_attribs"][attrib_name][control_index]
                    point.setAttribValue(attrib_name, attrib_value)
    

    return curve_geo

def sync_attributes_with_node(node):
    # type: (hou.Node) -> None

    controls = node.parm("controls").evalAsString()

    if not len(controls):
        return

    data = json.loads(controls)

    anchors = data["anchors"]
    attrib_meta = data["attrib_meta"]

    num_attributes = node.parm("num_attributes").evalAsInt()

    attribute_names = [node.parm("attr_name_{}".format(i + 1)).evalAsString() for i in range(num_attributes)]
    attribute_types = [node.parm("attr_type_{}" .format(i + 1)).evalAsInt() for i in range(num_attributes)]

    # add missing attributes (also reset type mismatch)
    for i in range(num_attributes):
        attribute_name = attribute_names[i] 
        attribute_type = attribute_types[i]
        
        if attribute_name != "__pr":

            attrib_missing = not any((True for a in attrib_meta if a[0] == attribute_name))
            type_mismatch = False
            if not attrib_missing:
                meta_type = next((a[1] for a in attrib_meta if a[0] == attribute_name))
                type_mismatch = meta_type != attribute_type
            
            if attrib_missing or type_mismatch:
                if attrib_missing:
                    attrib_meta.append([attribute_name, attribute_type])
                if type_mismatch:
                    a = next(a for a in attrib_meta if a[0] == attribute_name)
                    a[1] = attribute_type
                for anchor in anchors:
                    anchor["attribs"][attribute_name] = AnchorAttributeType.default_value(attribute_type)

    for attribute_name, attribute_type in attrib_meta:
        if attribute_name not in attribute_names and attribute_name != "__pr":
            for anchor in anchors:
                if attribute_name in anchor["attribs"]:
                    del anchor["attribs"][attribute_name]

    data["attrib_meta"] = [a for a in attrib_meta if a[0] in attribute_names or a[0]=="__pr"]

    node.parm("controls").set(json.dumps(data))

    geo = rebuild_geo_from_json(data)

    node.parm("stash").set(geo)
    node.parm("guide_stash").set(geo)


# Anchor for Bezier curve
class AnchorPoint(object):

    def __init__(self):
        self.position = hou.Vector3()
        self.controls = [hou.Vector3(), hou.Vector3()]
        self.anchor_type = AnchorType.SMOOTH
        self.tag = ""
        self.attributes = {} 
        self.interpolated_attribs = {}

        self.geo_points = []
        self.anchor_index = -1

    def __getitem__(self, key):
        if key == 0:
            return self.controls[0]
        elif key == 1:
            return self.position
        return self.controls[1]

    @property
    def in_control(self):
        return self.controls[0]
    
    @property
    def out_control(self):
        return self.controls[1]

    def move_control(self, control_index, new_position, aligned=True, symmetric=False, rotate_corner=False):
        # type: (int, hou.Vector3, bool) -> None
        if control_index not in [0, 1]:
            return

        old_position = self.controls[control_index]
        self.controls[control_index] = new_position            

        if aligned:
            other_index = 0 if control_index == 1 else 1
            if symmetric:
                other_gradient = (new_position - self.position).length()
            else:
                other_gradient = (self.controls[other_index] - self.position).length()
            other_control_direction = -(new_position - self.position).normalized()
            self.controls[other_index] = self.position + other_gradient * other_control_direction

        if rotate_corner:
            other_index = 0 if control_index == 1 else 1
            other_gradient = self.controls[other_index] - self.position

            rotation = hou.Quaternion()
            old_direction = (old_position - self.position).normalized()
            new_direction = (new_position - self.position).normalized()
            rotation.setToVectors(old_direction, new_direction)

            other_gradient = rotation.rotate(other_gradient)
            self.controls[other_index] = self.position + other_gradient

    def move_anchor(self, new_position):
        # type: (hou.Vector3) -> None
        diff = new_position - self.position

        self.position += diff
        
        self.controls[0] += diff
        self.controls[1] += diff

CustomShapeAnchor = namedtuple("CustomShapeAnchor", ["in_control", "position", "out_control", "anchor_type"])

UNTIE_TOLERANCE = 0.0001
CORNER_TOLERANCE = 0.0000001

class CustomShape:

    def __init__(self):
        self.anchors = [] # type: list[CustomShapeAnchor]
        self.is_closed = False

    def read_from_prim(self, prim):
        # type: (hou.Face) -> None
        self.anchors = []
        self.is_closed = prim.isClosed()
        prim_center = prim.boundingBox().center()
        shape_points = [point.position() - prim_center for point in prim.points()] # type: list[hou.Vector3]

        if self.is_closed:
            shape_points = [shape_points[-1]] + shape_points[:-1]
        else:
            first_control = 2.0 * shape_points[0] - shape_points[1]
            last_control = 2.0 * shape_points[-1] - shape_points[-2]
            shape_points = [first_control] + shape_points + [last_control]

        for anchor_index in range(0, len(shape_points), 3):

            in_control = shape_points[anchor_index] # type: hou.Vector3
            position_control = shape_points[anchor_index + 1] # type: hou.Vector3
            out_control = shape_points[anchor_index + 2] # type: hou.Vector3

            in_direction = position_control - in_control
            out_direction = out_control - position_control

            anchor_type = AnchorType.UNTIED
            anchor_type = AnchorType.SMOOTH if abs(in_direction.normalized().dot(out_direction.normalized()) - 1.0) < UNTIE_TOLERANCE else anchor_type
            anchor_type = AnchorType.CORNER if (in_direction.lengthSquared() + out_direction.lengthSquared()) < CORNER_TOLERANCE else anchor_type

            self.anchors.append(CustomShapeAnchor(in_control, position_control, out_control, anchor_type))

# Main editor class
class BezierEditor(object):

    def __init__(self, scene_viewer):
        self.scene_viewer = scene_viewer # type: hou.SceneViewer
        self.node = None # type: hou.Node
        self.resampled_guide_node = None # type: hou.SopNode
        
        self.closed_parm = None # type: hou.Parm
        self.controls_parm = None # type: hou.Parm
        self.geo_stash = None # type: hou.Parm
        self.guide_stash = None # type: hou.Parm

        self.editing_anchor = -1
        self.editable_handles = () # type: list[AnchorPoints]
        self.handle_points = [] # type: list[hou.Vector3]
        self.handle_lines = []
        self.curve_prim_under_cursor = None # type: int

        self.curve_pos_under_cursor = None # type: float
        self.symmetric_handle_move = False
        self.aligned_handle_move = True
        self.rotate_corner_mode = False
        self.adding_anchor = False

        self.edit_transaction = False
        self.update_geo_on_edit = False
        self.control_clicked = False
        self.control_moved = False
        self.new_anchor_added = False
        self.draw_mode = True

        self.use_curve_guides = False
        self.use_arrow_heads = False
        self.handles_snapping = True

        # Anchors
        self.anchor_points = [] # type: list[AnchorPoint]
        self.anchor_points_controls = {} # type: dict[AnchorPoint, list[PointControl]]

        # Attributes
        self.attribute_names = {} # type: dict[str, AnchorAttribute]
        
        # Editor controls
        self.point_controls = PointControlGroup(scene_viewer)
        self.current_handle_controls = [] # type: list[PointControl]

        # Prims
        # Controls stored as flat list so prims are just ranges
        self.prims = []
        self.geo_prims = []
        self.selection = []
        self.curve_geo = None # type: hou.Geometry

        # Custom shapes dict
        self.custom_shapes = {} # type: dict[str, CustomShape]
        
        self.curve_geo_dirty = False
        self.attribs_dirty = True
        self.names_dirty = True
        self.tags_dirty = True
        self.disable_control_sync = False

        self.point_controls.add_drawable("anchors")
        self.point_controls.add_drawable("handles")

        self.point_controls.set_drawing_params("anchors", pcontrol_params)
        self.point_controls.set_hovered_params("anchors", pcontrol_hover_params)
        self.point_controls.set_selected_params("anchors", pcontrol_selected_params)

        self.point_controls.set_drawing_params("handles", handle_params)
        self.point_controls.set_hovered_params("handles", handle_hover_params)
        self.point_controls.set_selected_params("handles", handle_selected_params)

        # Text drawers
        self.attrib_value_drawer = TextDrawableGroup(self.scene_viewer)
        self.attrib_value_drawer.set_params({
            'color1' : (1.0,1.0,1.0, 1.0),
            'color2' : (0.0,0.0,0.0, 1.0),
            'origin' : hou.drawableTextOrigin.UpperLeft,
            'margins': hou.Vector2(10, -5),
            'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
            "glow_width": 1.0,
        })
        self.attrib_value_drawer.show(True)

        self.prim_names_drawer = TextDrawableGroup(self.scene_viewer)
        self.prim_names_drawer.set_params({
            'color1' : (1.0,1.0,1.0, 1.0),
            'color2' : (0.0,0.0,0.0, 1.0),
            'origin' : hou.drawableTextOrigin.BottomRight,
            'margins': hou.Vector2(-15, 5),
            'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
            "glow_width": 1.0,
        })
        self.prim_names_drawer.show(True)

        self.anchor_tags_drawer = TextDrawableGroup(self.scene_viewer)
        self.anchor_tags_drawer.set_params({
            'color1' : (1.0,1.0,1.0, 1.0),
            'color2' : (0.0,0.0,0.0, 1.0),
            'origin' : hou.drawableTextOrigin.BottomLeft,
            'margins': hou.Vector2(10, 5),
            'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
            "glow_width": 1.0,
        })
        self.anchor_tags_drawer.show(True)


        self.current_attribute = None
        self.current_attribute_class = None

        self.multiselect_box = None

        # Handles lines geo
        self._handles_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Line, "handles_geo_drawable") # type: hou.GeometryDrawable
        self._handles_drawable.setParams(handle_line_params)

        # Curve drawable
        curve_drawable_params = {
            "color1": (0.0,0.75,1.0,1.0),
            "line_width": 1.8,
            "glow_width": 0.0,
            "fade_factor": 0.8,
        }
        self._curve_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Line, "curve_drawable") # type: hou.GeometryDrawable
        self._curve_drawable.setParams(curve_drawable_params)
        self._arrowhead_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Face, "arrowhead_drawable") # type: hou.GeometryDrawable
        heads_drawable_params = {
            "color1": (0.0,0.75,1.0,1.0),
            "fade_factor": 0.8,
        }        
        self._arrowhead_drawable.setParams(heads_drawable_params)

        selection_drawable_params = {
            "color1": (0.3,0.9,0.6,1.0),
            "line_width": 1.0,
            "glow_width": 0.0,
            "fade_factor": 1.0,
        }
        self._selection_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Line, "selection_drawable") # type: hou.GeometryDrawable
        self._selection_drawable.setParams(selection_drawable_params)
        self.selection_mode = 0
        self.selection_start_anchors = []
        self.selection_start = None 
        self.selection_viewport = None # type: hou.GeometryViewport

        # Houdini handles
        self.point_translate_handle = None # type: hou.Handle
        self.spin_handle = None # type: hou.Handle
        self.pscale_handle = None # type: hou.Handle

        # Multi-selection data
        self.selection_box_positions = []
        self.selection_box_size = hou.Vector3()
        self.reset_selection_box = False

    def set_display_settings(self):

        guides_color = list(self.node.parmTuple("guides_color").eval()) + [1.0]
        controls_color = list(self.node.parmTuple("controls_color").eval()) + [1.0]
        selected_color = list(self.node.parmTuple("selected_color").eval()) + [1.0]
        names_color = list(self.node.parmTuple("names_color").eval()) + [1.0]
        attribs_color = list(self.node.parmTuple("attribs_color").eval()) + [1.0]


        controls_size = self.node.parm("controls_size").eval()
        text_size = self.node.parm("text_size").eval()
        names_size = self.node.parm("names_size").eval()

        self._arrowhead_drawable.setParams(
            {
                
                "color1": guides_color
            }
        )

        self._curve_drawable.setParams(
            {
                "color1": guides_color,
                "line_width": self.node.parm("guides_thickness").eval()
            }
        )

        self.point_controls.set_drawing_params("anchors", {
            "color1": controls_color,
            "radius": controls_size 
        })
        self.point_controls.set_hovered_params("anchors", {
            "color1": controls_color,
            "radius": controls_size * 1.5555
        })
        self.point_controls.set_selected_params("anchors", {
            "color1": selected_color,
            "radius": controls_size * 0.55
        })

        self.point_controls.set_drawing_params("handles", {
            "color1": controls_color,
            "radius": controls_size * 0.666
        })
        self.point_controls.set_hovered_params("handles", {
            "color1": controls_color,
            "radius": controls_size * 0.9
        })
        self.point_controls.set_selected_params("handles", {
            "color1": controls_color,
            "radius": controls_size * 0.666
        })

        self._handles_drawable.setParams(
            {
                "color1": controls_color
            }
        )

        self.attrib_value_drawer.global_size = text_size
        self.attrib_value_drawer.set_size(text_size)

        self.prim_names_drawer.global_size = names_size
        self.prim_names_drawer.set_size(names_size)

        self.anchor_tags_drawer.global_size = names_size
        self.anchor_tags_drawer.set_size(names_size)

        controls_color_parms = {"color1": controls_color}
        names_color_parms = {"color1": names_color}
        attribs_color_parms = {"color1": attribs_color}

        self.anchor_tags_drawer.global_color = controls_color
        for text in self.anchor_tags_drawer.texts:
            text.drawable.setParams(controls_color_parms)

        self.prim_names_drawer.global_color = names_color
        for text in self.prim_names_drawer.texts:
            text.drawable.setParams(names_color_parms)

        self.attrib_value_drawer.global_color = attribs_color
        for text in self.attrib_value_drawer.texts:
            text.drawable.setParams(attribs_color_parms)

        self.attribs_dirty = True
        self.tags_dirty = True
        self.names_dirty = True


    def process_custom_shapes(self):

        shapes_input = node_input(self.node, 0)

        if shapes_input is not None:

            shapes_geo = shapes_input.geometry() # type: hou.Geometry
            name_attrib = shapes_geo.findPrimAttrib("name") # type: hou.Attrib

            if name_attrib is not None:

                shapes_prims = [prim for prim in shapes_geo.prims() if prim.type() == hou.primType.BezierCurve] # type: list[hou.Prim]

                for shape_prim in shapes_prims:
                    if "order" in shape_prim.intrinsicNames() and shape_prim.intrinsicValue("order") == 4:
                        custom_shape = CustomShape()
                        custom_shape.read_from_prim(shape_prim)
                        shape_name = shape_prim.stringAttribValue(name_attrib)
                        self.custom_shapes[shape_name] = custom_shape

    def select_custom_shape(self):

        if not self.custom_shapes:
            version = hou.applicationVersion()
            if version[0] == 18 and version[1] == 5:
                self.scene_viewer.flashMessage("NETVIEW_error_badge", "No shapes found!", 2.0)
            return None

        shape_names = self.custom_shapes.keys()
        shape = hou.ui.selectFromList(shape_names, (0,), exclusive=True, title="Select Shape", clear_on_cancel=True, column_header="Shapes")
        
        return shape_names[shape[0]] if shape else None

    def insert_custom_shape(self, position, surface_normal, shape_name):
        # type: (hou.Vector3, str) -> None

        if shape_name not in self.custom_shapes:
            return

        shape = self.custom_shapes[shape_name]
        numpt = len(self.anchor_points)

        self.begin_edit()

        self.prims.append([numpt, numpt + len(shape.anchors), shape.is_closed, shape_name])
        primnum = len(self.prims) - 1

        plane_transform = hou.hmath.identityTransform()

        if self.point_controls.projection_mode == ProjectionType.FREE:
            cplane = self.scene_viewer.constructionPlane() # type: hou.ConstructionPlane
            viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport
            plane_transform = cplane.transform if cplane.isVisible() else viewport.viewTransform() # type: hou.Matrix4
            plane_transform = hou.hmath.buildRotate(plane_transform.extractRotates())
        else:
            plane_transform = ProjectionType.plane_transform[self.point_controls.projection_mode]

        if surface_normal is not None:
            plane_transform = hou.hmath.buildRotateZToAxis(surface_normal)

        for anchor in shape.anchors: # type: CustomShapeAnchor
            new_anchor = AnchorPoint()

            self.anchor_points.append(new_anchor)

            new_anchor.anchor_type = anchor.anchor_type
            new_anchor.position = position + anchor.position * plane_transform
            new_anchor.controls[0] = position + anchor.in_control * plane_transform
            new_anchor.controls[1] = position + anchor.out_control * plane_transform
            
            self.add_anchor_controls(new_anchor)
            self.sync_anchor_controls(new_anchor)
            self.reset_anchor_attributes(new_anchor)

        self.update_anchors_indices()
        self.select_prim(primnum)
        self.end_edit()

        self.allocate_names_drawer()
        self.allocate_value_drawer()
        self.attribs_dirty = True

        self.on_anchor_selected()
        self.update_all_editor_geo()

    def duplicate_prim(self, position, prim_index):

        prim = self.prims[prim_index]
        prim_len = prim[1] - prim[0]

        if prim_len < 2:
            return
        
        self.begin_edit()

        prim_anchors = self.anchor_points[prim[0]:prim[1]]
        numpt = len(self.anchor_points)

        prim_points_pos = [anchor.position for anchor in prim_anchors]
        prim_center = hou.Vector3(np.mean(prim_points_pos, axis=0))
        
        self.prims.append([numpt, numpt + prim_len, prim[2], prim[3]])
        primnum = len(self.prims) - 1

        for anchor in prim_anchors:

            new_anchor = AnchorPoint()

            self.anchor_points.append(new_anchor)

            new_anchor.anchor_type = anchor.anchor_type
            new_anchor.position = position + (anchor.position - prim_center)
            new_anchor.controls[0] = position + (anchor.controls[0] - prim_center)
            new_anchor.controls[1] = position + (anchor.controls[1] - prim_center)

            new_anchor.attributes = deepcopy(anchor.attributes)

            self.add_anchor_controls(new_anchor)
            self.sync_anchor_controls(new_anchor)

        self.update_anchors_indices()
        self.select_prim(primnum)
        self.end_edit()

        self.allocate_names_drawer()
        self.allocate_value_drawer()
        self.attribs_dirty = True

        self.on_anchor_selected()
        self.update_all_editor_geo()
        

    def add_default_attributes(self):
        self.add_attribute("__pr", AnchorAttributeType.PSCALE_AND_ROLL)

    def add_attribute(self, attribute_name, attribute_type):
        if attribute_name not in self.attribute_names:
            self.attribute_names[attribute_name] = AnchorAttribute(attribute_type)
            for anchor in self.anchor_points:
                anchor.attributes[attribute_name] = AnchorAttributeType.default_value(attribute_type) 

    def reset_anchor_attributes(self, anchor):
        # type: (AnchorPoint) -> None
        for attribute_name in self.attribute_names:
            anchor.attributes[attribute_name] = AnchorAttributeType.default_value(self.attribute_names[attribute_name].type) 

    def allocate_value_drawer(self):
        num_anchors = len(self.anchor_points)
        self.attrib_value_drawer.allocate_texts(num_anchors)
        self.anchor_tags_drawer.allocate_texts(num_anchors)
        self.attribs_dirty = True
        self.tags_dirty = True

    def allocate_names_drawer(self):
        self.prim_names_drawer.allocate_texts(len(self.prims))
        self.prim_names_drawer.set_color("pink")
        self.names_dirty = True

    def sync_names_drawer(self):

        if self.curve_geo is None:
            return

        if self.names_dirty:

            self.names_dirty = False

            for index, prim in enumerate(self.prims):
                value_text = self.prim_names_drawer.texts[index]
                value_text.set_text(prim[3])

        viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport

        curve_prims = self.curve_geo.prims()

        geo_prim_index = 0       

        for index, prim in enumerate(self.prims):
            value_text = self.prim_names_drawer.texts[index]

            if prim[1] - prim[0] > 1:
                
                geo_prim = curve_prims[geo_prim_index] # type: hou.Prim
                geo_prim_index += 1
                prim_pos = geo_prim.boundingBox().center() if prim[2] else geo_prim.positionAtInterior(0.5, 0.0)
                value_pos = viewport.mapToScreen(prim_pos)
                value_text.position = hou.Vector3(value_pos.x(), value_pos.y(), 0.0)
            else:
                value_pos = viewport.mapToScreen(self.anchor_points[prim[0]].position)
                value_text.position = hou.Vector3(value_pos.x(), value_pos.y(), 0.0)

    def sync_attrib_value_drawer(self, attribute_name):

        if self.attribs_dirty:

            self.attribs_dirty = False

            attribute_type = self.attribute_names[attribute_name].type
            formatter = AnchorAttributeType.meta[attribute_type][4]

            for index, anchor in enumerate(self.anchor_points):
                value_text = self.attrib_value_drawer.texts[index]
                value = anchor.attributes[attribute_name]
                formatted_attrib = formatter.format(*value) if isinstance(value, Iterable) else formatter.format(value)
                value_text.set_text(formatted_attrib)
        
        viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport

        for index, anchor in enumerate(self.anchor_points):
            value_text = self.attrib_value_drawer.texts[index]
            anchor_screen_pos = viewport.mapToScreen(anchor.position)
            value_text.position = hou.Vector3(anchor_screen_pos.x(), anchor_screen_pos.y(), 0)

    def sync_tags_drawer(self):

        if self.tags_dirty:
            
            self.tags_dirty = False

            for index, anchor in enumerate(self.anchor_points):
                value_text = self.anchor_tags_drawer.texts[index]
                value_text.set_text(anchor.tag)

        viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport

        for index, anchor in enumerate(self.anchor_points):
            value_text = self.anchor_tags_drawer.texts[index]
            anchor_screen_pos = viewport.mapToScreen(anchor.position)
            value_text.position = hou.Vector3(anchor_screen_pos.x(), anchor_screen_pos.y(), 0)


    def add_attributes_from_node(self):

        num_attributes = self.node.parm("num_attributes").evalAsInt()

        for i in range(1, num_attributes + 1):
            attrib_name = self.node.parm("attr_name_{}".format(i)).evalAsString()
            attrib_type = self.node.parm("attr_type_{}".format(i)).evalAsInt()

            self.add_attribute(attrib_name, attrib_type)

    def calculate_multiselect_box(self):
        selected_controls = self.point_controls.selected_controls

        if len(selected_controls) < 2:
            self.multiselect_box = None
            return

        selected_positions = [control.world_position for control in selected_controls]

        max_pos = hou.Vector3(np.max(selected_positions, axis=0))
        min_pos = hou.Vector3(np.min(selected_positions, axis=0))

        origin = (min_pos + max_pos) * 0.5
        size = (max_pos - origin) * 2.0

        self.multiselect_box = (origin, size)
        self.selection_box_size = size

        self.selection_box_positions = []

        for control in selected_controls:
            anchor = self.get_anchor_from_control(control)
            self.selection_box_positions.append((anchor[0]-origin, anchor[1]-origin, anchor[2]-origin))

        self.reset_selection_box = True

    def get_current_attribute(self):
        attribute_name = self.node.parm("current_attribute").evalAsString()
        self.current_attribute = self.current_attribute_class = None
        if attribute_name != "None" and attribute_name in self.attribute_names:
            self.current_attribute = attribute_name
            self.current_attribute_class = self.attribute_names[attribute_name]

    def interpolate_anchor_attributes(self, anchor, anchor_index):
        prev_index = self.get_prev_index(anchor_index)
        next_index = self.get_next_index(anchor_index)

        for attrib_name in self.attribute_names:
            attribute = self.attribute_names[attrib_name]
            attrib_value = anchor.attributes[attrib_name]
            if attribute.type != AnchorAttributeType.INTEGER_LADDER:
                prev_value = attribute.interpolate(attrib_value, self.anchor_points[prev_index].attributes[attrib_name], ONE_THIRD) if prev_index is not None else attrib_value
                next_value = attribute.interpolate(attrib_value, self.anchor_points[next_index].attributes[attrib_name], ONE_THIRD) if next_index is not None else attrib_value
            else:
                prev_value = self.anchor_points[prev_index].attributes[attrib_name] if prev_index is not None else attrib_value
                next_value = attrib_value
            anchor.interpolated_attribs[attrib_name] = (prev_value, next_value)

    def interpolate_all_attributes(self):
        if not self.anchor_points:
            return

        if len(self.anchor_points) == 1:
            for attrib_name in self.attribute_names:
                self.anchor_points[0].interpolated_attribs[attrib_name] = (
                    self.anchor_points[0].attributes[attrib_name],
                    self.anchor_points[0].attributes[attrib_name]
                )
            return

        for index, anchor in enumerate(self.anchor_points):
            self.interpolate_anchor_attributes(anchor, index)
             

    def begin_edit(self):
        self.state.log("Start edit transaction")
        self.edit_transaction = True
        self.scene_viewer.beginStateUndo("IE|Pen: Curve Modify")

    def end_edit(self):
        # commit changes
        self.edit_transaction = False
        self.rebuild_geo()
        self.save_anchor_points()
        self.scene_viewer.endStateUndo()

        self.state.log("End edit transaction")

    def attach_node(self, node, state):
        # type: (hou.Node, State) -> None
        self.node = node
        self.state = state
        self.resampled_guide_node = node.node("GUIDE")

        self.closed_parm = self.node.parm("close") # type: hou.Parm
        self.controls_parm = self.node.parm("controls") # type: hou.Parm
        self.geo_stash = self.node.parm("stash")
        self.guide_stash = self.node.parm("guide_stash")

        self.point_controls.projection_mode = self.node.parm("drawing_mode").eval()
        
        self.use_curve_guides = self.node.parm("use_curve_guide").eval()
        self.use_arrow_heads = self.node.parm("use_arrow_heads").eval()
        self.update_geo_on_edit = self.node.parm("update_geo_on_edit").eval()
        self.handles_snapping = self.node.parm("handles_snapping").eval()

        self.reads(self.controls_parm.evalAsString())
        resampled_guide_geo = self.resampled_guide_node.geometry()
        self._curve_drawable.setGeometry(resampled_guide_geo)
       
        self.show_editing_handles()
        self.sync_parmpane_with_selection()        
        self.allocate_value_drawer()
        self.allocate_names_drawer()

        self.process_custom_shapes()

        self.draw_mode = not bool(self.anchor_points)

        self.set_display_settings()

    def reset(self):
        self.attribute_names = {}
        self.point_controls.clear_controls()
        self.anchor_points = []
        self.editing_anchor = -1
        self.show_editing_handles()
        self.update_handles_geo()
        self.control_moved = False
        self.allocate_value_drawer()
        self.allocate_names_drawer()

    def writes(self):
        # type: () -> (str, str)

        anchors = [
            {
                "controls": [tuple(anchor[index]) for index in range(3)],
                "attribs": anchor.attributes,
                "flag": anchor.anchor_type,
                "tag": anchor.tag
            } for anchor in self.anchor_points]

        attrib_meta = [(name, self.attribute_names[name].type) for name in self.attribute_names]
        prims = self.prims

        selection = []
        selected_controls = self.point_controls.selected_controls
        if selected_controls:
            for control in selected_controls:
                anchor = self.get_anchor_from_control(control)
                selection.append(anchor.anchor_index)

        data = {
            "attrib_meta": attrib_meta,
            "anchors": anchors,
            "prims": prims,
            "selection": selection
        }

        return json.dumps(data)

    def reads(self, state, update_geo=True):
        # type: ((str, str)) -> None

        self.state.log("Read data from controls parm")

        if not len(state):
            self.add_default_attributes()
            self.add_attributes_from_node()
            return

        data = json.loads(state)

        anchors = data["anchors"]
        attrib_meta = data["attrib_meta"]

        if not len(anchors):
            self.add_default_attributes()
            self.add_attributes_from_node()
            return

        self.reset()

        self.prims = data["prims"]
        self.selection = data["selection"] if "selection" in data else []

        for attrib in attrib_meta:
            self.add_attribute(attrib[0], attrib[1])

        self.add_attributes_from_node()

        for anchor_index, anchor in enumerate(anchors):
            anchor_point = AnchorPoint()
            
            anchor_point.controls[0] = hou.Vector3(anchor["controls"][0])
            anchor_point.controls[1] = hou.Vector3(anchor["controls"][2])
            anchor_point.position = hou.Vector3(anchor["controls"][1])
            anchor_point.anchor_type = anchor["flag"]
            anchor_point.tag = anchor["tag"] if "tag" in anchor else ""

            self.anchor_points.append(anchor_point)

            anchor_point.attributes = anchor["attribs"]
            self.add_anchor_controls(anchor_point, update_geo=False)

        self.point_controls.update_points_geo()

        self.rebuild_geo(False)

        self.allocate_value_drawer()
        self.allocate_names_drawer()
        self.update_anchors_indices()

    def get_editing_anchor_from_selection(self):
        selected_controls = self.point_controls.selected_controls

        if len(selected_controls) > 1:
            self.editing_anchor = -1
            return

        for index, anchor in enumerate(self.anchor_points):
            if any((True for c in self.anchor_points_controls[anchor] if c in selected_controls)):
                self.editing_anchor = index
                break
        else:
            self.editing_anchor = -1

    def get_anchor_from_control(self, control):
        # type: (PointControl) -> AnchorPoint
        return next(anchor for anchor in self.anchor_points if control in self.anchor_points_controls[anchor])

    def need_handles(self, anchor):
        # type: (AnchorPoint) -> AnchorPoint
        return anchor if anchor is not None and anchor.anchor_type != AnchorType.CORNER else None

    def get_editing_anchors(self):
        if self.editing_anchor < 0:
            self.editable_handles = (None, None, None)
            return
        
        editing_anchor = self.anchor_points[self.editing_anchor]
        in_anchor = self.get_prev_anchor(editing_anchor)
        out_anchor = self.get_next_anchor(editing_anchor)
        
        self.editable_handles = (
            self.need_handles(in_anchor), 
            self.need_handles(editing_anchor), 
            self.need_handles(out_anchor)
        )

    def get_anchor_prim(self, anchor_index):
        # type: (int) -> int
        return next((index for index in range(len(self.prims)) 
            if anchor_index>=self.prims[index][0] and anchor_index<self.prims[index][1] ), 
            None)

    # get prim to add (at begin or end) from selected anchor
    def get_prim_to_add_anchor(self, anchor_index):
        selected_prim = self.get_anchor_prim(anchor_index)
        if self.prims[selected_prim][2]:
            return None, None
        prim = next((index for index in range(len(self.prims)) 
            if anchor_index==self.prims[index][0] or anchor_index==(self.prims[index][1]-1) ), 
            None)
        at_end = None
        if prim is not None:
            at_end = anchor_index == (self.prims[prim][1] - 1)

        return prim, at_end

    def sort_prims_after_insert(self, insert_index):
        prim = self.get_anchor_prim(insert_index)
        if prim is not None:
            self.prims[prim][1] += 1
            for p in range(prim+1, len(self.prims)):
                self.prims[p][0] += 1
                self.prims[p][1] += 1
        else:
            prim = next((index for index in range(len(self.prims)) 
                if insert_index==self.prims[index][0] and insert_index==self.prims[index][1] ), 
                None)
            if prim is not None:
                self.prims[prim][1] += 1

    def sort_prims_after_delete(self, delete_index):
        prim = self.get_anchor_prim(delete_index)

        if prim is not None:
            self.prims[prim][1] -= 1
            for p in range(prim+1, len(self.prims)):
                self.prims[p][0] -= 1
                self.prims[p][1] -= 1

            if self.prims[prim][1] == self.prims[prim][0]:
                del self.prims[prim]

    def update_anchors_indices(self):
        for anchor_index, anchor in enumerate(self.anchor_points):
            anchor.anchor_index = anchor_index

    def hide_all_handles(self):
        for control in self.point_controls.point_controls: # type: PointControl
            control.is_visible = False if control.drawable_index == 1 else control.is_visible

    def restore_selection(self):
        for selection_index in self.selection:
            anchor_control = self.anchor_points_controls[self.anchor_points[selection_index]][2]
            self.point_controls.add_control_to_selection(anchor_control)

        self.update_all_editor_geo()
        self.on_anchor_selected()

    def show_editing_handles(self):

        self.hide_all_handles()
        self.get_editing_anchors()

        if self.editable_handles[0] is not None:
            out_control = self.anchor_points_controls[self.editable_handles[0]][1] 
            out_control.is_visible = True

        if self.editable_handles[1] is not None:
            in_control = self.anchor_points_controls[self.editable_handles[1]][0]
            out_control = self.anchor_points_controls[self.editable_handles[1]][1]
            in_control.is_visible = out_control.is_visible = True

        if self.editable_handles[2] is not None:
            in_control = self.anchor_points_controls[self.editable_handles[2]][0]
            in_control.is_visible = True

        self.point_controls.update_points_geo()

    def update_all_editor_geo(self):
        self.get_editing_anchor_from_selection()
        self.show_editing_handles()

        self.point_controls.update_points_geo()
        self.point_controls.update_hovered_geo()
        self.point_controls.update_selected_geo()

        self.update_handles_geo()
    
    def update_handles_geo(self):
        geo = hou.Geometry()

        geo_points = []
        geo_lines = []

        if self.editable_handles[0] is not None:
            out_control = self.anchor_points_controls[self.editable_handles[0]][1]
            geo_points.extend((self.editable_handles[0].position, out_control.world_position))
            geo_lines.append((0, 1))

        if self.editable_handles[1] is not None:
            geo_points_len = len(geo_points)
            in_control = self.anchor_points_controls[self.editable_handles[1]][0]
            out_control = self.anchor_points_controls[self.editable_handles[1]][1]
            geo_points.extend((in_control.world_position, self.editable_handles[1].position, out_control.world_position))
            geo_lines.append((geo_points_len, geo_points_len + 1, geo_points_len + 2))

        if self.editable_handles[2] is not None:
            geo_points_len = len(geo_points)
            in_control = self.anchor_points_controls[self.editable_handles[2]][0]
            geo_points.extend((self.editable_handles[2].position, in_control.world_position))
            geo_lines.append((geo_points_len, geo_points_len + 1))

        geo.createPoints(geo_points)
        geo.createPolygons(geo_lines, False)
        
        self._handles_drawable.setGeometry(geo)

    def sync_anchor_controls(self, anchor):
        self.anchor_points_controls[anchor][0].world_position = anchor.controls[0]
        self.anchor_points_controls[anchor][1].world_position = anchor.controls[1]
        self.anchor_points_controls[anchor][2].world_position = anchor.position

    def update_anchor_position(self, anchor, new_position):
        # type: (AnchorPoint, hou.Vector3) -> None
        diff = new_position - anchor.position
        anchor.move_anchor(new_position)

        self.update_anchor_geo_position(anchor)

        self.sync_anchor_controls(anchor)
        if len(self.point_controls.selected_controls) > 1:
            for control in self.point_controls.selected_controls:
                selected_anchor = self.get_anchor_from_control(control)
                if selected_anchor is not anchor:
                    selected_anchor.move_anchor(selected_anchor.position + diff)
                    
                    self.update_anchor_geo_position(selected_anchor)
                    
                    self.sync_anchor_controls(selected_anchor)
            
            self.point_controls.update_points_geo()
            self.point_controls.update_selected_geo()

        self.update_handles_geo()

    def update_anchor_control_position(self, anchor, control_index, new_position):
        # type: (AnchorPoint, int, hou.Vector3) -> None
        if not self.aligned_handle_move:
            anchor.anchor_type = AnchorType.UNTIED

        anchor.move_control(control_index, new_position, self.aligned_handle_move, self.symmetric_handle_move, self.rotate_corner_mode)
        self.update_anchor_geo_position(anchor)
        self.sync_anchor_controls(anchor)
        self.update_handles_geo()

    def is_anchor_selected(self, anchor):
        # type: (AnchorPoint) -> bool
        if not self.point_controls.selected_controls:
            return False
        elif any((True for c in self.anchor_points_controls[anchor] if c in self.point_controls.selected_controls)):
            return True
        return False

    def close_prim(self, prim_index, is_closed):
        self.prims[prim_index][2] = is_closed
        self.rebuild_geo()
        self.update_all_editor_geo()

    def reverse_prim(self, prim_index):
        prim = self.prims[prim_index]

        if prim[1] - prim[0] > 1:
            self.anchor_points[prim[0]:prim[1]] = self.anchor_points[prim[0]:prim[1]][::-1]
            self.update_anchors_indices()

            for anchor in self.anchor_points[prim[0]:prim[1]]:
                anchor.controls = anchor.controls[::-1]
                #anchor.tag = tag
                self.sync_anchor_controls(anchor)

        self.on_anchor_selected()

        self.attribs_dirty = True    
        self.tags_dirty = True    
        self.rebuild_geo()
        self.update_all_editor_geo()

    def rewire_prim(self, anchor_index):
        prim = self.prims[self.get_anchor_prim(anchor_index)]

        if prim[1] - prim[0] > 1:
            anchors_before = self.anchor_points[prim[0]:anchor_index]
            self.anchor_points[prim[0]:prim[0] + prim[1] - anchor_index] = self.anchor_points[anchor_index:prim[1]]
            self.anchor_points[prim[0] + prim[1] - anchor_index:prim[1]] = anchors_before

            self.update_anchors_indices()

            for anchor in self.anchor_points[prim[0]:prim[1]]:
                self.sync_anchor_controls(anchor)

        self.on_anchor_selected()

        self.attribs_dirty = True
        self.tags_dirty = True             
        self.rebuild_geo()
        self.update_all_editor_geo()


    def remove_prim(self, prim_index):
        if prim_index >= len(self.prims):
            return
        while self.prims[prim_index][1] - self.prims[prim_index][0] > 1:
            self.remove_anchor(self.anchor_points[self.prims[prim_index][0]], False)
        
        self.get_editing_anchor_from_selection()
        self.remove_anchor(self.anchor_points[self.prims[prim_index][0]])

    def straighten_anchors(self):

        selected_controls = self.point_controls.selected_controls
        if len(selected_controls) < 2:
            return

        selected_anchors = [self.get_anchor_from_control(control) for control in selected_controls]
        anchors_indicies = sorted([anchor.anchor_index for anchor in selected_anchors])

        # get sequences for straighten
        straighten_seqs = it.groupby(enumerate(anchors_indicies), lambda ia: (self.get_anchor_prim(ia[1]), ia[0] - ia[1]))
        straighten_seqs = [[a[1] for a in seq] for k, seq in straighten_seqs]

        if not any(len(s) > 1 for s in straighten_seqs):
            return

        self.begin_edit()

        for anchors in straighten_seqs:

            if len(anchors) > 1:

                num_segments = len(anchors) - 1

                start_anchor = self.anchor_points[anchors[0]]
                end_anchor = self.anchor_points[anchors[-1]]

                line = end_anchor.position - start_anchor.position
                line_direction = line.normalized()
                segment_length = line.length() / num_segments
                segment = line_direction * segment_length
                gradient = line_direction * (segment_length / 3)

                if start_anchor.anchor_type != AnchorType.CORNER:
                    start_anchor.anchor_type = AnchorType.UNTIED
                    start_anchor.controls[1] = start_anchor.position + gradient
                    self.sync_anchor_controls(start_anchor)

                if end_anchor.anchor_type != AnchorType.CORNER:
                    end_anchor.anchor_type = AnchorType.UNTIED
                    end_anchor.controls[0] = end_anchor.position - gradient
                    self.sync_anchor_controls(end_anchor)

                for segment_index, anchor_index in enumerate(anchors[1:-1]):
                    anchor = self.anchor_points[anchor_index]
                    anchor.position = start_anchor.position + segment * (segment_index + 1)
                    if anchor.anchor_type != AnchorType.CORNER:
                        anchor.anchor_type = AnchorType.UNTIED
                        anchor.controls[0] = anchor.position - gradient
                        anchor.controls[1] = anchor.position + gradient
                    else:
                        anchor.controls[0] = anchor.position 
                        anchor.controls[1] = anchor.position
                    self.sync_anchor_controls(anchor)
        
        self.end_edit()

        self.update_all_editor_geo() 


    def clear_selection(self):
        self.point_controls.clear_selection()
        self.update_all_editor_geo()
        self.on_anchor_selected()

    def select_all(self):
        self.point_controls.clear_selection()
        for anchor in self.anchor_points:
            anchor_control = self.anchor_points_controls[self.anchor_points[anchor.anchor_index]][2]
            self.point_controls.add_control_to_selection(anchor_control)

        self.update_all_editor_geo()
        self.on_anchor_selected()

    def select_prim(self, prim_index, clear_selection=True):
        if clear_selection:
            self.point_controls.clear_selection()

        for anchor_index in range(self.prims[prim_index][0], self.prims[prim_index][1]):
            anchor_control = self.anchor_points_controls[self.anchor_points[anchor_index]][2]
            self.point_controls.add_control_to_selection(anchor_control)

        self.update_all_editor_geo()
        self.on_anchor_selected()

    def add_prim_to_selection(self, prim_index):
        any_handle_selected = any((c.tag == "handle" for c in self.point_controls.selected_controls))
        empty_selection = not self.point_controls.selected_controls

        if any_handle_selected and not empty_selection:
            self.point_controls.clear_selection()

        self.select_prim(prim_index, clear_selection=False)

    def remove_anchor(self, anchor, update=True):
        # type: (AnchorPoint) -> None

        if update and self.is_anchor_selected(anchor):
            for control in self.anchor_points_controls[anchor]:
                if control is self.point_controls.hovered_control:
                    self.point_controls.hovered_control = None
                self.point_controls.unselect_control(control)

            self.point_controls.update_selected_geo()

        for control in self.anchor_points_controls[anchor]: # type: PointControl
            self.point_controls.point_controls.remove(control)

        anchor_index = self.anchor_points.index(anchor)
        self.sort_prims_after_delete(anchor_index)      

        self.anchor_points.remove(anchor)

        if update:
            self.allocate_value_drawer()
            self.allocate_names_drawer()

            self.update_anchors_indices()
            self.rebuild_geo()
            self.on_anchor_selected()

    def remove_selected_anchors(self):
        if not self.point_controls.selected_controls:
            return False
        
        if not any(c.tag == "position" for c in self.point_controls.selected_controls):
            return False

        selected_controls = list(self.point_controls.selected_controls)

        self.begin_edit()

        for control in selected_controls:
            anchor = self.get_anchor_from_control(control)
            if control is self.point_controls.hovered_control:
                self.point_controls.hovered_control = None
            self.remove_anchor(anchor, False)

        self.clear_selection()

        self.allocate_value_drawer()
        self.allocate_names_drawer()

        self.update_anchors_indices()
        self.rebuild_geo()

        self.end_edit()

        self.point_controls.update_points_geo()
        self.point_controls.update_selected_geo()
        self.point_controls.update_hovered_geo()

        self.editing_anchor = -1
        self.get_editing_anchor_from_selection()
        self.show_editing_handles()
        self.update_handles_geo()

        self.on_anchor_selected()
        
        return True 

    def is_closed(self):
        return self.closed_parm.evalAsInt() > 0

    def get_prev_index(self, index):
        prim = self.get_anchor_prim(index)
        if prim is not None:
            prim = self.prims[prim]
            if index > prim[0]:
                return index - 1
            elif prim[2]: # is prim closed
                return prim[1] - 1
            else:
                return None

        return None

    def get_next_index(self, index):
        prim = self.get_anchor_prim(index)
        if prim is not None:
            prim = self.prims[prim]
            if index < prim[1] - 1:
                return index + 1
            elif prim[2]: # is prim closed
                return prim[0]
            else:
                return None

        return None

    def get_anchor_tangent(self, index):
        # type: () -> hou.Vector3
        anchor = self.anchor_points[index]

        if anchor.anchor_type == AnchorType.SMOOTH or anchor.anchor_type == AnchorType.UNTIED:
            tangent = anchor.controls[1] - anchor.controls[0]
            return tangent.normalized()

        if anchor.anchor_type == AnchorType.CORNER:
            if len(self.anchor_points) == 1:
                return hou.Vector3(0, 0, 1)

            next_index = self.get_next_index(index)
            prev_index = self.get_prev_index(index)

            if next_index is not None and prev_index is not None:
                tangent = self.anchor_points[next_index].position - self.anchor_points[prev_index].position
                return tangent.normalized()
            elif next_index is not None:
                tangent = self.anchor_points[next_index].position - self.anchor_points[index].position
                return tangent.normalized()
            elif prev_index is not None:
                tangent = self.anchor_points[index].position - self.anchor_points[prev_index].position
                return tangent.normalized()
            else:
                return hou.Vector3(0, 0, 1)

    def get_next_anchor(self, anchor):
        current_index = self.anchor_points.index(anchor)
        next_index = self.get_next_index(current_index)
        if next_index is not None:
            return self.anchor_points[next_index]
        else:
            return None

    def get_prev_anchor(self, anchor):
        current_index = self.anchor_points.index(anchor)
        prev_index = self.get_prev_index(current_index)
        if prev_index is not None:
            return self.anchor_points[prev_index]
        else:
            return None

    def anchor_auto_gradient(self, anchor):
        # Catmull-Rom with 0.5 tension
        # TODO: Add parametrization
        
        next_anchor = self.get_next_anchor(anchor)
        prev_anchor = self.get_prev_anchor(anchor)

        next_pos = next_anchor.position if next_anchor is not None else anchor.position
        prev_pos = prev_anchor.position if prev_anchor is not None else anchor.position

        gradient = next_pos - prev_pos # type: hou.Vector3
        
        anchor.controls[0] = anchor.position - 0.25 * gradient
        anchor.controls[1] = anchor.position + 0.25 * gradient

    def make_anchor_smooth(self, anchor):
        anchor.anchor_type = AnchorType.SMOOTH
        self.anchor_auto_gradient(anchor)

    def make_anchor_corner(self, anchor):
        anchor.anchor_type = AnchorType.CORNER
        anchor.controls[0] = anchor.controls[1] = anchor.position

    def set_anchor_type(self, anchor, anchor_type):
        # type: (AnchorPoint, AnchorType) -> None
        if anchor_type == AnchorType.UNTIED:
            if anchor.anchor_type == AnchorType.CORNER:
                self.make_anchor_smooth(anchor)
            anchor.anchor_type = anchor_type

        if anchor_type == AnchorType.SMOOTH:
            self.make_anchor_smooth(anchor)

        if anchor_type == AnchorType.CORNER:
            self.make_anchor_corner(anchor)

        self.sync_anchor_controls(anchor)
        self.update_handles_geo()
        self.point_controls.update_points_geo()
        self.rebuild_geo()
        self.update_all_editor_geo()

    def toggle_anchor_smoothness(self, anchor):
        # type: (AnchorPoint) -> None
        if anchor.anchor_type == AnchorType.CORNER:
            # make it smooth
            self.make_anchor_smooth(anchor)
        else:
            # maket it corny
            self.make_anchor_corner(anchor)

        self.sync_anchor_controls(anchor)
        self.update_handles_geo()
        self.point_controls.update_points_geo()

    def insert_anchor(self, u, geo_prim_num):
        # type: (float) -> AnchorPoint
        curve_sop = self.node.node("curve_geo") # type: hou.SopNode
        curve_geo = curve_sop.geometry() # type: hou.Geometry

        curve_prim = curve_geo.prim(geo_prim_num) # type: hou.Prim
        pos_on_curve = curve_prim.positionAtInterior(u, 0.0, 0.0) # type: hou.Vector3

        prim_num = self.geo_prims[geo_prim_num]
        start_index, end_index, is_closed, prim_name = self.prims[prim_num]
        prim_len = end_index - start_index

        num_segments = prim_len if is_closed else prim_len - 1

        prev_anchor_index = start_index + int( num_segments * u)
        
        next_anchor_index = self.get_next_index(prev_anchor_index)

        if next_anchor_index is None:
            return 

        prev_anchor = self.anchor_points[prev_anchor_index]
        next_anchor = self.anchor_points[next_anchor_index]

        prev_control_pos = prev_anchor.out_control
        next_control_pos = next_anchor.in_control

        prev_anchor_u = (prev_anchor_index - start_index) * 1.0 / num_segments
        next_anchor_u = (next_anchor_index - start_index) * 1.0 / num_segments if next_anchor_index > start_index else 1.0 

        t = (u - prev_anchor_u) / (next_anchor_u - prev_anchor_u) # segment U
        one_m_2 = (1.0 - t) * (1.0 - t)

        gradient_0 = one_m_2 * prev_anchor.position + 2.0 * (1.0 - t) * t * prev_control_pos + t * t * next_control_pos
        gradient_1 = one_m_2 * prev_control_pos + 2.0 * (1.0 - t) * t * next_control_pos + t * t * next_anchor.position

        new_anchor = AnchorPoint()
        new_anchor.position = pos_on_curve
        new_anchor.controls[0] = gradient_0
        new_anchor.controls[1] = gradient_1

        prev_anchor.controls[1] = lerp(prev_anchor.position, prev_anchor.controls[1], t)
        next_anchor.controls[0] = lerp(next_anchor.controls[0], next_anchor.position, t)

        self.sync_anchor_controls(prev_anchor)
        self.sync_anchor_controls(next_anchor)

        if next_anchor_index > prev_anchor_index:
            self.sort_prims_after_insert(prev_anchor_index + 1)
        else:
            self.sort_prims_after_insert(prev_anchor_index)
        self.anchor_points.insert(prev_anchor_index + 1, new_anchor)
        self.add_anchor_controls(new_anchor)

        self.update_anchors_indices()

        self.point_controls.select_control(self.anchor_points_controls[new_anchor][2])
        self.point_controls.plane_point = new_anchor.position        
        self.get_editing_anchor_from_selection()
        self.show_editing_handles()
        self.update_handles_geo()

        self.allocate_value_drawer()
        self.attribs_dirty = True
        self.reset_anchor_attributes(new_anchor)

        for attrib_name in self.attribute_names:
            attribute = self.attribute_names[attrib_name]
            prev_value =  prev_anchor.attributes[attrib_name]
            next_value =  next_anchor.attributes[attrib_name]

            if attribute.type == AnchorAttributeType.INTEGER_LADDER:
                value = prev_anchor.attributes[attrib_name]
            elif attribute.type == AnchorAttributeType.VECTOR_ARBITRARY or attribute.type == AnchorAttributeType.ORIENTATION:
                value = attribute.interpolate(prev_value, next_value, t)
            else:
                prev_prev_anchor = self.get_prev_anchor(prev_anchor)
                next_next_anchor = self.get_next_anchor(next_anchor)

                prev_prev_value = prev_prev_anchor.attributes[attrib_name] if prev_prev_anchor is not None else prev_value
                next_next_value = next_next_anchor.attributes[attrib_name] if next_next_anchor is not None else next_value

                interp_values = (prev_prev_value, prev_value, next_value, next_next_value)

                keys = (0.0, ONE_THIRD, 2.0*ONE_THIRD, 1.0)
                value_ramp = hou.Ramp((hou.rampBasis.CatmullRom,) * 4, keys, interp_values)
                value = value_ramp.lookup((1.0 + t) * ONE_THIRD)
                value = [value[0], value[1]] if attribute.type == AnchorAttributeType.PSCALE_AND_ROLL else value

            new_anchor.attributes[attrib_name] = value

        self.rebuild_geo()
        self.on_anchor_selected()

    def append_anchor(self, pos, anchor_index, at_end, prim_to_add):
        # type (hou.Vector3) -> AnchorPoint
        anchor = AnchorPoint()
        anchor.position = pos
        anchor.controls[0] = anchor.position - hou.Vector3(0.0, 0.0, 0.0)
        anchor.controls[1] = anchor.position + hou.Vector3(0.0, 0.0, 0.0)

        is_new_prim = self.prims[prim_to_add][0] == self.prims[prim_to_add][1]

        self.sort_prims_after_insert(anchor_index)
        insert_index = anchor_index + 1 if at_end else anchor_index
        self.anchor_points.insert(insert_index, anchor)
        
        self.add_anchor_controls(anchor)
        
        self.update_anchors_indices()

        self.editing_anchor = insert_index

        handle_to_select = 1 if at_end or is_new_prim else 0
        self.point_controls.plane_point = pos
        self.point_controls.select_control(self.anchor_points_controls[anchor][handle_to_select])
        
        self.show_editing_handles()
        self.update_handles_geo()

        self.allocate_value_drawer()
        self.attribs_dirty = True
        self.reset_anchor_attributes(anchor)

        self.rebuild_geo()
        self.on_anchor_selected()

    def add_anchor_controls(self, anchor, update_geo=True):
        # type: (AnchorPoint) -> None
        position_control = self.point_controls.add_control(anchor.position, tag="position")
        position_control._on_move = ft.partial(BezierEditor.update_anchor_position, self, anchor)

        in_control = self.point_controls.add_control(anchor.controls[0], 1, tag="handle")
        out_control = self.point_controls.add_control(anchor.controls[1], 1, tag="handle")

        in_control._on_move = ft.partial(BezierEditor.update_anchor_control_position, self, anchor, 0)
        out_control._on_move = ft.partial(BezierEditor.update_anchor_control_position, self, anchor, 1)

        self.anchor_points_controls[anchor] = (in_control, out_control, position_control)
        if update_geo:
            self.point_controls.update_points_geo()

    
    def show_anchor_parms(self, show):
        self.node.parmTuple("anchor_position").hide(not show)
        self.node.parmTuple("anchor_in_control").hide(not show)
        self.node.parmTuple("anchor_out_control").hide(not show)
        self.node.parmTuple("anchor_type").hide(not show)
        self.node.parmTuple("anchor_tag").hide(not show)


    def sync_parmpane_with_selection(self):

        num_attribs_parm = self.node.parm("anchor_attribs")

        sorted_names = ["__pr_scale", "__pr_roll"]
        sorted_names.extend([name for name in self.attribute_names if name != "__pr"])

        selected_controls = self.point_controls.selected_controls
        current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]
        current_anchor = self.get_anchor_from_control(current_control) if current_control is not None else None

        if selected_controls:

            with hou.undos.disabler():

                self.node.parmTuple("tabs").set((0,))

                if len(selected_controls) > 1:
                    self.node.parm("selected_prim_folder").hide(True)
                    self.node.parm("selected_control_label").hide(False)
                    self.node.parm("anchor_attribs").hide(False)
                    self.show_anchor_parms(False)
                    self.node.parmTuple("anchor_tag").hide(False)
                    self.node.parm("anchor_tag").set("")

                    self.node.parm("selected_control_label").set("Multiple Anchors Selected")
                else:
                    self.node.parm("selected_prim_folder").hide(False)
                    self.node.parm("selected_control_label").hide(True)
                    self.node.parm("anchor_attribs").hide(False)
                    self.show_anchor_parms(True)

                    current_prim = self.get_anchor_prim(current_anchor.anchor_index)

                    self.node.parm("prim_closed").set(self.prims[current_prim][2])
                    self.node.parm("prim_name").set(self.prims[current_prim][3])

                    self.node.parmTuple("anchor_position").set(current_anchor.position)
                    self.node.parmTuple("anchor_in_control").set(current_anchor.in_control)
                    self.node.parmTuple("anchor_out_control").set(current_anchor.out_control)

                    self.node.parm("anchor_type").set(current_anchor.anchor_type)
                    self.node.parm("anchor_tag").set(current_anchor.tag)

                num_attribs_parm.set(len(sorted_names))

                for attrib_index, attrib_name in enumerate(sorted_names):
                    
                    if attrib_name in ["__pr_scale", "__pr_roll"]:
                        label = "Pscale"
                        label = "Roll" if attrib_name == "__pr_roll" else label
                        attrib_type = self.attribute_names["__pr"].type
                        attrib_value = current_anchor.attributes["__pr"] if len(selected_controls) < 2 else AnchorAttributeType.meta[attrib_type][0]
                        attrib_value = attrib_value[0] if attrib_name == "__pr_scale" else attrib_value[1]
                    else:
                        attrib_type = self.attribute_names[attrib_name].type
                        attrib_value = current_anchor.attributes[attrib_name] if len(selected_controls) < 2 else AnchorAttributeType.meta[attrib_type][0]
                        label = attrib_name

                    self.node.parm("attrib_name{}".format(attrib_index + 1)).set(label)

                    for value_parm_name in AnchorAttributeType.parm_names:
                        parm_tuple = self.node.parmTuple(value_parm_name.format(attrib_index + 1))
                        is_hidden_tuple = value_parm_name != AnchorAttributeType.meta[attrib_type][1]
                        parm_tuple.hide(is_hidden_tuple)

                        if not is_hidden_tuple:
                            parm_value = (attrib_value,) if not isinstance(attrib_value, Iterable) else attrib_value
                            parm_tuple.set(parm_value)
       
        else:

            with hou.undos.disabler():
                self.node.parm("selected_prim_folder").hide(True)
                self.node.parm("selected_control_label").hide(False)
                self.node.parm("anchor_attribs").hide(True)
                self.show_anchor_parms(False)

                self.node.parm("selected_control_label").set("Nothing Is Selected")
            
                       


    def on_anchor_selected(self):

        self.calculate_multiselect_box()
        self.state.show_houdini_handle()

        self.sync_parmpane_with_selection()


    def on_mouse_down(self, ui_event):
        device = ui_event.device() # type: hou.UIEventDevice

        selected_before = None
        if len(self.point_controls.selected_controls) == 1 and self.point_controls.selected_controls[0].tag == "position":
            selected_before = self.point_controls.selected_controls[0]

        self.point_controls.on_mouse_down(ui_event)
        selected_control = self.point_controls.select_point()
        self.adding_anchor = False
        if selected_control is None:

            if self.curve_pos_under_cursor is None: 
                # add anchor to prim (either start or end)

                if not device.isShiftKey() and not device.isCtrlKey() and self.draw_mode:

                    anchor_index = prim_to_add = at_end = None

                    new_prim = first_prim = False

                    if not self.anchor_points:
                        self.prims.append([0, 0, False, "curve"])
                        anchor_index = prim_to_add = 0
                        first_prim = True
                        at_end = False
                    elif selected_before is not None:
                        anchor_before = self.get_anchor_from_control(selected_before)
                        anchor_index = self.anchor_points.index(anchor_before)
                        prim_to_add, at_end = self.get_prim_to_add_anchor(anchor_index)

                    if prim_to_add is None:
                        numpt = len(self.anchor_points)
                        self.prims.append([numpt, numpt, False, "curve"])
                        anchor_index = numpt
                        prim_to_add = len(self.prims)-1
                        at_end = False
                        new_prim = True

                    if prim_to_add is not None:

                        if self.anchor_points and not new_prim and selected_before is not None:
                            self.point_controls.plane_point = selected_before.world_position
                        else:
                            self.point_controls.plane_point = hou.Vector3(0, 0, 0)
                        construction_point = self.point_controls.get_construction_point(ui_event)

                        if construction_point is not None:

                            self.aligned_handle_move = True
                            self.symmetric_handle_move = True
                            self.rotate_corner_mode = False

                            self.control_clicked = True
                            self.control_moved = False
                            self.adding_anchor = True
                            self.new_anchor_added = True
                            
                            self.begin_edit()
                            self.append_anchor(construction_point, anchor_index, at_end, prim_to_add)
                        else:
                            self.state.log("Warning: Intersection failed")

                            self.point_controls.clear_selection()
                            self.update_all_editor_geo()
                            self.on_anchor_selected()
                            if new_prim or first_prim:
                                del self.prims[prim_to_add]
                    
                    self.allocate_names_drawer()
                else:
                    self.state.log("Start selection")
                    if device.isShiftKey():
                        self.selection_mode = 2
                        selection_drawable_params = { "color1": (0.3,0.9,0.0,1.0) }
                    elif device.isCtrlKey():
                        self.selection_mode = 3
                        selection_drawable_params = { "color1": (0.9,0.3,0.0,1.0) }
                    else:
                        self.selection_mode = 1
                        selection_drawable_params = { "color1": (0.9,0.9,0.9,1.0) }
                    
                    self._selection_drawable.setParams( selection_drawable_params )

                    viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport

                    if len(self.point_controls.selected_controls) == 1 and self.point_controls.selected_controls[0].tag == "handle":
                        self.point_controls.clear_selection()
                        self.update_all_editor_geo()
                        self.on_anchor_selected()

                    self.selection_start_anchors = [self.get_anchor_from_control(c) for c in self.point_controls.selected_controls]

                    mouse_pos = hou.Vector3(device.mouseX(), device.mouseY(), 0.0)
                    mouse_pos *= viewport.windowToViewportTransform()

                    self.selection_start = mouse_pos
                    self.selection_viewport = viewport

            else:
                # inserting anchor inside prim

                self.new_anchor_added = True

                self.begin_edit()
                self.insert_anchor(self.curve_pos_under_cursor, self.curve_prim_under_cursor)
                self.on_anchor_selected()

        else:
            self.control_moved = False
            self.control_clicked = True

            clicked_on_anchor = selected_control.tag == "position"
            editing_anchor = self.get_anchor_from_control(selected_control)

            if clicked_on_anchor:

                self.point_controls.plane_point = editing_anchor.position

                # Ctrl + Shift - Remove anchor
                if device.isCtrlKey() and device.isShiftKey():
                    self.begin_edit()

                    self.remove_anchor(editing_anchor)
                    self.editing_anchor = -1
                    self.point_controls.hovered_control = None
                    self.point_controls.update_points_geo()
                    self.point_controls.update_hovered_geo()

                    self.end_edit()

                # Ctrl - Smooth toggle
                elif device.isCtrlKey():

                    self.point_controls.select_control(selected_control)

                    self.begin_edit()
                    self.toggle_anchor_smoothness(editing_anchor)
                    self.update_anchor_geo_position(editing_anchor)
                    self.end_edit()

                    

                elif device.isShiftKey():
                    any_handle_selected = any((c.tag == "handle" for c in self.point_controls.selected_controls))
                    empty_selection = not self.point_controls.selected_controls

                    if not any_handle_selected or empty_selection:
                        if selected_control in self.point_controls.selected_controls:
                            self.point_controls.unselect_control(selected_control)
                            self.point_controls.update_selected_geo()
                            self.point_controls.dragged_control = None
                        else:
                            self.point_controls.add_control_to_selection(selected_control)
                            self.point_controls.dragged_control = None

                    if any_handle_selected:
                        self.point_controls.select_control(selected_control)

                else:
                    multi_selected = all(c.tag == "position" for c in self.point_controls.selected_controls)
                    multi_selected = multi_selected and len(self.point_controls.selected_controls) > 1
                    if not multi_selected or selected_control not in self.point_controls.selected_controls:
                        self.point_controls.select_control(selected_control)
                    else:
                        self.point_controls.dragged_control = selected_control

                self.get_editing_anchor_from_selection()
                self.on_anchor_selected()

            else:
                self.point_controls.plane_point = selected_control.world_position

                self.point_controls.select_control(selected_control)
                self.get_editing_anchor_from_selection()

                if device.isCtrlKey() and device.isShiftKey():
                    self.rotate_corner_mode = True

                self.aligned_handle_move = not device.isCtrlKey() and not self.rotate_corner_mode
                self.symmetric_handle_move = device.isShiftKey() and not self.rotate_corner_mode


                if self.anchor_points[self.editing_anchor].anchor_type == AnchorType.UNTIED:
                    self.aligned_handle_move = False
                
                if self.symmetric_handle_move:
                    self.aligned_handle_move = True
                    self.anchor_points[self.editing_anchor].anchor_type = AnchorType.SMOOTH

            self.show_editing_handles()
            self.update_handles_geo()

    def on_mouse_up(self, ui_event):
        self.point_controls.on_mouse_up(ui_event)
        
        self.aligned_handle_move = True
        self.symmetric_handle_move = False
        self.rotate_corner_mode = False

        if self.control_clicked:
            self.control_clicked = False

        if self.control_moved:
            self.control_moved = False
            #self.point_translate_handle.update()
            if len(self.point_controls.selected_controls) == 1 and not self.state.show_point_handles:
                anchor = self.get_anchor_from_control(self.point_controls.dragged_control)
                self.point_controls.select_control(self.anchor_points_controls[anchor][2])
                self.on_anchor_selected()
            if not self.new_anchor_added:
                self.end_edit()
        else:
            if self.point_controls.selected_controls and self.point_controls.dragged_control is not None and not self.selection_mode:
                self.point_controls.select_control(self.point_controls.dragged_control)
                self.get_editing_anchor_from_selection()
                self.show_editing_handles()
                self.update_handles_geo()
                self.on_anchor_selected()

            if self.adding_anchor:
                anchor = self.get_anchor_from_control(self.point_controls.dragged_control)
                anchor.anchor_type = AnchorType.CORNER


        if self.adding_anchor:
            anchor = self.get_anchor_from_control(self.point_controls.dragged_control)
            self.point_controls.select_control(self.anchor_points_controls[anchor][2])

            self.get_editing_anchor_from_selection()
            self.show_editing_handles()
            self.update_handles_geo()
            self.on_anchor_selected()
            self.point_controls.update_points_geo()
            self.point_controls.update_selected_geo()

        if self.new_anchor_added:
            self.new_anchor_added = False
            self.end_edit()
        
        self.point_controls.enable_snapping = True

        if self.selection_mode:
            self.state.log("Selection ends with {} selected".format(len(self.point_controls.selected_controls)))
            self.selection_mode = 0

    
    def build_selection_geo(self, mouse_pos):

        geo = hou.Geometry() # type: hou.Geometry

        mouse_pos *= self.selection_viewport.windowToViewportTransform()

        pt1 = self.selection_start
        pt2 = mouse_pos

        pt1_ray = self.selection_viewport.mapToWorld(pt1.x(), pt1.y())
        pt2_ray = self.selection_viewport.mapToWorld(pt1.x(), pt2.y())
        pt3_ray = self.selection_viewport.mapToWorld(pt2.x(), pt2.y())
        pt4_ray = self.selection_viewport.mapToWorld(pt2.x(), pt1.y())


        view_transform = self.selection_viewport.viewTransform() # type: hou.Matrix4

        camera_pos = hou.Vector3(0, 0, 0) * view_transform # type: hou.Vector3
        camera_look =  hou.Vector3(0, 0, -1) * view_transform - camera_pos # type: hou.Vector3

        plane_point = camera_pos + 10.0 * camera_look

        geo_pt1 = hou.hmath.intersectPlane(plane_point, camera_look, pt1_ray[1], pt1_ray[0])
        geo_pt2 = hou.hmath.intersectPlane(plane_point, camera_look, pt2_ray[1], pt2_ray[0])
        geo_pt3 = hou.hmath.intersectPlane(plane_point, camera_look, pt3_ray[1], pt3_ray[0])
        geo_pt4 = hou.hmath.intersectPlane(plane_point, camera_look, pt4_ray[1], pt4_ray[0])

        geo.createPoints((geo_pt1, geo_pt2, geo_pt3, geo_pt4))
        geo.createPolygons(((0, 1, 2, 3),), True)

        self._selection_drawable.setGeometry(geo)

    def is_anchor_in_box_selection(self, anchor, left, right, bottom, top):
        # type: (AnchorPoint, hou.Vector3) -> None

        viewport = self.selection_viewport # type: hou.GeometryViewport
        anchor_screen_pos = viewport.mapToScreen(anchor.position * viewport.modelToGeometryTransform().inverted()) # type: hou.Vector2

        return left <= anchor_screen_pos.x() <= right and bottom <= anchor_screen_pos.y() <= top

    def process_box_selection(self, device):
        # type(hou.UIEventDevice) -> bool

        mouse_pos = hou.Vector3(device.mouseX(), device.mouseY(), 0.0)
        mouse_pos *=  self.selection_viewport.windowToViewportTransform()

        start_x = self.selection_start.x()
        start_y = self.selection_start.y()

        end_x = mouse_pos.x()
        end_y = mouse_pos.y()

        left = min(start_x, end_x)
        right = left + abs(start_x - end_x)

        bottom = min(start_y, end_y)
        top = bottom + abs(start_y - end_y)

        anchors_in_box = [anchor for anchor in self.anchor_points if self.is_anchor_in_box_selection(anchor, left, right, bottom, top)]

        self.point_controls.clear_selection()

       
        if self.selection_mode == 1:
            selected_anchors = anchors_in_box
        elif self.selection_mode == 2:
            selected_anchors = (self.selection_start_anchors + anchors_in_box)
        else:
            selected_anchors = set(self.selection_start_anchors) - set(anchors_in_box)

        for anchor in selected_anchors:
            self.point_controls.add_control_to_selection(self.anchor_points_controls[anchor][2], False)
        self.point_controls.update_selected_geo()
    
        self.get_editing_anchor_from_selection()
        self.show_editing_handles()
        self.update_handles_geo()

        self.on_anchor_selected()



    def on_mouse_move(self, ui_event):
        if not self.selection_mode:
            if self.control_clicked and not self.control_moved:
                self.state.log("[Start Moving Control]")
                self.control_moved = True
                self.control_clicked = False

                if self.point_controls.dragged_control.tag == "handle" and not self.handles_snapping:
                    self.point_controls.enable_snapping = False
                else:
                    self.point_controls.enable_snapping = True

                if not self.new_anchor_added:
                    self.begin_edit()
            
            self.point_controls.on_mouse_move(ui_event)
        else:
            device = ui_event.device() # type: hou.UIEventDevice
            mouse_pos = hou.Vector3(device.mouseX(), device.mouseY(), 0.0)
            self.build_selection_geo(mouse_pos)
            self.process_box_selection(device)


    def draw(self, handle):
        if self.current_attribute is not None and not self.state.show_point_handles:
            attribute_type = self.current_attribute_class.type
            if attribute_type == AnchorAttributeType.PSCALE_AND_ROLL or attribute_type == AnchorAttributeType.FLOAT_SCALE:
                self.state.pscale_handle.update(True)

        if self.state.show_attrib_values and self.current_attribute is not None:
            self.sync_attrib_value_drawer(self.current_attribute)
            self.attrib_value_drawer.draw(handle)

        if self.state.show_tags:
            self.sync_tags_drawer()
            self.anchor_tags_drawer.draw(handle)

        if self.state.show_names:
            self.sync_names_drawer()
            self.prim_names_drawer.draw(handle)

        geo_was_dirty = self.curve_geo_dirty
        self.export_to_SOP()

        if self.use_curve_guides:
            self._curve_drawable.draw(handle)
            if self.use_arrow_heads:
                with hou.undos.disabler():
                    self.build_arrowheads_geo()
                self._arrowhead_drawable.draw(handle)

        self._handles_drawable.draw(handle)
        self.point_controls.draw(handle)
    

        if self.selection_mode:
            self._selection_drawable.draw(handle)


    def show(self, visible):
        self._handles_drawable.show(visible)
        self._curve_drawable.show(visible)
        self._arrowhead_drawable.show(visible)
        self._selection_drawable.show(visible)
        self.point_controls.show(visible)

    def save_anchor_points(self):
        self.disable_control_sync = True
        controls_str = self.writes()
        self.controls_parm.set(controls_str)
        self.disable_control_sync = False

    def get_anchor_attrib_value(self, anchor, attrib_name, control_index):
        attrib = anchor.attributes[attrib_name]
        if control_index == 1:
            return attrib
        interp_attrib = anchor.interpolated_attribs[attrib_name]
        if control_index == 0:
            return interp_attrib[0]
        return interp_attrib[1]

    def get_anchor_geo_point(self, anchor, control_index):
        # type: (AnchorPoint, int) -> hou.Point
        if anchor.geo_points[control_index] is not None:
            return self.curve_geo.point(anchor.geo_points[control_index])
        return None

    def update_anchor_geo_position(self, anchor):
        # type: (AnchorPoint) -> None
        self.curve_geo_dirty = True
        for control_index in range(3):
            geo_point = self.get_anchor_geo_point(anchor, control_index)
            if geo_point is not None:
                geo_point.setPosition(anchor[control_index])

    def update_anchor_geo_attribs(self, anchor):
        # type: (AnchorPoint) -> None
        self.curve_geo_dirty = True
        self.attribs_dirty = True
        anchors_to_update = (self.get_prev_anchor(anchor), anchor, self.get_next_anchor(anchor))

        for anchor_to_update in (anchor for anchor in anchors_to_update if anchor is not None):
            self.interpolate_anchor_attributes(anchor_to_update, anchor_to_update.anchor_index)
            for control_index in range(3):
                geo_point = self.get_anchor_geo_point(anchor_to_update, control_index)
                if geo_point is not None:

                    for attrib_name in self.attribute_names:
                        attrib_value = self.get_anchor_attrib_value(anchor_to_update, attrib_name, control_index)
                        geo_point.setAttribValue(attrib_name, attrib_value)

    def build_arrowheads_geo(self):
        arrowheads_points = hou.Geometry() # type: hou.Geometry

        pscale_attrib = arrowheads_points.addAttrib(hou.attribType.Point, "pscale", 1.0)
        N_attrib = arrowheads_points.addAttrib(hou.attribType.Point, "N", (0, 1.0, 0.0), True)
        anchors_to_export = [prim[1] - 1 if not prim[2] else prim[0] for prim in self.prims if prim[1] - prim[0] > 1]
        prims_to_export = [primnum for primnum, prim in enumerate(self.prims) if prim[1] - prim[0] > 1]
        geo_points = [self.anchor_points[index].position for index in anchors_to_export]
        arrowheads_points.createPoints(geo_points)

        # from path deform state
        viewport = self.scene_viewer.curViewport()

        proj = viewport.viewportToNDCTransform() * viewport.ndcToCameraTransform() * viewport.cameraToModelTransform() * viewport.modelToGeometryTransform()
        dx = (hou.Vector4(1, 0, 0, 0) * proj).length()
        dy = (hou.Vector4(0, 1, 0, 0) * proj).length()

        scale = min(dx, dy)
        
        proj_inv = proj.inverted()


        for ptnum, point in enumerate(arrowheads_points.points()): # type: int, hou.Point
            anchor_index = anchors_to_export[ptnum]
            anchor = self.anchor_points[anchor_index]
            prim = self.prims[prims_to_export[ptnum]]
            prev_anchor = self.anchor_points[anchor_index-1] if not prim[2] else self.anchor_points[prim[1] - 1]
            tangent = anchor.position - anchor.in_control if anchor.anchor_type != AnchorType.CORNER else anchor.position - prev_anchor.out_control
            point.setAttribValue(N_attrib, tangent.normalized())
            pt_pos = point.position()
            p = hou.Vector4(pt_pos.x(), pt_pos.y(), pt_pos.z(), 1.0) * proj_inv
            point.setAttribValue(pscale_attrib, scale * p[3] * 100)

        geo = hou.Geometry()
        verb = hou.sopNodeTypeCategory().nodeVerb('copytopoints::2.0')
        verb.setParms({'useidattrib': True, 'idattrib': '__type', 'targetattribs':({'applyattribs#': '* ^N'},)})
        arrowhead_geo = self.node.node("head_scale").geometry()
        verb.execute(geo, [arrowhead_geo, arrowheads_points])

        self._arrowhead_drawable.setGeometry(geo)
               

    # TODO: can be optimized with setPointFloatAttribValuesFromString (though point number is not that bad)
    def rebuild_geo(self, update_stash=True):
        if update_stash:
            self.curve_geo_dirty = True
        self.curve_geo = hou.Geometry()

        if len(self.geo_prims) < len(self.prims):
            self.geo_prims.extend([-1] * (len(self.prims) - len(self.geo_prims)))
        geo_prim_num = 0

        for attrib_name in self.attribute_names:
            attrib = self.attribute_names[attrib_name]
            self.curve_geo.addAttrib(hou.attribType.Point, attrib_name, attrib.value, create_local_variable=False)

        self.curve_geo.addAttrib(hou.attribType.Point, "tag", "", create_local_variable=False)

        roll_attribs = [attrib_name for attrib_name in self.attribute_names if self.attribute_names[attrib_name].type == AnchorAttributeType.VECTOR_UP]
        if roll_attribs:
            self.curve_geo.addAttrib(hou.attribType.Global, "roll_attribs", "", create_local_variable=False)
            self.curve_geo.setGlobalAttribValue("roll_attribs", " ".join(roll_attribs))

        orient_attribs = [attrib_name for attrib_name in self.attribute_names if self.attribute_names[attrib_name].type == AnchorAttributeType.ORIENTATION]
        if orient_attribs:
            self.curve_geo.addAttrib(hou.attribType.Global, "orient_attribs", "", create_local_variable=False)
            self.curve_geo.setGlobalAttribValue("orient_attribs", " ".join(orient_attribs))



        self.interpolate_all_attributes()

        self.curve_geo.addAttrib(hou.attribType.Prim, "name", "", create_local_variable=False)

        for anchor in self.anchor_points:
            anchor.geo_points = [None, None, None]

        for prim_num, prim in enumerate(self.prims):
            prim_points = [anchor[index] for anchor in self.anchor_points[prim[0]:prim[1]] for index in range(3)]
            prim_attribs = [(anchor_index, attrib_index) for anchor_index in range(prim[0], prim[1]) for attrib_index in range(3)]

            if (prim[1]-prim[0]) > 1 and self.node:
                prim_export_points = prim_points[1:-1]
                prim_export_attribs = prim_attribs[1:-1]

                # if closed
                if prim[2]:
                    prim_export_points.extend((prim_points[-1], prim_points[0]))
                    prim_export_attribs.extend((prim_attribs[-1], prim_attribs[0]))
                
                bezier_prim = self.curve_geo.createBezierCurve(len(prim_export_points), prim[2], 4) # type: hou.Face
                bezier_prim.setAttribValue("name", prim[3])

                for ptnum, point in enumerate(bezier_prim.points()): # type: int, hou.Point
                    point.setPosition(prim_export_points[ptnum])
                    
                    anchor_index = prim_export_attribs[ptnum][0]
                    control_index = prim_export_attribs[ptnum][1]
                    
                    if control_index == 1:
                        point.setAttribValue("tag", self.anchor_points[anchor_index].tag)
                    
                    self.anchor_points[anchor_index].geo_points[control_index] = point.number()

                    for attrib_name in self.attribute_names:
                        attrib_value = self.get_anchor_attrib_value(self.anchor_points[anchor_index], attrib_name, control_index)
                        point.setAttribValue(attrib_name, attrib_value)

                self.geo_prims[geo_prim_num] = prim_num
                geo_prim_num += 1

        if update_stash:
            self.export_to_SOP()

    def update_guide_geo(self):
        self.guide_stash.set(self.curve_geo)
        resampled_guide_geo = self.resampled_guide_node.geometry()
        self._curve_drawable.setGeometry(resampled_guide_geo)

    def export_to_SOP(self):
        if self.curve_geo_dirty:
            if self.update_geo_on_edit or not self.edit_transaction or not self.use_curve_guides:
               self.geo_stash.set(self.curve_geo)
               self.curve_geo.incrementAllDataIds()

            self.update_guide_geo()
            self.curve_geo_dirty = False


# Main class

class State(object):
    MSG = "Draw a curve"

    ANCHOR_TYPE_TO_MENU_PARM = {AnchorType.SMOOTH:"smooth", AnchorType.CORNER:"corner", AnchorType.UNTIED:"untied"}
    MENU_PARM_TO_ANCHOR_TYPE = {"smooth":AnchorType.SMOOTH, "corner":AnchorType.CORNER, "untied":AnchorType.UNTIED}
    DISPLAY_SETTINGS_PARMS = ["controls_size", "controls_color", "guides_color", "guides_thickness",
        "text_size", "selected_color", "names_size", "names_color", "attribs_color"]
    
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.node = None # type: hou.SopNode
        self.scene_viewer = scene_viewer # type: hou.SceneViewer
        self.bezier_editor = BezierEditor(scene_viewer)

        self.curve_geo = None # type: hou.Geometry
        self.point_drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Point, "intersect_point") # type: hou.GeometryDrawable

        self.warning_drawable = hou.TextDrawable(self.scene_viewer, "warning_text")

        self.corner_text_drawable = hou.TextDrawable(self.scene_viewer, "corner_text_drawable")

        self.last_cursor_world_pos = hou.Vector3()
        self.last_cursor_normal = None # type: hou.Vector3
        self.menu_world_position = hou.Vector3()
        self.menu_world_normal = None # type: hou.Vector3
        self.last_shape = None

        (x,y,width,height) = self.scene_viewer.curViewport().size()
        margin = 10

        self.warning_drawable.setParams({
            "text": "",
            'color1' : (1.0,1.0,1.0, 1.0),
            'color2' : (0.0,0.0,0.0, 1.0),
            'translate' : hou.Vector3(0, height, 0),
            'origin' : hou.drawableTextOrigin.UpperLeft,
            'margins': hou.Vector2(margin, -3 * margin),
            'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
            "glow_width": 1.0,
        })

        self.corner_text_drawable.setParams({
            "text": "",
            'color1' : (1.0,1.0,1.0, 1.0),
            'color2' : (0.0,0.0,0.0, 1.0),
            'translate' : hou.Vector3(0, height, 0),
            'origin' : hou.drawableTextOrigin.UpperLeft,
            'margins': hou.Vector2(margin, -margin),
            'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
            "glow_width": 1.0,
        })


        self.warning_drawable.show(True)
        self.corner_text_drawable.show(True)

        self.point_drawable.setParams(
            {
                "color1": (0, 1, 0, 1),
                "fade_factor": 1.0,
            }
        )

        self.point_translate_handle = hou.Handle(scene_viewer, "point_translate_handle")
        self.spin_handle = hou.Handle(scene_viewer, "spin_handle")
        self.pscale_handle = hou.Handle(scene_viewer, "pscale_handle")
        self.vector_handle = hou.Handle(scene_viewer, "vector_handle")
        self.angle_handle = hou.Handle(scene_viewer, "angle_handle")
        self.box_handle = hou.Handle(scene_viewer, "box_handle")

        self.hou_handles = {
            "pscale_handle": self.pscale_handle,
            "vector_handle": self.vector_handle,
            "spin_handle": self.spin_handle,
            "angle_handle": self.angle_handle,
        }

        self.bezier_editor.point_translate_handle = self.point_translate_handle
        self.bezier_editor.spin_handle = self.spin_handle
        self.bezier_editor.pscale_handle = self.pscale_handle

        self.ladder_opened = False

        self.show_point_handles = False
        self.show_box_handle = False
        self.show_attrib_values = False
        self.show_tags = False
        self.show_names = False

        self.double_clicked = False
        
                
    def show(self, visible):
        """ Display or hide drawables.
        """
        self.bezier_editor.show(visible)



    def onEnter(self, kwargs):
        self.log("== Enter ==")
        node = kwargs["node"] # type: hou.Node

        self.node = node

        with hou.undos.disabler():
            self.node.removeSpareParms()

        self.show(True)
        self.scene_viewer.setPromptMessage( State.MSG )
        self.bezier_editor.attach_node(node, self)
        self.point_drawable.show(True)

        self.point_translate_handle.disableParms(["rx", "ry", "rz", "sx", "sy", "sz", "uniform_scale"]) 
        self.spin_handle.disableParms(["uniform_scale", "tx", "ty", "tz", "sx", "sy", "sz", "rx", "ry"])
        self.pscale_handle.disableParms(["uniform_scale", "tx", "ty", "tz", "sx", "sz", "rx", "ry", "rz"])
        self.vector_handle.disableParms(["tx", "ty", "tz", "scale"])
        self.angle_handle.disableParms(["tx", "ty", "tz", "scale"])

        self.on_current_attrib()

        with hou.undos.disabler():
            self.node.parm("hide_attributes").set(1)
            self.node.parmTuple("tabs").set((0,))

        self.show_point_handles = self.node.parm("point_handles").evalAsInt()
        self.show_box_handle = self.node.parm("box_handle").evalAsInt()
        self.show_attrib_values = self.node.parm("display_values").evalAsInt()
        self.show_names = self.node.parm("display_names").evalAsInt()
        self.show_tags = self.node.parm("display_tags").evalAsInt()

        self.set_corner_text()

        version = hou.applicationVersion()

        if (version[0] == 18 and version[1] == 5) or version[0] >= 19:
            callback_parms = ["point_handles", "box_handle", "display_values", "display_names", "controls",
                "use_curve_guide", "use_arrow_heads", "update_geo_on_edit", "current_attribute", "drawing_mode", 
                "handles_snapping", "display_tags", "use_surface"] + self.DISPLAY_SETTINGS_PARMS
            self.node.addParmCallback(self.on_parm_changed, callback_parms)
            self.node.addEventCallback((hou.nodeEventType.InputRewired,), self.on_rewired)
        elif version[0] == 18 and version[1] == 0:
            self.node.addEventCallback((hou.nodeEventType.ParmTupleChanged,), self.on_parm_changed)

        self.setup_surface_input()


    def onExit(self, kwargs):
        self.log("== Exit ==")

        try:
    
            with hou.undos.disabler():
                self.node.removeSpareParms()
                self.node.parm("hide_attributes").set(0)

            self.node.removeAllEventCallbacks()
        except:
            # node probably doesn't exist at the exit
            pass

    def onResume(self, kwargs):
        self.show(True)
        self.scene_viewer.setPromptMessage( State.MSG )

    def onInterrupt(self,kwargs):
        pass

    def onHandleToState(self, kwargs):
        node = kwargs['node'] # type: hou.Node
        handle = kwargs['handle']
        parms = kwargs['parms']

        selected_controls = self.bezier_editor.point_controls.selected_controls
        current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

        if selected_controls and self.show_point_handles:

            handle_control = selected_controls[0]

            if handle == self.point_translate_handle.name():
                handle_position = hou.Vector3(parms["tx"], parms["ty"], parms["tz"])

                anchor = self.bezier_editor.get_anchor_from_control(handle_control)

                self.bezier_editor.aligned_handle_move = anchor.anchor_type == AnchorType.SMOOTH
                handle_control.move_to(handle_position)
                self.bezier_editor.point_controls.update_points_geo()
                self.bezier_editor.point_controls.update_selected_geo()
                self.bezier_editor.point_controls.update_hovered_geo()

        if len(selected_controls) > 1 and handle == self.box_handle.name():

            rx, ry, rz = parms["rx"], parms["ry"], parms["rz"]
            tx, ty, tz = parms["centerx"], parms["centery"], parms["centerz"]
            box_center = hou.Vector3((tx, ty, tz))
            sizex, sizey, sizez = parms["sizex"], parms["sizey"], parms["sizez"]
            
            size_tolerance = 0.000001

            selection_size = self.bezier_editor.selection_box_size

            sx = 1.0 if abs(selection_size.x()) < size_tolerance else sizex / selection_size.x()
            sy = 1.0 if abs(selection_size.y()) < size_tolerance else sizey / selection_size.y()
            sz = 1.0 if abs(selection_size.z()) < size_tolerance else sizez / selection_size.z()

            transform = hou.hmath.identityTransform()
            transform *= hou.hmath.buildScale(sx, sy, sz)
            transform *= hou.hmath.buildRotate(rx, ry, rz)

            for index, control in enumerate(selected_controls):

                anchor = self.bezier_editor.get_anchor_from_control(control)
                box_positions = self.bezier_editor.selection_box_positions[index]

                box_positions = [pos * transform for pos in box_positions]

                anchor.position = box_center + box_positions[1]
                anchor.controls[0] = box_center + box_positions[0]
                anchor.controls[1] = box_center + box_positions[2]

                self.bezier_editor.sync_anchor_controls(anchor)
                self.bezier_editor.update_anchor_geo_position(anchor)

            self.bezier_editor.point_controls.update_points_geo()
            self.bezier_editor.point_controls.update_selected_geo()


                                        
        if current_control is not None and self.bezier_editor.current_attribute is not None and not self.show_point_handles:

            current_attribute = self.bezier_editor.current_attribute
            anchor = self.bezier_editor.get_anchor_from_control(current_control)

            if current_attribute == "__pr":
    
                if handle == self.spin_handle.name():
                    __pr = anchor.attributes["__pr"]
                    anchor.attributes["__pr"][1] = parms["rz"]

                if handle == self.pscale_handle.name():

                    #delta = parms["sy"]
                    __pr = anchor.attributes["__pr"]
                    anchor.attributes["__pr"][0] = parms["sy"]

                self.bezier_editor.update_anchor_geo_attribs(anchor)

            elif current_attribute in self.bezier_editor.attribute_names:

                attribute_type = self.bezier_editor.current_attribute_class.type
                handle_name = AnchorAttributeType.meta[attribute_type][3][0]

                if handle == handle_name:

                    value = 0.0

                    if handle == self.vector_handle.name():
                        anchor.attributes[current_attribute][0] = parms["vx"]
                        anchor.attributes[current_attribute][1] = parms["vy"]
                        anchor.attributes[current_attribute][2] = parms["vz"]
                    elif handle == self.angle_handle.name():
                        anchor.attributes[current_attribute][0] = parms["rx"]
                        anchor.attributes[current_attribute][1] = parms["ry"]
                        anchor.attributes[current_attribute][2] = parms["rz"]
                    elif handle == self.spin_handle.name():
                        anchor.attributes[current_attribute] = parms["rz"]
                    elif handle == self.pscale_handle.name():
                        anchor.attributes[current_attribute] = parms["sy"]

                    self.bezier_editor.update_anchor_geo_attribs(anchor)


    def onBeginHandleToState(self, kwargs):
        node = kwargs["node"] # type: hou.Node
        handle = kwargs["handle"]

        self.bezier_editor.begin_edit()
        
    def onEndHandleToState(self, kwargs):
        node = kwargs["node"] # type: hou.Node
        handle = kwargs["handle"]

        self.bezier_editor.end_edit()
        self.bezier_editor.sync_parmpane_with_selection()
        

    def onStateToHandle(self, kwargs):
        node = kwargs["node"] # type: hou.Node
        handle = kwargs["handle"]
        parms = kwargs["parms"]

        selected_controls = self.bezier_editor.point_controls.selected_controls
        current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

        if selected_controls and handle == self.point_translate_handle.name():

            handle_control = selected_controls[0]
            
            parms["tx"] = handle_control.world_position.x()
            parms["ty"] = handle_control.world_position.y()
            parms["tz"] = handle_control.world_position.z()

        if (self.bezier_editor.reset_selection_box and len(selected_controls) > 1 
            and handle == self.box_handle.name() and self.bezier_editor.multiselect_box is not None):

            parms["centerx"] = self.bezier_editor.multiselect_box[0].x()
            parms["centery"] = self.bezier_editor.multiselect_box[0].y()
            parms["centerz"] = self.bezier_editor.multiselect_box[0].z()

            parms["sizex"] = self.bezier_editor.multiselect_box[1].x() 
            parms["sizey"] = self.bezier_editor.multiselect_box[1].y()
            parms["sizez"] = self.bezier_editor.multiselect_box[1].z()

            parms["rx"] = parms["ry"] = parms["rz"] = 0.0

            self.bezier_editor.reset_selection_box = False


        if current_control is not None:

            if self.bezier_editor.current_attribute is not None:

                anchor = self.bezier_editor.get_anchor_from_control(current_control)
                anchor_index = self.bezier_editor.anchor_points.index(anchor)

                attribute_type = self.bezier_editor.current_attribute_class.type
                scale = anchor.attributes["__pr"][0] if attribute_type == AnchorAttributeType.PSCALE_AND_ROLL else anchor.attributes[self.bezier_editor.current_attribute]
                roll = anchor.attributes["__pr"][1] if attribute_type == AnchorAttributeType.PSCALE_AND_ROLL else anchor.attributes[self.bezier_editor.current_attribute]

                handle_position = anchor.position

                if handle == self.vector_handle.name():
                    parms["tx"] = handle_position.x()
                    parms["ty"] = handle_position.y()
                    parms["tz"] = handle_position.z()

                    if attribute_type == AnchorAttributeType.VECTOR_ARBITRARY:
                        attrib_value = anchor.attributes[self.bezier_editor.current_attribute]
                        
                        parms["vx"] = attrib_value[0]
                        parms["vy"] = attrib_value[1]
                        parms["vz"] = attrib_value[2]

                if handle == self.angle_handle.name():
                    parms["tx"] = handle_position.x()
                    parms["ty"] = handle_position.y()
                    parms["tz"] = handle_position.z()

                    if attribute_type == AnchorAttributeType.ORIENTATION:
                        attrib_value = anchor.attributes[self.bezier_editor.current_attribute]
                        
                        parms["rx"] = attrib_value[0]
                        parms["ry"] = attrib_value[1]
                        parms["rz"] = attrib_value[2]


                if handle == self.pscale_handle.name() or handle == self.spin_handle.name():

                    anchor_tangent = self.bezier_editor.get_anchor_tangent(anchor_index)
                    handle_orient = hou.Quaternion()
                    handle_orient.setToVectors(hou.Vector3(0, 0, -1), anchor_tangent)

                    handle_rotation = handle_orient.extractEulerRotates() # type: hou.Vector3

                    #rot_matrix = hou.hmath.buildRotateZToAxis(anchor_tangent).extractRotationMatrix3()
                    rot_matrix = look_at(anchor_tangent, hou.Vector3(0, 1, 0)) # type: hou.Matrix4
                    roll_matrix = hou.hmath.buildRotateAboutAxis(anchor_tangent, roll).extractRotationMatrix3()

                    rot_matrix *= roll_matrix
                    
                    handle_up = hou.Vector3(0, 0.01, 0) * rot_matrix
                    handle_rotation = rot_matrix.extractRotates()

                    viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport
                    
                    view_transform = viewport.viewTransform() # type: hou.Matrix4
                    ndc_to_cam = viewport.ndcToCameraTransform() # type: hou.Matrix4
                    
                    proj = view_transform.inverted() * ndc_to_cam.inverted()
                   
                    if handle == self.pscale_handle.name():
                        offset = proj.asTuple()[15]*handle_up
                        handle_position = handle_position + offset if parms["sy"] > 0 else handle_position - offset

                    parms["px"] = handle_position.x()
                    parms["py"] = handle_position.y()
                    parms["pz"] = handle_position.z()

                    parms["pivot_rx"] = handle_rotation.x()
                    parms["pivot_ry"] = handle_rotation.y()
                    parms["pivot_rz"] = handle_rotation.z()

                    if handle == self.pscale_handle.name():
                        parms["sy"] = scale

                    if handle == self.spin_handle.name():
                        parms["rz"] = roll

    def on_ladder(self, new_value):
        selected_controls = self.bezier_editor.point_controls.selected_controls
        current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

        if self.bezier_editor.current_attribute is not None:

            attribute_type = self.bezier_editor.current_attribute_class.type

            if not (attribute_type == AnchorAttributeType.FLOAT_LADDER or attribute_type == AnchorAttributeType.INTEGER_LADDER):
                return

            anchor = self.bezier_editor.get_anchor_from_control(current_control)
            value = float(new_value) if attribute_type == AnchorAttributeType.FLOAT_LADDER else int(new_value)
            anchor.attributes[self.bezier_editor.current_attribute] = value

            self.bezier_editor.update_anchor_geo_attribs(anchor)
    

    def on_mouse_down(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.bezier_editor.on_mouse_down(ui_event)

    def on_mouse_up(self, ui_event):
        self.bezier_editor.on_mouse_up(ui_event)

    def on_mouse_move(self, ui_event):
        self.bezier_editor.on_mouse_move(ui_event)

    def on_current_attrib(self):
        self.bezier_editor.attribs_dirty = True
        self.bezier_editor.get_current_attribute()
        self.hide_all_houdini_handles()
        self.show_attribute_handle()

    def hide_toolbox_attribs(self, state_parms):
        state_parms["parm_int"]["visible"] = False
        state_parms["parm_float"]["visible"] = False
        state_parms["parm_float3"]["visible"] = False
        state_parms["parm_pr"]["visible"] = False
        state_parms["prim_name"]["visible"] = False

    def on_parm_changed(self, **kwargs):
        parm_tuple = kwargs["parm_tuple"] # type: hou.ParmTuple
   
        if parm_tuple is not None:

            parm_name = parm_tuple.name()

            if parm_name in self.DISPLAY_SETTINGS_PARMS:
                self.bezier_editor.set_display_settings()

            if parm_name == "use_surface":
                self.setup_surface_input()

            if parm_name == "handles_snapping":
                self.bezier_editor.handles_snapping = parm_tuple.eval()[0]

            if parm_name == "drawing_mode":
                self.bezier_editor.point_controls.projection_mode = parm_tuple.eval()[0]

            if parm_name == "current_attribute":
                self.on_current_attrib()

            if parm_name == "point_handles":
                self.show_point_handles = parm_tuple.eval()[0]
                self.bezier_editor.on_anchor_selected()
            
            if parm_name == "box_handle":
                self.show_box_handle = parm_tuple.eval()[0]
                if self.show_box_handle:
                    self.bezier_editor.calculate_multiselect_box()

            if parm_name == "display_values":
                self.show_attrib_values = parm_tuple.eval()[0]
                self.bezier_editor.attribs_dirty = True

            if parm_name == "display_names":
                self.show_names = parm_tuple.eval()[0]
                self.bezier_editor.names_dirty = True

            if parm_name == "display_tags":
                self.show_tags = parm_tuple.eval()[0]
                self.bezier_editor.tags_dirty = True

            if parm_name == "controls" and not self.bezier_editor.disable_control_sync:
                self.bezier_editor.reads(self.bezier_editor.controls_parm.evalAsString(), update_geo=False)
                self.bezier_editor.restore_selection()

            if parm_name == "update_geo_on_edit":
                self.bezier_editor.update_geo_on_edit = parm_tuple.eval()[0]

            if parm_name == "use_curve_guide":
                self.bezier_editor.use_curve_guides = parm_tuple.eval()[0]

            if parm_name == "use_arrow_heads":
                self.bezier_editor.use_arrow_heads = parm_tuple.eval()[0]

        self.show_houdini_handle() # it also force updates the state

    
    def set_position_from_parm(self, position, control_index):
        selected_controls = self.bezier_editor.point_controls.selected_controls
        current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

        if current_control is not None:
            current_anchor = self.bezier_editor.get_anchor_from_control(current_control)
            self.bezier_editor.aligned_handle_move = current_anchor.anchor_type == AnchorType.SMOOTH
            self.bezier_editor.begin_edit()
            self.bezier_editor.anchor_points_controls[current_anchor][control_index].move_to(position)
            self.bezier_editor.end_edit()
            self.bezier_editor.update_all_editor_geo()

    def onCommand(self, kwargs):
        name = kwargs["command"]

        if name == "sync_parmpane":

            value = kwargs["command_args"]["value"]
            parm_name = kwargs["command_args"]["parm_name"]
            multiparm_index = kwargs["command_args"]["multiparm_index"]

            position_parms = ["anchor_in_control", "anchor_out_control", "anchor_position"]
            if parm_name in position_parms:
                self.set_position_from_parm(hou.Vector3(value), position_parms.index(parm_name))

            parm_name_str = parm_name.rstrip(string.digits)
            is_attrib_parm = any(True for attrib_value_name in AnchorAttributeType.parm_names if parm_name_str in attrib_value_name)

            selected_controls = self.bezier_editor.point_controls.selected_controls
            current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

            if is_attrib_parm:
                attrib_name = self.node.parm("attrib_name{}".format(multiparm_index)).eval()
                is_pr_attrib = attrib_name in ["Pscale", "Roll"]
                __pr_index = 0 if is_pr_attrib and attrib_name == "Pscale" else 1

                attrib_name = "__pr" if is_pr_attrib else attrib_name

                attrib_value = value[0] if len(value) == 1 else value

                
                
                if selected_controls:
                    self.bezier_editor.begin_edit()

                    for control in selected_controls:
                        anchor = self.bezier_editor.get_anchor_from_control(control)
                        if not is_pr_attrib:
                            anchor.attributes[attrib_name] = attrib_value
                        else:
                            anchor.attributes["__pr"][__pr_index] = attrib_value

                    self.bezier_editor.end_edit()

                    self.bezier_editor.attribs_dirty = True

            if parm_name in ["prim_name", "prim_closed"]:
                if current_control is not None:
                    current_anchor = self.bezier_editor.get_anchor_from_control(current_control)
                    current_prim = self.bezier_editor.get_anchor_prim(current_anchor.anchor_index)

                    if parm_name == "prim_name":
                        self.bezier_editor.begin_edit()
                        self.bezier_editor.prims[current_prim][3] = value[0]
                        self.bezier_editor.end_edit()
                        self.bezier_editor.names_dirty = True

                    if parm_name == "prim_closed":
                        self.bezier_editor.begin_edit()
                        self.bezier_editor.prims[current_prim][2] = value[0]
                        self.bezier_editor.end_edit()

            if parm_name == "anchor_type":
                if current_control is not None:
                    current_anchor = self.bezier_editor.get_anchor_from_control(current_control)
                    self.bezier_editor.begin_edit()
                    self.bezier_editor.set_anchor_type(current_anchor, value[0])
                    self.bezier_editor.end_edit()

            if parm_name == "anchor_tag":
                if selected_controls:
                    self.bezier_editor.begin_edit()

                    for control in selected_controls:
                        anchor = self.bezier_editor.get_anchor_from_control(control)
                        anchor.tag = value[0]

                    self.bezier_editor.end_edit()

                    self.bezier_editor.tags_dirty = True
                        



    def onKeyEvent(self, kwargs):
        ui_event = kwargs["ui_event"] # type: hou.UIEvent
        device = ui_event.device() # type: hou.UIEventDevice

        if "Del" in device.keyString():
            return self.bezier_editor.remove_selected_anchors()

        return False

    def onMouseDoubleClickEvent(self, kwargs):
        ui_event = kwargs["ui_event"] # type: hou.UIEvent
        device = ui_event.device() # type: hou.UIEventDevice

        hovered_control = self.bezier_editor.point_controls.hovered_control
        hovered_prim = hovered_anchor = None

        if self.bezier_editor.curve_pos_under_cursor is not None:
            hovered_prim = self.bezier_editor.geo_prims[self.bezier_editor.curve_prim_under_cursor]

        if hovered_control is not None and hovered_control.tag == "position":
            hovered_anchor = self.bezier_editor.get_anchor_from_control(hovered_control)
            hovered_prim = self.bezier_editor.get_anchor_prim(hovered_anchor.anchor_index)

        if hovered_prim is not None:
            if device.isShiftKey():
                self.bezier_editor.add_prim_to_selection(hovered_prim)
            else:
                self.bezier_editor.select_prim(hovered_prim)
            self.double_clicked = True
            return True
        
        return False

        

    def onMouseEvent(self, kwargs):
        ui_event = kwargs["ui_event"] # type: hou.UIEvent
        state_parms = kwargs["state_parms"]

        self.last_cursor_world_pos = self.bezier_editor.point_controls.get_construction_point(ui_event)
        self.last_cursor_normal = self.bezier_editor.point_controls.surface_normal

        # Consume after double click
        if self.double_clicked:
            self.double_clicked = False
            return

        origin, direction = ui_event.ray() # type: hou.Vector3, hou.Vector3
        device = ui_event.device() # type: hou.UIEventDevice
        reason = ui_event.reason() # type: hou.uiEventReason

        viewport = self.scene_viewer.curViewport() # type: hou.GeometryViewport

        left_button = device.isLeftButton()
        middle_button = device.isMiddleButton()

        gi = su.GeometryIntersector(self.bezier_editor.curve_geo, tolerance=0.02)
        gi.intersect(origin, direction)

        geo = hou.Geometry()
        self.bezier_editor.curve_pos_under_cursor = None
        if gi.prim_num > -1 and self.bezier_editor.point_controls.hovered_control is None:
            
            curve_prim = self.bezier_editor.curve_geo.prim(gi.prim_num) # type: hou.Prim
            intersect_pos = curve_prim.positionAtInterior(gi.uvw[0], gi.uvw[1], gi.uvw[2])
            self.bezier_editor.curve_pos_under_cursor = gi.uvw[0]
            self.bezier_editor.curve_prim_under_cursor = gi.prim_num
            
            geo.createPoints((intersect_pos,))
            
        self.point_drawable.setGeometry(geo)

        if reason == hou.uiEventReason.Active or reason == hou.uiEventReason.Located:
            self.on_mouse_move(ui_event)
            # force snapping UI on move
            if self.bezier_editor.point_controls.enable_snapping:
                snapping_ray = ui_event.snappingRay()

        if reason == hou.uiEventReason.Picked and left_button:
            self.on_mouse_down(ui_event)
            self.on_mouse_up(ui_event)

        if reason == hou.uiEventReason.Changed:
            self.on_mouse_up(ui_event)

            if self.ladder_opened:
                hou.ui.closeValueLadder()
                self.ladder_opened = False
                self.bezier_editor.end_edit()
                

        if reason == hou.uiEventReason.Start and left_button:
            self.on_mouse_down(ui_event)
            #self.on_mouse_move(ui_event)

        if middle_button and reason == hou.uiEventReason.Start and not self.ladder_opened:
            selected_controls = self.bezier_editor.point_controls.selected_controls
            current_control = None if not selected_controls or len(selected_controls) > 1 else selected_controls[0]

            if self.bezier_editor.current_attribute is not None:
                attribute_type = self.bezier_editor.current_attribute_class.type

                if attribute_type == AnchorAttributeType.FLOAT_LADDER or attribute_type == AnchorAttributeType.INTEGER_LADDER:
                    ladder_type = hou.valueLadderDataType.Float if attribute_type == AnchorAttributeType.FLOAT_LADDER else hou.valueLadderDataType.Int
                    anchor = self.bezier_editor.get_anchor_from_control(current_control)
                    initial_value = anchor.attributes[self.bezier_editor.current_attribute]
                    self.bezier_editor.begin_edit()
                    hou.ui.openValueLadder(initial_value, self.on_ladder, data_type=ladder_type)
                    self.ladder_opened = True

        if middle_button and reason == hou.uiEventReason.Active and self.ladder_opened:
            hou.ui.updateValueLadder(
                int(device.mouseX()),
                int(device.mouseY()),
                device.isAltKey(),
                device.isShiftKey()
            )

    def on_rewired(self, **kwargs):
        self.setup_surface_input()

    def setup_surface_input(self):
        use_surface = self.node.parm("use_surface").evalAsInt()
        surface_input = node_input(self.node, 1)

        self.bezier_editor.point_controls.surface_geo = None
        self.bezier_editor.point_controls.surface_normal_attrib = None

        if use_surface and surface_input is not None:
            surface_geo = surface_input.geometry() # type: hou.Geometry

            if surface_geo is not None:

                self.bezier_editor.point_controls.surface_geo = surface_geo

                normal_attrib = surface_geo.findVertexAttrib("N") # type: hou.Attrib
                normal_attrib = surface_geo.findPointAttrib("N") if normal_attrib is None else normal_attrib

                if normal_attrib is not None:
                    valid_normal = normal_attrib.dataType() == hou.attribData.Float and normal_attrib.size() == 3
                    self.bezier_editor.point_controls.surface_normal_attrib = normal_attrib if valid_normal else None

    def hide_all_houdini_handles(self):
        self.point_translate_handle.show(False)
        self.pscale_handle.show(False)
        self.spin_handle.show(False)
        self.vector_handle.show(False)
        self.box_handle.show(False)
        self.angle_handle.show(False)

    def show_attribute_handle(self):
        if self.bezier_editor.current_attribute is not None and self.bezier_editor.editing_anchor >= 0:
            attribute_type = self.bezier_editor.attribute_names[self.bezier_editor.current_attribute].type
            attribute_handles = AnchorAttributeType.meta[attribute_type][3]
            for handle in attribute_handles:
                if handle != "None":
                    self.hou_handles[handle].show(True)

    def show_houdini_handle(self):
        self.hide_all_houdini_handles()

        if self.show_box_handle and len(self.bezier_editor.point_controls.selected_controls) > 1:
            self.box_handle.show(True)
            self.box_handle.update()
        elif self.show_point_handles and self.bezier_editor.point_controls.selected_controls:
            self.point_translate_handle.show(True)
            self.point_translate_handle.update()
        else:
            self.show_attribute_handle()

    def set_corner_text(self):
        label = "<font color=green>ON</font>" if self.bezier_editor.draw_mode else "<font color=red>OFF</font>"
        text = "<b><font face='Source Code Pro' size=4>Drawing mode: " + label + "</font></b>"
        self.corner_text_drawable.setParams({
            "text": text
        })
        self.scene_viewer.curViewport().draw()

    def show_snapping_warning(self):
        node_visible = self.node.isDisplayFlagSet()
        correct_mode = self.bezier_editor.use_curve_guides and not self.bezier_editor.update_geo_on_edit

        snapping_mode = self.scene_viewer.snappingMode()
        geo_snapping = ( snapping_mode == hou.snappingMode.Point or snapping_mode == hou.snappingMode.Prim )

        if node_visible and geo_snapping and not correct_mode:
            self.warning_drawable.setParams({
                "text": "<font size=4><font size=5 color=yellow><b>Warning: </b></font> To correctly use current snapping mode turn <b>Curve Guides</b> on and turn <b>Update Geo While Editing</b> off!</font>",
            })
            self.warning_drawable.show(True)
        else:
            self.warning_drawable.show(False)


    
    def onDraw( self, kwargs ):
        """ This callback is used for rendering the drawables
        """
        handle = kwargs["draw_handle"]

        self.bezier_editor.draw(handle)
        self.point_drawable.draw(handle)

        self.show_snapping_warning()

        self.warning_drawable.draw(handle)
        self.corner_text_drawable.draw(handle)

    def onDrawInterrupt(self, kwargs):
        handle = kwargs["draw_handle"]
        self.bezier_editor.draw(handle)


    def show_curve_menu(self, menu_item_states, show):
        menu_items = ["curve_actions_label", "closed_curve", 
            "remove_curve", "select_curve", "add_curve_to_selection", "reverse_curve", "duplicate_curve"]
        
        for item in menu_items:
            menu_item_states[item]["visible"] = show

    def show_anchor_menu(self, menu_item_states, show):
        menu_items = ["anchor_actions_label", "remove_anchor", "anchor_type_menu", "anchor_project",
            "anchor_align", "auto_smooth_anchor", "rewire_anchor", "straighten"]

        for item in menu_items:
            menu_item_states[item]["visible"] = show


    def onMenuPreOpen(self, kwargs):
        """ Implement this callback to update the menu content before 
            it is drawn. 
        """
        menu_states = kwargs["menu_states"]
        menu_item_states = kwargs["menu_item_states"]
        menu_id = kwargs["menu"]
        ui_event = kwargs["ui_event"]

        self.menu_world_position = self.last_cursor_world_pos
        self.menu_world_normal = self.last_cursor_normal

        hovered_control = self.bezier_editor.point_controls.hovered_control
        hovered_prim = hovered_anchor = None

        multiselection = False
        selected_anchors = []
        action_anchors = []

        if self.bezier_editor.curve_pos_under_cursor is not None:
            hovered_prim = self.bezier_editor.geo_prims[self.bezier_editor.curve_prim_under_cursor]

        if hovered_control is not None and hovered_control.tag == "position":
            hovered_anchor = self.bezier_editor.get_anchor_from_control(hovered_control)
            hovered_prim = self.bezier_editor.get_anchor_prim(hovered_anchor.anchor_index)

        if len(self.bezier_editor.point_controls.selected_controls) > 1:
            multiselection = True
            selected_anchors = [self.bezier_editor.get_anchor_from_control(control) for control in self.bezier_editor.point_controls.selected_controls]

        if hovered_anchor is not None and hovered_anchor not in selected_anchors:
            action_anchors = [hovered_anchor]
        else:
            action_anchors = selected_anchors

        if menu_id == "pen_menu":

            #self.menu_world_position = self.bezier_editor.point_controls.get_construction_point(ui_event)

            if hovered_prim is not None:
                self.show_curve_menu(menu_item_states, True)
                menu_item_states["closed_curve"]["value"] = int(self.bezier_editor.prims[hovered_prim][2])
            else:
                self.show_curve_menu(menu_item_states, False)

            if action_anchors:
                self.show_anchor_menu(menu_item_states, True)
            else:
                self.show_anchor_menu(menu_item_states, False)

            if self.show_box_handle and len(self.bezier_editor.point_controls.selected_controls) > 1:
                menu_item_states["reset_selection_transform"]["visible"] = True
            else:
                menu_item_states["reset_selection_transform"]["visible"] = False

            if self.last_shape is not None:
                menu_item_states["insert_last_shape"]["visible"] = True
            else:
                menu_item_states["insert_last_shape"]["visible"] = False

            menu_item_states["enable_drawing"]["value"] = int(self.bezier_editor.draw_mode)
            menu_item_states["show_box_handles"]["value"] = int(self.show_box_handle)
            menu_item_states["show_attribute_values"]["value"] = int(self.show_attrib_values)
            menu_item_states["show_prim_names"]["value"] = int(self.show_names)
            menu_item_states["show_translate_handles"]["value"] = int(self.show_point_handles)
            menu_item_states["enable_handles_snapping"]["value"] = int(self.bezier_editor.handles_snapping)

            num_anchors = len(action_anchors)
            anchor_label = "Anchor Actions" if num_anchors < 2 else "Anchor Actions ({} selected)".format(num_anchors)
            
            menu_item_states["anchor_actions_label"]["label"] = anchor_label

        if menu_id == "curve_actions_label":
            menu_item_states["curve_action_dummy"]["visible"] = False

        if menu_id == "anchor_actions_label":
            menu_item_states["anchor_action_dummy"]["visible"] = False

        if menu_id == "anchor_type":
            if hovered_anchor is not None:
                menu_states["value"] = State.ANCHOR_TYPE_TO_MENU_PARM[hovered_anchor.anchor_type]

    def onMenuAction(self, kwargs):
        """ Callback implementing the actions of a bound menu. Called 
        when a menu item has been selected. 
        """
        menu_item = kwargs["menu_item"]
        hovered_control = self.bezier_editor.point_controls.hovered_control
        hovered_prim = hovered_anchor = None

        multiselection = False
        selected_anchors = []
        action_anchors = []

        if self.bezier_editor.curve_pos_under_cursor is not None:
            hovered_prim = self.bezier_editor.geo_prims[self.bezier_editor.curve_prim_under_cursor]

        if hovered_control is not None and hovered_control.tag == "position":
            hovered_anchor = self.bezier_editor.get_anchor_from_control(hovered_control)
            hovered_prim = self.bezier_editor.get_anchor_prim(hovered_anchor.anchor_index)

        if len(self.bezier_editor.point_controls.selected_controls) > 1:
            multiselection = True
            selected_anchors = [self.bezier_editor.get_anchor_from_control(control) for control in self.bezier_editor.point_controls.selected_controls]

        if hovered_anchor is not None and hovered_anchor not in selected_anchors:
            action_anchors = [hovered_anchor]
        else:
            action_anchors = selected_anchors

        if menu_item == "insert_shape":
            shape = self.bezier_editor.select_custom_shape()

            if shape is not None and self.menu_world_position is not None:
                self.bezier_editor.insert_custom_shape(self.menu_world_position, self.menu_world_normal, shape)
                self.last_shape = shape

        if menu_item == "insert_last_shape":
            if self.last_shape is not None and self.menu_world_position is not None:
                self.bezier_editor.insert_custom_shape(self.menu_world_position, self.menu_world_normal, self.last_shape)

        if menu_item == "enable_drawing":
            self.bezier_editor.draw_mode = not self.bezier_editor.draw_mode
            self.set_corner_text()

        if menu_item == "remove_anchor" and action_anchors:
            self.bezier_editor.begin_edit()
            for anchor in action_anchors:
                self.bezier_editor.remove_anchor(anchor)
            self.bezier_editor.end_edit()

            self.bezier_editor.update_all_editor_geo()
            self.bezier_editor.point_controls.show_hovered(False)
            self.bezier_editor.on_anchor_selected()

        if menu_item == "rewire_anchor" and len(action_anchors) == 1:
            self.bezier_editor.begin_edit()
            self.bezier_editor.rewire_prim(action_anchors[0].anchor_index)
            self.bezier_editor.end_edit()

        if menu_item == "remove_curve" and hovered_prim is not None:
            self.bezier_editor.begin_edit()
            self.bezier_editor.remove_prim(hovered_prim)
            self.bezier_editor.end_edit()

            self.bezier_editor.update_all_editor_geo()
            if hovered_anchor is not None:
                self.bezier_editor.point_controls.show_hovered(False)
            self.bezier_editor.on_anchor_selected()

        if menu_item == "select_all":
            self.bezier_editor.select_all()

        if menu_item == "select_none":
            self.bezier_editor.clear_selection()

        if menu_item == "duplicate_curve" and hovered_prim is not None:
            self.bezier_editor.duplicate_prim(self.menu_world_position, hovered_prim)

        if menu_item == "select_curve" and hovered_prim is not None:
            self.bezier_editor.select_prim(hovered_prim)

        if menu_item == "add_curve_to_selection" and hovered_prim is not None:
            self.bezier_editor.add_prim_to_selection(hovered_prim)

        if menu_item == "closed_curve" and hovered_prim is not None:
            is_closed = kwargs["closed_curve"]

            self.bezier_editor.begin_edit()
            self.bezier_editor.close_prim(hovered_prim, is_closed)
            self.bezier_editor.end_edit()

        if menu_item == "reverse_curve" and hovered_prim is not None:
            self.bezier_editor.begin_edit()
            self.bezier_editor.reverse_prim(hovered_prim)
            self.bezier_editor.end_edit()

        if menu_item == "show_translate_handles":
            self.node.parm("point_handles").set(kwargs["show_translate_handles"])

        if menu_item == "show_box_handles":
            self.node.parm("box_handle").set(kwargs["show_box_handles"])

        if menu_item == "show_attribute_values":
            self.node.parm("display_values").set(kwargs["show_attribute_values"])

        if menu_item == "show_prim_names":
            self.node.parm("display_names").set(kwargs["show_prim_names"])

        if menu_item == "enable_handles_snapping":
            self.node.parm("handles_snapping").set(kwargs["enable_handles_snapping"])

        if menu_item == "reset_selection_transform":
            self.bezier_editor.calculate_multiselect_box()
            self.box_handle.show(self.show_box_handle) #TODO: force update workaround?
            self.box_handle.update()

        if menu_item == "anchor_type" and action_anchors:
            anchor_type = State.MENU_PARM_TO_ANCHOR_TYPE[kwargs["anchor_type"]]
            self.bezier_editor.begin_edit()
            for anchor in action_anchors:
                self.bezier_editor.set_anchor_type(anchor, anchor_type)
            self.bezier_editor.end_edit()

        if menu_item == "auto_smooth_anchor" and action_anchors:

            self.bezier_editor.begin_edit()
            for anchor in action_anchors:
                self.bezier_editor.set_anchor_type(anchor, AnchorType.SMOOTH)
                self.bezier_editor.anchor_auto_gradient(anchor)
            self.bezier_editor.end_edit()

        if menu_item.startswith("align_") and action_anchors:
            tokens = menu_item.split("_")

            axis = {
                "x": 0,
                "y": 1,
                "z": 2
            } [tokens[1]]

            mode_func = {
                "max": np.max,
                "min": np.min,
                "avrg": np.mean
            } [tokens[2]]

            value = mode_func([anchor.position[axis] for anchor in action_anchors])

            self.bezier_editor.begin_edit()
            for anchor in action_anchors: # type: AnchorPoint
                anchor.position[axis] = anchor.controls[0][axis] = anchor.controls[1][axis] = value
            self.bezier_editor.end_edit()

            self.bezier_editor.update_all_editor_geo()

        if menu_item == "straighten" and action_anchors:
            self.bezier_editor.straighten_anchors()

        if menu_item.startswith("anchor_proj_") and action_anchors:
            tokens = menu_item.split("_")

            world_origin = hou.Vector3(0, 0, 0)
            construction_plane = self.scene_viewer.constructionPlane() # type: hou.ConstructionPlane

            plane_origin = {
                "xy": world_origin,
                "yz": world_origin,
                "xz": world_origin,
                "cp": world_origin * construction_plane.transform()
            } [tokens[2]]

            plane_normal = {
                "xy": hou.Vector3(0, 0, 1),
                "yz": hou.Vector3(1, 0, 0),
                "xz": hou.Vector3(0, 1, 0),
                "cp": hou.Vector3(0, 0, 1) * construction_plane.transform().inverted().transposed()
            } [tokens[2]]

            self.bezier_editor.begin_edit()
            for anchor in action_anchors:
                anchor.position = hou.hmath.intersectPlane(plane_origin, plane_normal, anchor.position, plane_normal)
                anchor.controls[0] = hou.hmath.intersectPlane(plane_origin, plane_normal, anchor.controls[0], plane_normal)
                anchor.controls[1] = hou.hmath.intersectPlane(plane_origin, plane_normal, anchor.controls[1], plane_normal)
                self.bezier_editor.sync_anchor_controls(anchor)
            self.bezier_editor.end_edit()

            self.bezier_editor.update_all_editor_geo()


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "ie::pen_tool_state"
    state_label = "IE|Pen Tool"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)

    node_type: hou.NodeType = hou.nodeType(hou.sopNodeTypeCategory(), "ie::pen_tool::1.0")

    template.bindIcon(node_type.icon())

    template.bindHandle("xform", "spin_handle", cache_previous_parms=True)
    template.bindHandle("xform", "pscale_handle")
    template.bindHandle("xform", "point_translate_handle")
    template.bindHandle("vector", "vector_handle")
    template.bindHandle("angle", "angle_handle")
    template.bindHandle("boundingbox", "box_handle")

    menu = hou.ViewerStateMenu("pen_menu", "IE::Pen")

    # General actions
    menu.addSeparator()

    menu.addActionItem("insert_shape", "Insert Custom Shape")    
    menu.addActionItem("insert_last_shape", "Insert Last Shape")

    hotkey = su.hotkey(state_typename, "enable_drawing", "a", "Enable Point Translate Handle")
    menu.addToggleItem("enable_drawing", "Enable Drawing Mode", False, hotkey=hotkey)

    hotkey = su.hotkey(state_typename, "show_translate_handles", "h", "Enable Point Translate Handle")
    menu.addToggleItem("show_translate_handles", "Enable Point Translate Handle", False, hotkey=hotkey)
    
    menu.addToggleItem("enable_handles_snapping", "Enable Handles Snapping", False)

    hotkey = su.hotkey(state_typename, "show_box_handles", "b", "Enable Box Handle")
    menu.addToggleItem("show_box_handles", "Enable Box Handle", False, hotkey=hotkey)
    
    menu.addToggleItem("show_attribute_values", "Display Attribute Values", False)
    
    menu.addToggleItem("show_prim_names", "Display Prim Names", False)

    hotkey = su.hotkey(state_typename, "select_all", "shift+a", "Select All")
    menu.addActionItem("select_all", "Select All", hotkey=hotkey)
    
    hotkey = su.hotkey(state_typename, "select_none", "shift+z", "Clear Selection")
    menu.addActionItem("select_none", "Clear Selection", hotkey=hotkey)
    
    hotkey = su.hotkey(state_typename, "reset_selection_transform", "shift+B", "Reset Box Selection Transform")
    menu.addActionItem("reset_selection_transform", "Reset Box Selection Transform", hotkey=hotkey)

    menu.addSeparator()

    # Anchor actions
    menu.addRadioStrip("anchor_actions_label", "Anchor Actions", "anchor_action_dummy")
    menu.addRadioStripItem("anchor_actions_label", "anchor_action_dummy", "Dummy")

    menu.addActionItem("remove_anchor", "Remove anchor")
    hotkey = su.hotkey(state_typename, "auto_smooth_anchor", "shift+S", "Auto Smooth Anchor")
    menu.addActionItem("auto_smooth_anchor", "Auto Smooth Anchor", hotkey=hotkey)
    menu.addActionItem("rewire_anchor", "Rewire From Anchor")

    anchor_type_menu = hou.ViewerStateMenu("anchor_type_menu", "Select Anchor Type") # type: hou.ViewerStateMenu
    anchor_type_menu.addRadioStrip("anchor_type", "Anchor Type", "smooth")
    anchor_type_menu.addRadioStripItem("anchor_type", "smooth", "Smooth")
    anchor_type_menu.addRadioStripItem("anchor_type", "untied", "Untied")
    anchor_type_menu.addRadioStripItem("anchor_type", "corner", "Corner")

    menu.addMenu(anchor_type_menu)

    menu.addActionItem("straighten", "Straighten Anchors")
    
    anchor_project_menu = hou.ViewerStateMenu("anchor_project", "Project To") # type: hou.ViewerStateMenu
    anchor_project_menu.addActionItem("anchor_proj_xy", "XY")
    anchor_project_menu.addActionItem("anchor_proj_xz", "XZ")
    anchor_project_menu.addActionItem("anchor_proj_yz", "YZ")
    anchor_project_menu.addActionItem("anchor_proj_cp", "Construction")

    menu.addMenu(anchor_project_menu)

    anchor_align_menu = hou.ViewerStateMenu("anchor_align", "Align To") # type: hou.ViewerStateMenu

    anchor_align_menu_x = hou.ViewerStateMenu("align_x", "X Axis") # type: hou.ViewerStateMenu
    anchor_align_menu_x.addActionItem("align_x_avrg", "Average")
    anchor_align_menu_x.addActionItem("align_x_max", "Max")
    anchor_align_menu_x.addActionItem("align_x_min", "Min")
    anchor_align_menu.addMenu(anchor_align_menu_x)

    anchor_align_menu_y = hou.ViewerStateMenu("align_y", "Y Axis") # type: hou.ViewerStateMenu
    anchor_align_menu_y.addActionItem("align_y_avrg", "Average")
    anchor_align_menu_y.addActionItem("align_y_max", "Max")
    anchor_align_menu_y.addActionItem("align_y_min", "Min")
    anchor_align_menu.addMenu(anchor_align_menu_y)

    anchor_align_menu_z = hou.ViewerStateMenu("align_z", "Z Axis") # type: hou.ViewerStateMenu
    anchor_align_menu_z.addActionItem("align_z_avrg", "Average")
    anchor_align_menu_z.addActionItem("align_z_max", "Max")
    anchor_align_menu_z.addActionItem("align_z_min", "Min")
    anchor_align_menu.addMenu(anchor_align_menu_z)

    menu.addMenu(anchor_align_menu)


    menu.addSeparator()

    # Curve Actions
    menu.addRadioStrip("curve_actions_label", "Curve Actions", "curve_action_dummy")
    menu.addRadioStripItem("curve_actions_label", "curve_action_dummy", "Dummy")

    menu.addToggleItem("closed_curve", "Closed curve", False)
    menu.addActionItem("duplicate_curve", "Duplicate curve")
    menu.addActionItem("reverse_curve", "Reverse curve")
    menu.addActionItem("remove_curve", "Remove curve")
    menu.addActionItem("select_curve", "Select all curve anchors")
    menu.addActionItem("add_curve_to_selection", "Add all curve anchors to selection")
    

    template.bindMenu(menu)

    return template