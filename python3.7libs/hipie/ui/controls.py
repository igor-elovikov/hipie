# Generic Point Controls State

from __future__ import annotations

import inspect
import traceback
from collections import Iterable
from typing import Optional

import hou
import numpy as np
import viewerstate.utils as su

def_pcontrol_params = {
    "radius": 11,
    "color1": (1.0,1.0,0.8,1.0),
    "color2": (0.0,0.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.SmoothCircle,
    "highlight_mode": hou.drawableHighlightMode.MatteOverGlow,
    "falloff_range": (0.65, 0.75),
    "num_rings": 1,
    "fade_factor": 0.95,
    "glow_width": 1,
}
 
def_pcontrol_hover_params = {
    "radius": 15,
    "style": hou.drawableGeometryPointStyle.RingsCircle,
    "color1": (1.0,1.0,0.7,1.0),
    "falloff_range": (0.7, 0.99),
}

def_pcontrol_selected_params = {
    "radius": 9,
    "color1": (0.0,1.0,0.0,1.0),
    "style": hou.drawableGeometryPointStyle.SmoothCircle,
    "falloff_range": (0.65, 0.95),
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

class MovingType:
    FREE_DRAG = 0
    HANDLES_ONLY = 1

# Simple point control with callbacks on moving
class PointControl(object):

    def __init__(self, position = hou.Vector3(0, 0, 0), drawable_index=0, tag=""):
        self.position = position
        self.drawable_index = drawable_index
        self.is_visible = True
        self._on_move = None
        self._on_select = None
        self.tag = tag
        self.attributes = {} 
        self.geo_point = None # type: hou.Point

    def set_attribute_value(self, name, value):
        self.attributes[name] = value
        self.geo_point.setAttribValue(name, value)

    def move_to(self, position):
        self.position = position
        if self.geo_point is not None:
            self.geo_point.setPosition(position)
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
        self.drag_start = False
        self.plane_point = hou.Vector3()

        self.projection_mode = projection_mode
        self.enable_snapping = True
        self.surface_geo = None # type: hou.Geometry
        self.surface_normal = None # type: hou.Vector3
        self.surface_hit_prim = -1 # type: int

        self.on_hover_update = lambda hover_control, prev_control: None
        self.on_control_moved = lambda control, new_position, old_position: None
        self.on_control_start_move = lambda control: None
        self.on_control_end_move = lambda control: None

        self.cached_construction_point = None # type: hou.Vector3

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
            point_positions = [control.position for control in self.point_controls if control.drawable_index == index and control.is_visible]
            geo.createPoints(point_positions)
            drawable._points_drawable.setGeometry(geo)

    def update_hovered_geo(self):
        for index, drawable in enumerate(self.drawables):
            geo = hou.Geometry()
            if self.hovered_control is not None and index == self.hovered_control.drawable_index:
                geo.createPoints([self.hovered_control.position])
            drawable._hovered_drawable.setGeometry(geo) 

    def show_hovered(self, show):
        for drawable in self.drawables:
            drawable._hovered_drawable.show(show)

    def update_selected_geo(self):
        for index, drawable in enumerate(self.drawables):
            point_positions = [c.position for c in self.selected_controls if c.drawable_index == index and c.is_visible]
            geo = hou.Geometry()
            if point_positions:
                geo.createPoints(point_positions)
            drawable._selected_drawable.setGeometry(geo)

    def add_control(self, position: hou.Vector3, drawable_index=0, tag=""):
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
            point_screen_pos = viewport.mapToScreen(point_control.position * viewport.modelToGeometryTransform().inverted()) # type: hou.Vector2

            dev = ui_event.device() # type: hou.UIEventDevice

            mouse_pos = hou.Vector3(dev.mouseX(), dev.mouseY(), 0.0)
            mouse_pos *= viewport.windowToViewportTransform()
            mouse_pos = hou.Vector2(mouse_pos.x(), mouse_pos.y())

            distance_to_cursor = (point_screen_pos - mouse_pos).lengthSquared()

            if distance_to_cursor < self.hover_tolerance and distance_to_cursor < max_distance:
                self.hovered_control = point_control
                max_distance = distance_to_cursor

        if self.hovered_control is not None and self.hovered_control is not prev_control:
            self.update_hovered_geo()
            self.show_hovered(True)
            self.on_hover_update(self.hovered_control, prev_control)
        
        if self.hovered_control is None:
            self.show_hovered(False)
            if prev_control is not None:
                self.on_hover_update(self.hovered_control, prev_control)

    def select_point(self):
        # type: () -> PointControl
        if self.hovered_control is not None:
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

    def unselect_control(self, point_control, update_geo=True):
        if point_control in self.selected_controls:
            self.selected_controls.remove(point_control)
            if update_geo:
                self.update_selected_geo()

    def select_controls(self, controls):
        for control in controls:
            self.add_control_to_selection(control, False)
        self.update_selected_geo()

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
            if self.drag_start and self.dragged_control is not None:
                self.plane_point = self.dragged_control.position
                self.on_control_start_move(self.dragged_control)
                self.drag_start = False
            self.on_mouse_drag(ui_event)

        self.cached_construction_point = None

    def get_surface_hit_prim(self):
        # type: () -> hou.Prim
        if self.surface_geo is not None and self.surface_hit_prim >= 0:
            return self.surface_geo.prim(self.surface_hit_prim)
        return None

    def get_construction_point(self, ui_event, force_update=False):
        # type (hou.UIEvent) -> hou.Vector3
        print("".join(traceback.format_stack()))

        if self.cached_construction_point is not None and not force_update:
            return self.cached_construction_point

        self.surface_normal = None
        snapping_ray = None
        if self.enable_snapping:
            snapping_ray = ui_event.snappingRay()
            origin: hou.Vector3
            direction: hou.Vector3
            origin, direction = snapping_ray["origin_point"], snapping_ray["direction"] 
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
            plane_normal = -camera_look

            cplane = self.scene_viewer.constructionPlane() # type: hou.ConstructionPlane

            if cplane.isVisible():
                cplane_transform = cplane.transform() # type: hou.Matrix4
                plane_point = hou.Vector3(0.0, 0.0, 0.0) * cplane_transform
                plane_normal = hou.Vector3(0.0, 0.0, 1.0) * cplane_transform.inverted().transposed()

        try:
            construction_point = hou.hmath.intersectPlane(plane_point, plane_normal, origin, direction)
            self.surface_normal = plane_normal
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
                        geo_point = geo.point(snapping_ray["point_index"]) # type: hou.Point
                        construction_point = geo_point.position()

                        ref_plane = self.scene_viewer.referencePlane()
                        cplane = self.scene_viewer.constructionPlane() # type: hou.ConstructionPlane

                        if ref_plane is not None and cplane is not None:
                            transform = cplane.transform() if cplane.isVisible() else ref_plane.transform()
                            self.surface_normal = hou.Vector3(0.0, 0.0, 1.0) * transform.inverted().transposed()

                    if geo_type == hou.snappingPriority.GeoPrim:
                        geo = hou.nodeBySessionId(snapping_ray["node_id"]).geometry()
                        prim_index = snapping_ray["prim_index"]
                        geo_prim = geo.prim(prim_index) # type: hou.Prim

                        position = hou.Vector3()
                        normal = hou.Vector3()
                        uvw = hou.Vector3()

                        intersect_prim = geo.intersect(origin, direction, position, normal, uvw, str(geo_prim))
                        if intersect_prim == prim_index:
                            construction_point = geo_prim.positionAtInterior(uvw.x(), uvw.y(), uvw.z())
            except TypeError:
                construction_point = None

        if self.surface_geo is not None and self.enable_snapping:

            gi = su.GeometryIntersector(self.surface_geo, tolerance=0.02)
            gi.intersect(origin, direction)

            self.surface_hit_prim = -1

            if gi.prim_num > -1:
                
                construction_point = gi.position 
                self.surface_normal = gi.normal
                self.surface_hit_prim = gi.prim_num

                # currently hou.Geometry.intersect doesn't give you correct normal with non-uniform scales
                prim = self.surface_geo.prim(gi.prim_num) # type: hou.PackedPrim
                if isinstance(prim, hou.PackedPrim):
                    prim_transform = prim.transform() # type: hou.Matrix4
                    self.surface_normal *= prim_transform.inverted()
                    prim_full_transform = prim.fullTransform()
                    self.surface_normal *= prim_full_transform.inverted().transposed()
                    

        self.cached_construction_point = construction_point
        return construction_point

    def on_mouse_drag(self, ui_event):
        # type: (hou.UIEvent) -> None
        if not self.selected_controls or self.dragged_control is None:
            return

        construction_point = self.get_construction_point(ui_event)

        if construction_point is not None:

            old_position = self.dragged_control.position

            self.dragged_control.move_to(construction_point)
            self.on_control_moved(self.dragged_control, construction_point, old_position)

            self.update_points_geo()
            self.update_hovered_geo()
            self.update_selected_geo()

    def on_mouse_down(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.dragging = True
        self.drag_start = True
        
    def on_mouse_up(self, ui_event):
        # type: (hou.UIEvent) -> None
        if not self.drag_start and self.dragging and self.dragged_control is not None:
            self.on_control_end_move(self.dragged_control)
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


BUILTIN_TO_ATTRIBDATA = {
    float: hou.attribData.Float,
    int: hou.attribData.Int,
    str: hou.attribData.String 
#    hou.attribData.Dict: dict # Disable for now
}

class AttributeMeta:

    def __init__(self, name, default_value, control_parm=None, allow_multiedit=False):

        self.control_parm = control_parm
        self.name = name
        self.allow_multiedit = allow_multiedit

        if isinstance(default_value, str):
            value_type = str
            self.size = 1
        elif isinstance(default_value, Iterable):
            value_type = type(default_value[0])
            if not all(type(v) == value_type for v in default_value):
                raise TypeError("Attribute default value contains different types")
            if value_type not in (float, int):
                raise TypeError("Incorrect type for default value tuple (not integer or float)")
            self.size = len(default_value)
        else:
            value_type = type(default_value)
            if value_type not in BUILTIN_TO_ATTRIBDATA:
                raise TypeError("Incorrect type for default value (not string, integer or float)")
            self.size = 1

        self.default_value = default_value
        self.type = BUILTIN_TO_ATTRIBDATA[value_type]

    def is_same_type(self, attrib):
        # type: (hou.Attrib) -> bool
        return attrib.dataType() == self.type and attrib.size() == self.size

    def is_value_correct(self, value):
        if isinstance(value, Iterable) and len(value) == self.size:
            value_type = type(value[0])
            if not all(type(v) == value_type for v in value_type):
                return False
            return BUILTIN_TO_ATTRIBDATA[type(value_type)] == self.type if type(value_type) in BUILTIN_TO_ATTRIBDATA else False
        elif not isinstance(value, Iterable):
            return BUILTIN_TO_ATTRIBDATA[type(value)] == self.type if type(value) in BUILTIN_TO_ATTRIBDATA else False
        return False

class PointHandle:

    def __init__(self, name, attrib_mapping, handle, disabled_parms, on_update=lambda parms, new_values, old_values: None):
        self.name = name
        self.attrib_mapping = attrib_mapping
        self.new_values = {}
        self.old_values = {}
        for key in attrib_mapping:
            self.new_values[key] = None
            self.old_values[key] = None
        self.disabled_parms = disabled_parms
        self.handle = handle # type: hou.Handle
        self.on_update = on_update
        self.state: PointControlsState = None
        self.enabled = True
    
    def move_to(self, parms, position):
        # type: (dict, hou.Vector3) -> None
        parms["tx"] = position.x()
        parms["ty"] = position.y()
        parms["tz"] = position.z()

        #self.handle.update()

    def sync_with_control(self, parms, control):
        # type: (dict, PointControl) -> None

        for mapping in self.attrib_mapping:
            if mapping == "@P":
                continue
            value_map = self.attrib_mapping[mapping]
            if isinstance(value_map, Iterable):
                control_attribute = control.attributes[mapping]
                for i, p in enumerate(value_map):
                    parms[p] = control_attribute[i]
            else:
                parms[value_map] = control.attributes[mapping]

        self.move_to(parms, control.position)

    def apply_mapping(self, parms: dict, control: PointControl):

        if self.attrib_mapping is None:
            self.on_update(parms, None, None)
            return
        for mapping in self.attrib_mapping:
            value_map = self.attrib_mapping[mapping]
            if isinstance(value_map, Iterable):
                value = tuple(parms[v] for v in value_map)
            else:
                value = parms[value_map]
            
            if mapping != "@P":
                self.old_values[mapping] = control.attributes[mapping]
                self.new_values[mapping] = value
                control.set_attribute_value(mapping, value)
            else:
                self.old_values[mapping] = control.position
                self.new_values[mapping] = value
                old_position = control.position
                new_position = hou.Vector3(value)
                control.move_to(new_position)
                self.state.point_controls.plane_point = new_position
                self.state.on_control_moved(control, new_position, old_position)

        self.on_update(parms, self.new_values, self.old_values)

class PointGadget(object):
    def __init__(self, gadget, name, geo, params, dragger):
        self.gadget = gadget # type: hou.GadgetDrawable
        self.gadget.setGeometry(geo)
        self.gadget.setParams(params)
        self.dragger = dragger # can't create it?

        self.on_start_drag = lambda gadget, ui_event: None
        self.on_drag = lambda gadget, ui_event: None
        self.on_end_drag = lambda gadget, ui_event: None

        self.enabled = True

    def on_mouse_event(self, ui_event):
        # type: (hou.UIEvent) -> None
        if not self.enabled:
            return

        reason = ui_event.reason()

        if reason == hou.uiEventReason.Start:
            self.on_start_drag(self, ui_event)

        elif reason in [hou.uiEventReason.Active, hou.uiEventReason.Changed]:
            self.on_drag(self, ui_event)

    def set_params(self, params):
        self.gadget.setParams(params)

class StateParm:

    def __init__(self) -> None:
        self.name: str = ""
        self.value = None
        self.default_value = None
        self.on_changed_name: str = ""
        self.node_parm_name: str = ""
        self.node_parm: hou.Parm = None
        self.on_changed = lambda value: None


    def read(self):
        if self.node_parm is not None:
            self.value = self.node_parm.evalAsInt()

    def set(self, value):
        self.on_changed(value)
        self.value = value
        if self.node_parm is not None:
            self.node_parm.set(value)

class MenuAction:

    class Context:
        ALWAYS = 0
        ONE_CONTROL_SELECTED = 1
        MULTIPLE_CONTROL_SELECTED = 2
        STATE_PARM = 3
    
    def __init__(self, name: str, callback: str, menu_context: MenuAction.Context) -> None:
        self.name: str = name
        self.callback = None
        self.callback_name = callback
        self.menu_context: MenuAction.Context = menu_context
        self.state_parm: StateParm = None

class BoxSelection:

    class Mode:
        NEW_SELECTION = 1
        ADD_TO_SELECTION = 2
        SUBTRACT_FROM_SELECTION = 3

    MODE_PARAMS = {
        Mode.NEW_SELECTION: { "color1": (0.9,0.9,0.9,1.0) },
        Mode.ADD_TO_SELECTION: { "color1": (0.3,0.9,0.0,1.0) },
        Mode.SUBTRACT_FROM_SELECTION: { "color1": (0.9,0.3,0.0,1.0) },
    }

    def __init__(self, scene_viewer: hou.SceneViewer, state: PointControlsState) -> None:
        self.scene_viewer = scene_viewer
        self.state = state
        selection_drawable_params = {
            "color1": (0.3,0.9,0.6,1.0),
            "line_width": 1.0,
            "glow_width": 0.0,
            "fade_factor": 1.0,
        }
        self.mode = BoxSelection.Mode.NEW_SELECTION
        self.selection_start: hou.Vector3 = None
        self.selection_end: hou.Vector3 = None
        self.selection_viewport: hou.GeometryViewport = None
        self._drawable = hou.GeometryDrawable(scene_viewer, hou.drawableGeometryType.Line, f"{state.state_label}_selection_drawable") # type: hou.GeometryDrawable
        self._drawable.setParams(selection_drawable_params)
        self._drawable.show(True)
        self.in_progress = False

    def set_mode(self, mode: BoxSelection.Mode):
        self.mode = mode
        self._drawable.setParams(BoxSelection.MODE_PARAMS[mode])

    
    def start_selection(self, mode: BoxSelection.Mode, viewport: hou.GeometryViewport, start_position: hou.Vector3):
        self.state.log("Start selection")
        self.set_mode(mode)
        self.selection_start = start_position
        self.selection_viewport = viewport
        self.in_progress = True

    def build_geo(self, mouse_pos):

        self.selection_end = mouse_pos

        geo: hou.Geometry = hou.Geometry()

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

        self._drawable.setGeometry(geo)

    def check_point(self, point: hou.Vector3) -> bool:
        viewport: hou.GeometryViewport = self.selection_viewport
        screen_pos: hou.Vector2 = viewport.mapToScreen(point * viewport.modelToGeometryTransform().inverted())

        start_x = self.selection_start.x()
        start_y = self.selection_start.y()

        end_x = self.selection_end.x()
        end_y = self.selection_end.y()

        left = min(start_x, end_x)
        right = left + abs(start_x - end_x)

        bottom = min(start_y, end_y)
        top = bottom + abs(start_y - end_y)

        return left <= screen_pos.x() <= right and bottom <= screen_pos.y() <= top


    def draw(self, handle):
        self._drawable.draw(handle)  


POINT_CONTROL_HANDLE = "__pc_xform_handle"
BOX_TRANSFORM_HANDLE = "__pc_box_transform_handle"

# TODO: Add dictionary support 
# Generic point control state with geo storage
class PointControlsState(object):

    def __init__(self, state_name, scene_viewer):

        self.moving_type = MovingType.FREE_DRAG
        self.state_name = state_name
        self.scene_viewer: hou.SceneViewer = scene_viewer
        self.state_label = state_name

        self.point_controls: PointControlGroup = PointControlGroup(scene_viewer)
        self.point_controls.add_drawable("controls")
        self.point_controls.set_drawing_params("controls", def_pcontrol_params)
        self.point_controls.set_hovered_params("controls", def_pcontrol_hover_params)
        self.point_controls.set_selected_params("controls", def_pcontrol_selected_params)
        
        # setup callbacks
        self.point_controls.on_control_moved = self.on_control_moved
        self.point_controls.on_control_end_move = self.on_control_end_move
        self.point_controls.on_control_start_move = self.on_control_start_move
        
        self.node = None # type: hou.SopNode

        self.attributes_meta: dict[str, AttributeMeta] = {}
        self.point_handles: dict[str, PointHandle] = {}
        self.point_gadgets: dict[str, PointGadget] = {}

        self.point_stash_name = "points_stash"
        self.points_stash = None # type: hou.Parm
        self.points_geo = None # type: hou.Geometry

        self.point_controls.on_hover_update = self.on_control_hovered
        self.dragger = hou.ViewerStateDragger("dragger")
        self.dragging_gadget = None # type: PointGadget

        self.located_gadget = None # type: PointGadget

        self.menu_actions: dict[str, MenuAction] = {}
        self.state_parms: dict[str, StateParm] = {}

        self.disable_state_parms_callback = False

        self.initial_selection: list[PointControl] = []
        self.box_selection: BoxSelection = BoxSelection(scene_viewer, self)

        self.box_transform_bounds = None
        self.box_transform_size = None
        self.reset_box_transform_handle = False
        self.box_transform_positions: list[hou.Vector3] = []

        self.edit_transaction = False
        self.is_editing_by_handle = False

        self.allow_multiselection = True
        self.allow_box_selection = True
        self.allow_mass_moving = True
        self.allow_box_transform = True

        self.clicked_on_control = False
        self.clicked_on_selected_control = False
        self.selected_control_moved = False

        self.need_update_handle = False
        self.handle_cycle_keys = hou.hotkeys.assignments("h.pane.gview.handle.cycle_mode")
        self.handle_cycle_keys = [s.lower() for s in self.handle_cycle_keys]

        self.add_point_attribute("rotation", (0.0, 0.0, 0.0))
        self.add_point_attribute("scale", (1.0, 1.0, 1.0))

        self.add_point_handle(
            POINT_CONTROL_HANDLE, 
            attrib_mapping={
                "scale":("sx", "sy", "sz"), 
                "rotation":("rx", "ry", "rz"),
                "@P":("tx", "ty", "tz")}, 
        )
        self.xform_handle_enable = True

        self.box_transform_handle = hou.Handle(self.scene_viewer, BOX_TRANSFORM_HANDLE)

    def begin_edit(self):
        self.log("Start edit transaction")
        self.edit_transaction = True
        self.scene_viewer.beginStateUndo(f"{self.state_label}: Modify controls")

    def end_edit(self):
        self.log("End edit transaction")
        self.edit_transaction = False
        self.scene_viewer.endStateUndo()

    def add_point_handle(self, handle_name, attrib_mapping, disabled_parms=[], on_update=lambda parms, new_values, old_values: None):
        handle = hou.Handle(self.scene_viewer, handle_name)
        self.point_handles[handle_name] = PointHandle(handle_name, attrib_mapping, handle, disabled_parms, on_update)
        self.point_handles[handle_name].state = self

    def enable_xfrom_handle(self, enable: bool):
        self.xform_handle_enable = enable

        if not enable:
            self.show_handle(POINT_CONTROL_HANDLE, False)

        if enable and self.point_controls.selected_controls:
            self.show_handle(POINT_CONTROL_HANDLE, True)

    def calculate_box_transform_bounds(self):
        selected_controls = self.point_controls.selected_controls

        if len(selected_controls) < 2:
            self.box_transform_bounds = None
            return

        selected_positions = [control.position for control in selected_controls]

        max_pos = hou.Vector3(np.max(selected_positions, axis=0))
        min_pos = hou.Vector3(np.min(selected_positions, axis=0))

        origin = (min_pos + max_pos) * 0.5
        size = (max_pos - origin) * 2.0

        self.box_transform_bounds = (origin, size)
        self.box_transform_size = size

        self.box_transform_positions = [position - origin for position in selected_positions]
        self.reset_box_transform_handle = True

    def process_box_selection(self):
        # type(hou.UIEventDevice) -> bool

        points_in_pox = [point for point in self.point_controls.point_controls if self.box_selection.check_point(point.position)]

        self.point_controls.clear_selection()
       
        if self.box_selection.mode == BoxSelection.Mode.NEW_SELECTION:
            selected_points = points_in_pox
        elif self.box_selection.mode == BoxSelection.Mode.ADD_TO_SELECTION:
            selected_points = set(self.initial_selection + points_in_pox)
        else:
            selected_points = set(self.initial_selection) - set(points_in_pox)

        self.point_controls.select_controls(selected_points)
        self.on_control_selected()

    

    def add_point_gadget(self, gadget_name, geo, params, on_start_drag=lambda gadget, ui_event: None, on_end_drag=lambda gadget, ui_event: None, on_drag=lambda gadget, ui_event: None):
        gadget_instance = self.state_gadgets[gadget_name]
        gadget = PointGadget(gadget_instance, gadget_name, geo, params, self.dragger)
        gadget.on_drag = on_drag
        gadget.on_end_drag = on_end_drag
        gadget.on_start_drag = on_start_drag
        self.point_gadgets[gadget_name] = gadget

    def add_point_attribute(self, name, default_value, control_parm=None, allow_multiedit=False):
        self.attributes_meta[name] = AttributeMeta(name, default_value, control_parm, allow_multiedit)

    def sync_parms_with_selection(self, control):
        self.log("Sync parm pane with selection")
        if control is None:
            return

        with hou.undos.disabler():
            #with hou.undos.disabler():
            for attrib_name in self.attributes_meta:
                if self.attributes_meta[attrib_name].control_parm is None:
                    continue

                if self.attributes_meta[attrib_name].size < 2:
                    parm = self.node.parm(self.attributes_meta[attrib_name].control_parm) # type: hou.Parm
                else:
                    parm = self.node.parmTuple(self.attributes_meta[attrib_name].control_parm) # type: hou.Parm

                self.disable_state_parms_callback = True
                parm.set(control.attributes[attrib_name])
                self.disable_state_parms_callback = False


    def onMenuAction(self, kwargs):
        """ Callback implementing the actions of a bound menu. Called 
        when a menu item has been selected. 
        """
        menu_item: str = kwargs["menu_item"]
        
        
        num_selected = len(self.point_controls.selected_controls)
        one_control_selected = num_selected == 1

        if menu_item in self.menu_actions:
            menu_action = self.menu_actions[menu_item]

            if menu_action.menu_context == MenuAction.Context.ALWAYS:
                menu_action.callback(kwargs)
            elif menu_action.menu_context == MenuAction.Context.ONE_CONTROL_SELECTED and one_control_selected:
                menu_action.callback(kwargs)
            elif menu_action.menu_context == MenuAction.Context.MULTIPLE_CONTROL_SELECTED and num_selected:
                menu_action.callback(kwargs)
            elif menu_action.menu_context == MenuAction.Context.STATE_PARM:
                value = kwargs[menu_item]
                menu_action.state_parm.set(value)

    def setup_state_parms(self):
        for state_parm in self.state_parms:
            if self.state_parms[state_parm].node_parm_name:
                node_parm: hou.Parm = self.node.parm(self.state_parms[state_parm].node_parm_name)
            else:
                node_parm = None
            self.state_parms[state_parm].node_parm = node_parm

            if node_parm is not None:
                self.state_parms[state_parm].set(node_parm.eval())
    
    def setup_node_callbacks(self):
        watched_parms = [self.attributes_meta[a].control_parm for a in self.attributes_meta if self.attributes_meta[a].control_parm is not None]
        watched_parms += [self.state_parms[s].node_parm_name for s in self.state_parms]
        watched_parms += [self.point_stash_name]
        self.node.addParmCallback(self.on_control_parm_changed, watched_parms)
    
    def on_control_parm_changed(self, **kwargs):
        if self.disable_state_parms_callback:
            return
        parm_tuple = kwargs["parm_tuple"] # type: hou.ParmTuple

        if parm_tuple is None:
            return

        parm_name = parm_tuple.name()
        if parm_name == self.point_stash_name and not self.edit_transaction:
            self.load_from_stash()
            self.log("Load from stash")
            return

        attrib = next((a for a in self.attributes_meta if self.attributes_meta[a].control_parm == parm_name), None)
        
        if attrib is not None and self.point_controls.selected_controls:
            # is it attrib control parm

            if len(self.point_controls.selected_controls) > 1 and not self.attributes_meta[attrib].allow_multiedit:
                return

            value = parm_tuple.eval()
            value = value if len(value) > 1 else value[0]
           
            self.begin_edit()
            for control in self.point_controls.selected_controls:
                control.set_attribute_value(attrib, value)
            self.on_update()
            self.end_edit()
        
        else: 
            # or state parm control

            state_parm = next((p for p in self.state_parms if self.state_parms[p].node_parm_name == parm_name), None)

            if state_parm is None:
                return

            value = parm_tuple.eval()
            value = value if len(value) > 1 else value[0]

            # NOTE: Avoid recursion (any other better way?)
            self.disable_state_parms_callback = True
            self.state_parms[state_parm].set(value)
            self.disable_state_parms_callback = False

    def log_traceback(self):
        self.log("".join(traceback.format_stack()))

    def show_all_gadgets(self, show):
        for gadget in self.point_gadgets:
            self.point_gadgets[gadget].gadget.show(show)

    def show_all_handles(self, show):
        for handle in self.point_handles:
            self.point_handles[handle].handle.show(show and self.point_handles[handle].enabled)

    def update_all_handles(self):
        for handle in self.point_handles:
            self.point_handles[handle].handle.update()

    def show_handle(self, handle_name, show, hide_others=False):
        if hide_others:
            self.show_all_handles(False)
        self.point_handles[handle_name].handle.show(show and self.point_handles[handle_name].enabled)

    def enable_all_handles(self, enable):
        for handle in self.point_handles:
            self.point_handles[handle].enabled = enable

    def move_control(self, control, position):
        # type: (PointControl, hou.Vector3) -> None

        control.move_to(position)
        self.point_controls.update_points_geo()
        self.point_controls.update_hovered_geo()
        self.point_controls.update_selected_geo()

    def on_control_hovered(self, hovered_control, prev_control):
        # type: (PointControl, PointControl) -> None
        if self.moving_type == MovingType.FREE_DRAG:
            if hovered_control is None and prev_control is not None:
                self.show_handle(POINT_CONTROL_HANDLE, True)
            if hovered_control is not None and prev_control is None:
                self.show_handle(POINT_CONTROL_HANDLE, False)

    def toggle_handles_visibility(self):
        if self.allow_mass_moving and self.allow_box_transform and len(self.point_controls.selected_controls) > 1:
            self.box_transform_handle.show(True)
            self.calculate_box_transform_bounds()
            self.box_transform_handle.update()
        else:
            self.box_transform_handle.show(False)

        if len(self.point_controls.selected_controls) == 1:
            self.enable_all_handles(True)
            if self.point_controls.hovered_control is None:
                self.show_all_handles(True)
        else:
            self.enable_all_handles(False)
            self.show_all_handles(False)

    def on_control_selected(self, control=None):
        # type: (PointControl) -> None
        if control is not None:
            self.sync_parms_with_selection(control)

        self.toggle_handles_visibility()
        

    def on_control_start_move(self, control):
        self.selected_control_moved = True
        self.show_all_handles(False)
        self.begin_edit()
        self.log("Start moving control")

    def on_control_end_move(self, control):
        self.end_edit()
        self.log("End moving control")

    def on_control_moved(self, control, new_position, old_position):
        if len(self.point_controls.selected_controls) > 1 and self.allow_mass_moving:
            diff = new_position - old_position
            for selected_control in self.point_controls.selected_controls:
                if selected_control is not control:
                    selected_control.move_to(selected_control.position + diff)
    
    def update_all_controls_geo(self):
        self.point_controls.update_points_geo()
        self.point_controls.update_hovered_geo()
        self.point_controls.update_selected_geo()

    def delete_selected_controls(self) -> bool:
        if not self.point_controls.selected_controls:
            return False

        if self.point_controls.hovered_control in self.point_controls.selected_controls:
            self.point_controls.hovered_control = None

        for control in self.point_controls.selected_controls:
            self.point_controls.point_controls.remove(control)

        self.begin_edit()
        self.rebuild_points_geo()
        self.on_update()
        self.end_edit()

        self.point_controls.clear_selection()
        self.update_all_controls_geo()
        self.on_control_selected()

        return True


    def add_control(self, position: hou.Vector3, drawable_index=0, tag="", rebuild_geo=True, select=True):
        control = self.point_controls.add_control(position, drawable_index, tag)
        for attr in self.attributes_meta:
            control.attributes[attr] = self.attributes_meta[attr].default_value

        if select:
            self.point_controls.select_control(control)

        self.update_all_controls_geo()

        if rebuild_geo:
            self.begin_edit()
            self.rebuild_points_geo()
            self.on_update()
            self.end_edit()

        return control
    
    def get_one_selected_control(self):
        # type: () -> PointControl
        selected_controls = self.point_controls.selected_controls
        return selected_controls[0] if len(selected_controls) == 1 else None

    def rebuild_points_geo(self):

        self.points_geo = hou.Geometry()
        self.points_geo.createPoints([p.position for p in self.point_controls.point_controls])

        geo_attribs = []

        for attrib in self.attributes_meta:
            geo_attribs.append(self.points_geo.addAttrib(hou.attribType.Point, attrib, self.attributes_meta[attrib].default_value))

        for point in self.points_geo.points(): # type: hou.Point
            control = self.point_controls.point_controls[point.number()]
            control.geo_point = point
            for attrib in geo_attribs: # type: hou.Attrib
                point.setAttribValue(attrib, control.attributes[attrib.name()])

    def load_from_stash(self):
        self.log("Load controls from stash")
        self.log_traceback()

        self.point_controls.clear_controls()

        geo = self.points_stash.evalAsGeometry() # type: hou.Geometry
        if geo is None:
            self.rebuild_points_geo()
            return

        geo_points = geo.points()

        point_attribs = geo.pointAttribs() # type: list[hou.Attrib]

        point_attribs = [attrib for attrib in point_attribs 
                        if attrib.name() in self.attributes_meta and self.attributes_meta[attrib.name()].is_same_type(attrib)]


        #NOTE: In the future can be optimized with pointFloatAttribValues(name), currently not worth it
        for point in geo_points: # type: hou.Point
            control = self.add_control(point.position(), rebuild_geo=False, select=False)
            for attrib in point_attribs:
                control.attributes[attrib.name()] = point.attribValue(attrib)

        self.rebuild_points_geo()

        self.on_control_selected()

        self.point_controls.update_points_geo()

    def on_update(self):
        self.points_stash.set(self.points_geo)
        self.points_geo.incrementAllDataIds()

    def on_mouse_move(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.point_controls.on_mouse_move(ui_event)
        if self.point_controls.dragging:
            self.on_update()
        if self.box_selection.in_progress:
            device: hou.UIEventDevice = ui_event.device()
            mouse_pos = hou.Vector3(device.mouseX(), device.mouseY(), 0.0)
            self.box_selection.build_geo(mouse_pos)
            self.process_box_selection()

    def on_mouse_up(self, ui_event):
        # type: (hou.UIEvent) -> None
        self.point_controls.on_mouse_up(ui_event)

        if self.clicked_on_selected_control and not self.selected_control_moved:
            self.point_controls.select_control(self.point_controls.dragged_control)
            self.on_control_selected()

        if self.box_selection.in_progress:
            self.box_selection.in_progress = False


    def on_mouse_down(self, ui_event):
        # type: (hou.UIEvent) -> None

        device: hou.UIEventDevice = ui_event.device()

        self.clicked_on_control = False
        self.selected_control_moved = False
        self.clicked_on_selected_control = False

        self.point_controls.on_mouse_down(ui_event)
        selected_control = self.point_controls.select_point()

        is_shift_key = device.isShiftKey()
        is_ctrl_key = device.isCtrlKey()

        if selected_control is not None:
            self.clicked_on_control = True
            self.point_controls.dragged_control = selected_control
            if is_shift_key and self.allow_multiselection:
                self.disable_dragging()
                if selected_control in self.point_controls.selected_controls:
                    self.point_controls.unselect_control(selected_control)
                else:
                    self.point_controls.add_control_to_selection(selected_control)
            elif selected_control not in self.point_controls.selected_controls:    
                if self.moving_type == MovingType.HANDLES_ONLY:
                    self.disable_dragging()
                self.point_controls.select_control(selected_control)
            else:
                self.clicked_on_selected_control = True
            self.point_controls.plane_point = selected_control.position
            self.on_control_selected(selected_control)
            self.update_all_handles()
        else:

            self.clicked_on_control = False

            viewport = self.scene_viewer.curViewport()
            mouse_pos = hou.Vector3(device.mouseX(), device.mouseY(), 0.0)
            mouse_pos *= viewport.windowToViewportTransform()

            if self.allow_multiselection and (is_shift_key or is_ctrl_key) and self.allow_box_selection:
                self.disable_dragging()
                self.initial_selection = list(self.point_controls.selected_controls)

                if is_shift_key and is_ctrl_key:
                    self.box_selection.start_selection(BoxSelection.Mode.NEW_SELECTION, viewport, mouse_pos)
                    self.initial_selection = []
                elif is_shift_key:
                    self.box_selection.start_selection(BoxSelection.Mode.ADD_TO_SELECTION, viewport, mouse_pos)
                elif is_ctrl_key:
                    self.box_selection.start_selection(BoxSelection.Mode.SUBTRACT_FROM_SELECTION, viewport, mouse_pos)
            else:
                self.point_controls.clear_selection()

    def disable_dragging(self):
        self.point_controls.dragging = False
        self.point_controls.drag_start = False

    def enable_dragging(self):
        self.point_controls.dragging = True
        self.point_controls.drag_start = True

    def show(self, visible):
        self.point_controls.show(visible)

    def onResume(self, kwargs):
        self.show(True)

    def onStateToHandle(self, kwargs):
        handle = kwargs["handle"]
        parms = kwargs["parms"]

        selected_control = self.get_one_selected_control()
        if selected_control is not None:
            if handle in self.point_handles:
                self.point_handles[handle].sync_with_control(parms, selected_control)

            #self.on_update()

        if (handle == BOX_TRANSFORM_HANDLE and self.reset_box_transform_handle 
            and self.box_transform_bounds is not None and len(self.point_controls.selected_controls) > 1):

            parms["centerx"] = self.box_transform_bounds[0].x()
            parms["centery"] = self.box_transform_bounds[0].y()
            parms["centerz"] = self.box_transform_bounds[0].z()

            parms["sizex"] = self.box_transform_bounds[1].x() 
            parms["sizey"] = self.box_transform_bounds[1].y()
            parms["sizez"] = self.box_transform_bounds[1].z() 

            parms["rx"] = parms["ry"] = parms["rz"] = 0.0

            self.reset_box_transform_handle = False

    def process_box_transform(self, parms):
        rx, ry, rz = parms["rx"], parms["ry"], parms["rz"]
        tx, ty, tz = parms["centerx"], parms["centery"], parms["centerz"]
        box_center = hou.Vector3((tx, ty, tz))
        sizex, sizey, sizez = parms["sizex"], parms["sizey"], parms["sizez"]
        
        size_tolerance = 0.000001

        selection_size = self.box_transform_size

        sx = 1.0 if abs(selection_size.x()) < size_tolerance else sizex / selection_size.x()
        sy = 1.0 if abs(selection_size.y()) < size_tolerance else sizey / selection_size.y()
        sz = 1.0 if abs(selection_size.z()) < size_tolerance else sizez / selection_size.z()

        transform = hou.hmath.identityTransform()
        transform *= hou.hmath.buildScale(sx, sy, sz)
        transform *= hou.hmath.buildRotate(rx, ry, rz)

        for index, control in enumerate(self.point_controls.selected_controls):
            control.move_to(box_center + self.box_transform_positions[index] * transform)

    def onBeginHandleToState(self, kwargs):
        self.is_editing_by_handle = True
        self.begin_edit()
        
    def onEndHandleToState(self, kwargs):
        self.is_editing_by_handle = False
        self.end_edit()


    def onHandleToState(self, kwargs):
        handle = kwargs["handle"]
        parms = kwargs["parms"]

        selected_control = self.get_one_selected_control()
        if selected_control is not None:
            if handle in self.point_handles:
                self.point_handles[handle].apply_mapping(parms, selected_control)

        if handle == BOX_TRANSFORM_HANDLE and len(self.point_controls.selected_controls) > 1:
            self.process_box_transform(parms)

        self.update_all_controls_geo() 
        self.on_update()

    def on_enter(self, kwargs):
        pass

    def on_exit(self, kwargs):
        pass

    def on_gadget_located(self, gadget, enter):
        pass


    def onEnter(self, kwargs):
        self.log("== ENTER ==")
        self.node = kwargs["node"]
        if self.point_stash_name:
            self.points_stash = self.node.parm(self.point_stash_name)
        for handle in self.point_handles.values():
            if handle.disabled_parms:
                handle.handle.disableParms(handle.disabled_parms)

        self.show(True)
        self.load_from_stash()

        self.setup_state_parms()
        self.setup_node_callbacks()

        self.on_enter(kwargs)

    def onExit(self, kwargs):
        self.node.removeAllEventCallbacks()
        self.on_exit(kwargs)
        self.log("== EXIT ==")        

    def onKeyEvent(self, kwargs):
        ui_event: hou.UIEvent = kwargs["ui_event"] 
        device: hou.UIEventDevice = ui_event.device()

        key = device.keyString()

        if any(True for k in self.handle_cycle_keys if k in key):
            self.need_update_handle = True
            return False

        if "Del" in key:
            return self.delete_selected_controls()

        
    
    def onMouseEvent(self, kwargs):

        ui_event = kwargs["ui_event"] # type: hou.UIEvent

        device = ui_event.device() # type: hou.UIEventDevice
        reason = ui_event.reason() # type: hou.UIEventReason

        gadget_name = self.state_context.gadget()

        if gadget_name in self.point_gadgets and self.point_gadgets[gadget_name].enabled:
            self.point_gadgets[gadget_name].on_mouse_event(ui_event)
            if reason == hou.uiEventReason.Start:
                self.log(f"EventStart for Gadget {gadget_name}")
                self.dragging_gadget = self.point_gadgets[gadget_name]
            if reason == hou.uiEventReason.Located and self.located_gadget is None:
                self.located_gadget = self.point_gadgets[gadget_name]
                self.on_gadget_located(self.located_gadget, True)
            if reason == hou.uiEventReason.Changed and self.dragging_gadget is not None:
                self.dragging_gadget.on_end_drag(self.dragging_gadget, ui_event)
                self.dragging_gadget = None

            return True

        left_button = device.isLeftButton()

        if reason == hou.uiEventReason.Active or reason == hou.uiEventReason.Located:
            self.on_mouse_move(ui_event)

            if self.located_gadget is not None:
                self.on_gadget_located(self.located_gadget, False)
                self.located_gadget = None
            
            if self.point_controls.enable_snapping:
                snapping_ray = ui_event.snappingRay()

        if reason == hou.uiEventReason.Picked and left_button:
            self.on_mouse_down(ui_event)
            self.on_mouse_up(ui_event)

        if reason == hou.uiEventReason.Changed:
            self.on_mouse_up(ui_event)
            if self.dragging_gadget is not None and self.dragging_gadget.enabled:
                self.dragging_gadget.on_end_drag(self.dragging_gadget, ui_event)
                self.dragging_gadget = None

        if reason == hou.uiEventReason.Start and left_button:
            self.on_mouse_down(ui_event)
            #self.on_mouse_move(ui_event)


    def on_draw(self, handle):
        pass

    def onDraw(self, kwargs ):
        """ This callback is used for rendering the drawables
        """
        handle = kwargs["draw_handle"]
        for gadget in self.point_gadgets:
            self.point_gadgets[gadget].gadget.draw(handle)
        
        self.point_controls.draw(handle)
        
        if self.box_selection.in_progress:
            self.box_selection.draw(handle)
        
        if self.need_update_handle:
            self.need_update_handle = False
            self.toggle_handles_visibility()

        self.on_draw(handle)

    def onDrawInterrupt(self, kwargs ):
        handle = kwargs["draw_handle"]
        self.point_controls.draw(handle) 

class PointControlsStateMenu(hou.ViewerStateMenu):
    def __init__(self, template: PointControlsStateTemplate, label: str):
        super().__init__(f"{template.typeName()}_menu", label)
        self.template: PointControlsStateTemplate = template

    def addToggleItem(self, menu_id, label, default, hotkey='', callback="", state_parm="", context=MenuAction.Context.ALWAYS) -> None:

        menu_action = MenuAction(menu_id, callback, context)
        parm = next((p for p in self.template.factory.state_parms if p.name == state_parm), None)
        if parm is not None:
            menu_action.state_parm = parm
            menu_action.menu_context = MenuAction.Context.STATE_PARM

        self.template.factory.menu_actions.append(menu_action)

        hk = hotkey
        if hotkey:
            hk = su.hotkey(self.template.typeName(), menu_id, hotkey, label)        
        return super().addToggleItem(menu_id, label, default, hotkey=hk)

    def addActionItem(self, menu_id, label, hotkey='') -> None:
        hk = hotkey
        if hotkey:
            hk = su.hotkey(self.template.typeName(), menu_id, hotkey, label)        
        return super().addActionItem(menu_id, label, hotkey=hk)

    def addRadioStripItem(self, strip_id, menu_id, label, hotkey='') -> None:
        hk = hotkey
        if hotkey:
            hk = su.hotkey(self.template.typeName(), menu_id, hotkey, label)        
        return super().addRadioStripItem(self, strip_id, menu_id, label, hotkey=hk)

class PointControlsStateFactory:

    def __init__(self, state_class, state_typename):
        self.state_class = state_class
        self.state_parms: list[StateParm] = [] 
        self.menu_actions: list[MenuAction] = []
        self.state_typename = state_typename
        self.state_methods = {}

    def add_state_parm( self, name: str,
                        default_value = None, 
                        control_parm: str="", 
                        on_changed: str=""):

        state_parm = StateParm()
        state_parm.name = name
        state_parm.node_parm_name = control_parm
        state_parm.default_value = default_value
        state_parm.on_changed_name = on_changed

        self.state_parms.append(state_parm)

    def _bind_state_parms(self, state_instance: PointControlsState):
        for state_parm in self.state_parms:
            state_instance.state_parms[state_parm.name] = state_parm
            if state_parm.on_changed_name in self.state_methods:
                state_parm.on_changed = self.state_methods[state_parm.on_changed_name]

    def _bind_menu_actions(self, state_instance: PointControlsState):
        for menu_action in self.menu_actions:
            state_instance.menu_actions[menu_action.name] = menu_action
            if menu_action.callback_name in self.state_methods:
                menu_action.callback = self.state_methods[menu_action.callback_name]

    def __call__(self, state_name, scene_viewer):
        state_instance = self.state_class(state_name, scene_viewer)
        state_methods = inspect.getmembers(state_instance, inspect.ismethod)
        self.state_methods = {name: method for (name, method) in state_methods}
        self._bind_state_parms(state_instance)
        self._bind_menu_actions(state_instance)
        return state_instance

class PointControlsStateTemplate(hou.ViewerStateTemplate):
    def __init__(self, state_class, state_name, state_label, contexts=[]):
        super().__init__(state_name, state_label, hou.sopNodeTypeCategory(), contexts)
        self.factory = PointControlsStateFactory(state_class, state_name)
        self.bindFactory(self.factory)
        self.bindHandle("xform", POINT_CONTROL_HANDLE)
        self.bindHandle("boundingbox", BOX_TRANSFORM_HANDLE)

    def addStateParm( self, name: str,
                        default_value = None, 
                        control_parm: str="", 
                        on_changed: str=""):
        self.factory.add_state_parm(name, default_value, control_parm, on_changed)
