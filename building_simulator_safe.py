#!/usr/bin/env python3
"""
building_simulator_safe.py — Building Simulator with error prevention.

Features:
- Windows flush against walls (rotated to face outward)
- Multiple building types: skyscraper, high-rise apartment, low-rise apartment
- Multiple roof types: flat, gabled, pointed, terrace
- Flag validation to prevent "Invalid flag" errors
- Input validation for all slider values
"""

import maya.cmds as cmds
import functools


# ---------------------------------------------------------------------------
# Building type definitions
# ---------------------------------------------------------------------------

BUILDING_TYPES = {
    "skyscraper": {
        "label": "Skyscraper",
        "min_floors": 20,
        "max_floors": 100,
        "default_floors": 40,
        "floor_height": 3.5,
        "width_range": (3.0, 6.0),
        "depth_range": (3.0, 6.0),
        "windows_per_floor_range": (4, 8),
        "default_windows": 6,
        "window_size_range": (0.5, 1.2),
        "default_window_size": 0.8,
        "roof_types": ["flat", "pointed", "terrace"],
        "default_roof": "pointed",
        "has_door": False,
        "description": "Tall commercial tower with modern glass facade",
    },
    "high_rise_apartment": {
        "label": "High-Rise Apartment",
        "min_floors": 10,
        "max_floors": 40,
        "default_floors": 20,
        "floor_height": 3.0,
        "width_range": (6.0, 12.0),
        "depth_range": (6.0, 12.0),
        "windows_per_floor_range": (3, 6),
        "default_windows": 4,
        "window_size_range": (0.6, 1.4),
        "default_window_size": 1.0,
        "roof_types": ["flat", "gabled", "terrace"],
        "default_roof": "flat",
        "has_door": False,
        "description": "Residential tower with balconies and regular windows",
    },
    "low_rise_apartment": {
        "label": "Low-Rise Apartment",
        "min_floors": 2,
        "max_floors": 8,
        "default_floors": 4,
        "floor_height": 3.0,
        "width_range": (8.0, 16.0),
        "depth_range": (8.0, 16.0),
        "windows_per_floor_range": (2, 5),
        "default_windows": 3,
        "window_size_range": (0.8, 1.8),
        "default_window_size": 1.2,
        "roof_types": ["gabled", "flat", "terrace"],
        "default_roof": "gabled",
        "has_door": True,
        "description": "Small residential building with pitched roof",
    },
}

ROOF_TYPES = {
    "flat": {"label": "Flat Roof", "description": "Modern flat roof with slight overhang"},
    "gabled": {"label": "Gabled Roof", "description": "Classic triangular pitched roof"},
    "pointed": {"label": "Pointed Roof", "description": "Sharp spire-like roof for towers"},
    "terrace": {"label": "Terrace Roof", "description": "Flat roof with raised edge parapet"},
}


# ---------------------------------------------------------------------------
# Flag validation system
# ---------------------------------------------------------------------------

KNOWN_FLAGS = {
    "polyCube": {"width", "height", "depth", "name", "axis", "cuv", "ch"},
    "polyPlane": {"width", "height", "name", "axis", "cuv", "ch", "sx", "sy"},
    "polyPrism": {"length", "width", "height", "name", "subdivisions", "axis", "cuv", "ch"},
    "polyCylinder": {"radius", "height", "name", "axis", "subdivisionsX", "subdivisionsY", "subdivisionsCap", "cuv", "ch"},
    "polyCone": {"radius", "height", "name", "axis", "subdivisionsX", "subdivisionsCap", "cuv", "ch"},
    "move": {"x", "y", "z", "absolute", "relative", "worldSpace", "objectSpace"},
    "rotate": {"x", "y", "z", "absolute", "relative", "worldSpace", "objectSpace"},
    "scale": {"x", "y", "z", "absolute", "relative", "worldSpace", "objectSpace"},
    "group": {"name", "parent", "relative", "absolute"},
    "window": {"title", "widthHeight", "sizeable", "minimizeButton", "maximizeButton", "menuBar", "toolbox", "titleBar", "resizeToFitChildren"},
    "columnLayout": {"adjustableColumn", "rowSpacing", "columnAttach", "columnWidth", "columnAlign", "parent", "childArray", "numberOfChildren", "exists", "visible", "enable", "width", "height", "backgroundColor"},
    "rowColumnLayout": {"numberOfColumns", "columnWidth", "columnAlign", "columnAttach", "rowSpacing", "parent", "childArray", "numberOfChildren", "exists", "visible", "enable", "width", "height", "backgroundColor"},
    "intSliderGrp": {"field", "label", "minValue", "maxValue", "value", "fieldMinValue", "fieldMaxValue", "columnWidth", "columnAlign", "parent", "changeCommand", "dragCommand", "fieldStep", "sliderStep", "exists", "visible", "enable", "width", "height", "backgroundColor", "annotation", "noBackground"},
    "floatSliderGrp": {"field", "label", "minValue", "maxValue", "value", "fieldMinValue", "fieldMaxValue", "columnWidth", "columnAlign", "parent", "changeCommand", "dragCommand", "fieldStep", "sliderStep", "exists", "visible", "enable", "width", "height", "backgroundColor", "annotation", "noBackground"},
    "optionMenu": {"label", "parent", "changeCommand", "exists", "visible", "enable", "width", "height", "backgroundColor", "annotation", "noBackground", "alwaysCallChangeCommand"},
    "button": {"label", "height", "command", "backgroundColor", "parent", "exists", "visible", "enable", "width", "annotation", "noBackground"},
    "text": {"label", "align", "font", "height", "parent", "exists", "visible", "enable", "width", "backgroundColor", "annotation", "noBackground"},
    "separator": {"height", "style", "parent", "exists", "visible", "enable", "width", "backgroundColor"},
    "showWindow": set(),
    "deleteUI": set(),
    "setParent": set(),
    "viewFit": set(),
    "ls": set(),
    "delete": set(),
}


def safe_cmds_call(func):
    """Decorator that validates keyword arguments against known Maya flags."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cmd_name = func.__name__
        if cmd_name in KNOWN_FLAGS:
            valid = KNOWN_FLAGS[cmd_name]
            invalid = set(kwargs.keys()) - valid
            if invalid:
                raise TypeError(
                    f"Invalid flag(s) {sorted(invalid)} for command '{cmd_name}'. "
                    f"Valid flags are: {sorted(valid)}"
                )
        return func(*args, **kwargs)
    return wrapper


# Wrap commands
_safe_polyCube = safe_cmds_call(cmds.polyCube)
_safe_polyPlane = safe_cmds_call(cmds.polyPlane)
_safe_polyPrism = safe_cmds_call(cmds.polyPrism)
_safe_polyCylinder = safe_cmds_call(cmds.polyCylinder)
_safe_polyCone = safe_cmds_call(cmds.polyCone)
_safe_move = safe_cmds_call(cmds.move)
_safe_rotate = safe_cmds_call(cmds.rotate)
_safe_scale = safe_cmds_call(cmds.scale)
_safe_group = safe_cmds_call(cmds.group)
_safe_window = safe_cmds_call(cmds.window)
_safe_columnLayout = safe_cmds_call(cmds.columnLayout)
_safe_rowColumnLayout = safe_cmds_call(cmds.rowColumnLayout)
_safe_intSliderGrp = safe_cmds_call(cmds.intSliderGrp)
_safe_floatSliderGrp = safe_cmds_call(cmds.floatSliderGrp)
_safe_optionMenu = safe_cmds_call(cmds.optionMenu)
_safe_button = safe_cmds_call(cmds.button)
_safe_text = safe_cmds_call(cmds.text)
_safe_separator = safe_cmds_call(cmds.separator)


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def validate_positive(value, name):
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_range(value, name, min_val=None, max_val=None):
    if min_val is not None and value < min_val:
        raise ValueError(f"{name} must be >= {min_val}, got {value}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{name} must be <= {max_val}, got {value}")
    return value


def validate_int(value, name):
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    return value


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

# Global references to UI elements (updated when building type changes)
_ui = {
    "building_type_menu": None,
    "roof_type_menu": None,
    "floors_slider": None,
    "width_slider": None,
    "depth_slider": None,
    "windows_slider": None,
    "window_size_slider": None,
    "description_text": None,
}


def on_building_type_changed(*args):
    """Callback when building type dropdown changes — updates sliders and roof options."""
    try:
        selected = cmds.optionMenu(_ui["building_type_menu"], query=True, value=True)
        # Look up by label since optionMenu returns the display label
        btype = None
        for key, cfg in BUILDING_TYPES.items():
            if cfg["label"] == selected:
                btype = cfg
                break
        if btype is None:
            return

        # Update description
        cmds.text(_ui["description_text"], edit=True, label=btype["description"])

        # Update floor slider
        cmds.intSliderGrp(_ui["floors_slider"], edit=True,
                          minValue=btype["min_floors"],
                          maxValue=btype["max_floors"],
                          fieldMinValue=btype["min_floors"],
                          fieldMaxValue=btype["max_floors"],
                          value=btype["default_floors"])

        # Update width slider
        w_min, w_max = btype["width_range"]
        cmds.floatSliderGrp(_ui["width_slider"], edit=True,
                            minValue=w_min, maxValue=w_max,
                            fieldMinValue=w_min, fieldMaxValue=w_max,
                            value=(w_min + w_max) / 2.0)

        # Update depth slider
        d_min, d_max = btype["depth_range"]
        cmds.floatSliderGrp(_ui["depth_slider"], edit=True,
                            minValue=d_min, maxValue=d_max,
                            fieldMinValue=d_min, fieldMaxValue=d_max,
                            value=(d_min + d_max) / 2.0)

        # Update windows slider
        win_min, win_max = btype["windows_per_floor_range"]
        cmds.intSliderGrp(_ui["windows_slider"], edit=True,
                          minValue=win_min, maxValue=win_max,
                          fieldMinValue=win_min, fieldMaxValue=win_max,
                          value=btype["default_windows"])

        # Update window size slider
        ws_min, ws_max = btype["window_size_range"]
        cmds.floatSliderGrp(_ui["window_size_slider"], edit=True,
                            minValue=ws_min, maxValue=ws_max,
                            fieldMinValue=ws_min, fieldMaxValue=ws_max,
                            value=btype["default_window_size"])

        # Update roof type dropdown
        existing = cmds.optionMenu(_ui["roof_type_menu"], query=True, itemListLong=True) or []
        for item in existing:
            cmds.deleteUI(item)
        for roof_key in btype["roof_types"]:
            cmds.menuItem(label=ROOF_TYPES[roof_key]["label"], parent=_ui["roof_type_menu"])
        cmds.optionMenu(_ui["roof_type_menu"], edit=True, value=ROOF_TYPES[btype["default_roof"]]["label"])

        print("[UI] Switched to: " + btype["label"])
    except Exception as e:
        print("[ERROR] on_building_type_changed: " + str(e))


def on_roof_type_changed(*args):
    """Callback when roof type dropdown changes."""
    pass  # Roof type is read at generation time


def create_ui():
    if cmds.window("BuildingSimulatorWin", exists=True):
        cmds.deleteUI("BuildingSimulatorWin")

    win = _safe_window("BuildingSimulatorWin", title="Building Simulator", widthHeight=(380, 600))
    _safe_columnLayout(adjustableColumn=True, rowSpacing=6, columnAttach=("both", 10))

    _safe_text(label="Building Simulator", font="boldLabelFont", height=30)
    _safe_separator(height=8)

    # Building type dropdown
    _safe_text(label="Building Type", align="left")
    _ui["building_type_menu"] = _safe_optionMenu(
        label="",
        changeCommand=on_building_type_changed,
        alwaysCallChangeCommand=True,
        width=340
    )
    for key, btype in BUILDING_TYPES.items():
        cmds.menuItem(label=btype["label"], parent=_ui["building_type_menu"])

    _safe_separator(height=5)

    # Description
    _ui["description_text"] = _safe_text(
        label=BUILDING_TYPES["skyscraper"]["description"],
        align="center",
        font="smallPlainLabelFont",
        height=20
    )

    _safe_separator(height=8)

    # Roof type dropdown
    _safe_text(label="Roof Type", align="left")
    _ui["roof_type_menu"] = _safe_optionMenu(
        label="",
        changeCommand=on_roof_type_changed,
        width=340
    )
    default_roofs = BUILDING_TYPES["skyscraper"]["roof_types"]
    for roof_key in default_roofs:
        cmds.menuItem(label=ROOF_TYPES[roof_key]["label"], parent=_ui["roof_type_menu"])
    cmds.optionMenu(_ui["roof_type_menu"], edit=True,
                    value=ROOF_TYPES[BUILDING_TYPES["skyscraper"]["default_roof"]]["label"])

    _safe_separator(height=8)

    # Sliders
    _safe_text(label="Number of Buildings", align="left")
    building_count_slider = _safe_intSliderGrp(
        field=True, label="", minValue=1, maxValue=10, value=3,
        fieldMinValue=1, fieldMaxValue=20, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=5)
    _safe_text(label="Building Height (Floors)", align="left")
    _ui["floors_slider"] = _safe_intSliderGrp(
        field=True, label="",
        minValue=BUILDING_TYPES["skyscraper"]["min_floors"],
        maxValue=BUILDING_TYPES["skyscraper"]["max_floors"],
        value=BUILDING_TYPES["skyscraper"]["default_floors"],
        fieldMinValue=BUILDING_TYPES["skyscraper"]["min_floors"],
        fieldMaxValue=BUILDING_TYPES["skyscraper"]["max_floors"],
        columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Building Width", align="left")
    _ui["width_slider"] = _safe_floatSliderGrp(
        field=True, label="",
        minValue=BUILDING_TYPES["skyscraper"]["width_range"][0],
        maxValue=BUILDING_TYPES["skyscraper"]["width_range"][1],
        value=4.0,
        fieldMinValue=BUILDING_TYPES["skyscraper"]["width_range"][0],
        fieldMaxValue=BUILDING_TYPES["skyscraper"]["width_range"][1],
        columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Building Depth", align="left")
    _ui["depth_slider"] = _safe_floatSliderGrp(
        field=True, label="",
        minValue=BUILDING_TYPES["skyscraper"]["depth_range"][0],
        maxValue=BUILDING_TYPES["skyscraper"]["depth_range"][1],
        value=4.0,
        fieldMinValue=BUILDING_TYPES["skyscraper"]["depth_range"][0],
        fieldMaxValue=BUILDING_TYPES["skyscraper"]["depth_range"][1],
        columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=5)
    _safe_text(label="Windows Per Floor", align="left")
    _ui["windows_slider"] = _safe_intSliderGrp(
        field=True, label="",
        minValue=BUILDING_TYPES["skyscraper"]["windows_per_floor_range"][0],
        maxValue=BUILDING_TYPES["skyscraper"]["windows_per_floor_range"][1],
        value=BUILDING_TYPES["skyscraper"]["default_windows"],
        fieldMinValue=BUILDING_TYPES["skyscraper"]["windows_per_floor_range"][0],
        fieldMaxValue=BUILDING_TYPES["skyscraper"]["windows_per_floor_range"][1],
        columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Window Size", align="left")
    _ui["window_size_slider"] = _safe_floatSliderGrp(
        field=True, label="",
        minValue=BUILDING_TYPES["skyscraper"]["window_size_range"][0],
        maxValue=BUILDING_TYPES["skyscraper"]["window_size_range"][1],
        value=BUILDING_TYPES["skyscraper"]["default_window_size"],
        fieldMinValue=BUILDING_TYPES["skyscraper"]["window_size_range"][0],
        fieldMaxValue=BUILDING_TYPES["skyscraper"]["window_size_range"][1],
        columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=10)

    # Buttons — Generate is green, Clear is default
    btn_layout = _safe_rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 165), (2, 165)])
    _safe_button(
        label="Generate Buildings", height=45,
        command=lambda *args: generate_buildings(
            building_count_slider,
            _ui["building_type_menu"],
            _ui["roof_type_menu"],
            _ui["floors_slider"],
            _ui["width_slider"],
            _ui["depth_slider"],
            _ui["windows_slider"],
            _ui["window_size_slider"],
        ),
        backgroundColor=(0.2, 0.7, 0.2)
    )
    _safe_button(label="Clear All", height=45, command=lambda *args: clear_scene())
    cmds.setParent("..")

    _safe_separator(height=8)
    _safe_text(label="Tip: Pick a type, adjust sliders, then click Generate.", align="center", font="smallPlainLabelFont")

    # Show window immediately and bring to front
    cmds.showWindow(win)
    cmds.window(win, edit=True, visible=True, topLeftCorner=(100, 100))
    cmds.window(win, edit=True, **{"raise": True})
    print("[UI] Building Simulator window created.")


# ---------------------------------------------------------------------------
# Scene management
# ---------------------------------------------------------------------------

def clear_scene():
    all_nodes = cmds.ls("BuildingSim_*", long=True)
    if all_nodes:
        cmds.delete(all_nodes)
        print("[Clear] Deleted " + str(len(all_nodes)) + " node(s)")
    else:
        print("[Clear] Nothing to delete")


# ---------------------------------------------------------------------------
# Roof creation
# ---------------------------------------------------------------------------

def create_roof(roof_type, building_name, width, depth, roof_height, base_y, x_position):
    """Create a roof of the specified type. Returns the roof node name."""
    overhang = 0.5

    if roof_type == "flat":
        roof = _safe_polyCube(
            name=building_name + "_Roof",
            width=width + overhang,
            depth=depth + overhang,
            height=roof_height
        )[0]
        _safe_move(x_position, base_y + roof_height / 2.0, 0, roof)

    elif roof_type == "gabled":
        # Gabled roof: triangular prism standing upright
        # polyPrism creates a prism with triangle face in XY plane,
        # base along X, apex pointing up along Y, extruded along Z.
        # length = triangle base width, height = prism depth (along Z)
        roof = _safe_polyPrism(
            name=building_name + "_Roof",
            length=width + overhang,
            height=depth + overhang,
            subdivisions=1
        )[0]
        # No rotation needed — triangle already points up along Y
        # Position so the base of the triangle sits at the top of the building
        _safe_move(x_position, base_y, 0, roof)

    elif roof_type == "pointed":
        # Pointed roof using polyCone
        roof = _safe_polyCone(
            name=building_name + "_Roof",
            radius=max(width, depth) / 2.0 + overhang / 2.0,
            height=roof_height * 2.0,
            subdivisionsX=4
        )[0]
        _safe_rotate(45, 0, 0, roof)
        _safe_move(x_position, base_y + roof_height, 0, roof)

    elif roof_type == "terrace":
        # Terrace roof: flat slab with raised parapet edges
        roof = _safe_polyCube(
            name=building_name + "_Roof",
            width=width + overhang,
            depth=depth + overhang,
            height=roof_height * 0.5
        )[0]
        _safe_move(x_position, base_y + roof_height * 0.25, 0, roof)

        # Parapet walls
        parapet_h = roof_height * 0.5
        parapet_t = 0.15
        p1 = _safe_polyCube(
            name=building_name + "_Parapet_F",
            width=width + overhang, depth=parapet_t, height=parapet_h
        )[0]
        _safe_move(x_position, base_y + roof_height * 0.5 + parapet_h / 2.0,
                   (depth + overhang) / 2.0 - parapet_t / 2.0, p1)

        p2 = _safe_polyCube(
            name=building_name + "_Parapet_B",
            width=width + overhang, depth=parapet_t, height=parapet_h
        )[0]
        _safe_move(x_position, base_y + roof_height * 0.5 + parapet_h / 2.0,
                   -(depth + overhang) / 2.0 + parapet_t / 2.0, p2)

        p3 = _safe_polyCube(
            name=building_name + "_Parapet_L",
            width=parapet_t, depth=depth + overhang, height=parapet_h
        )[0]
        _safe_move(-(width + overhang) / 2.0 + parapet_t / 2.0,
                   base_y + roof_height * 0.5 + parapet_h / 2.0, 0, p3)

        p4 = _safe_polyCube(
            name=building_name + "_Parapet_R",
            width=parapet_t, depth=depth + overhang, height=parapet_h
        )[0]
        _safe_move((width + overhang) / 2.0 - parapet_t / 2.0,
                   base_y + roof_height * 0.5 + parapet_h / 2.0, 0, p4)

        # Group parapets with roof
        roof = _safe_group([roof, p1, p2, p3, p4], name=building_name + "_Roof")

    else:
        # Fallback to flat
        roof = _safe_polyCube(
            name=building_name + "_Roof",
            width=width + overhang,
            depth=depth + overhang,
            height=roof_height
        )[0]
        _safe_move(x_position, base_y + roof_height / 2.0, 0, roof)

    return roof


# ---------------------------------------------------------------------------
# Building generation
# ---------------------------------------------------------------------------

def create_building_from_sliders(building_count_slider, building_type_menu, roof_type_menu,
                                  floors_slider, width_slider, depth_slider,
                                  windows_slider, window_size_slider):
    try:
        num_buildings = cmds.intSliderGrp(building_count_slider, query=True, value=True)
        building_type_label = cmds.optionMenu(building_type_menu, query=True, value=True)
        roof_type_label = cmds.optionMenu(roof_type_menu, query=True, value=True)
        num_floors = cmds.intSliderGrp(floors_slider, query=True, value=True)
        width = cmds.floatSliderGrp(width_slider, query=True, value=True)
        depth = cmds.floatSliderGrp(depth_slider, query=True, value=True)
        windows_per_floor = cmds.intSliderGrp(windows_slider, query=True, value=True)
        window_size = cmds.floatSliderGrp(window_size_slider, query=True, value=True)

        # Look up building type config
        btype = None
        for key, cfg in BUILDING_TYPES.items():
            if cfg["label"] == building_type_label:
                btype = cfg
                break
        if btype is None:
            btype = BUILDING_TYPES["skyscraper"]

        # Look up roof type key
        roof_type = None
        for key, cfg in ROOF_TYPES.items():
            if cfg["label"] == roof_type_label:
                roof_type = key
                break
        if roof_type is None:
            roof_type = btype["default_roof"]

        # Validate inputs
        validate_int(num_buildings, "Number of buildings")
        validate_int(num_floors, "Number of floors")
        validate_int(windows_per_floor, "Windows per floor")
        validate_positive(width, "Width")
        validate_positive(depth, "Depth")
        validate_positive(window_size, "Window size")
        validate_range(num_buildings, "Number of buildings", min_val=1, max_val=100)
        validate_range(num_floors, "Number of floors", min_val=1, max_val=200)
        validate_range(windows_per_floor, "Windows per floor", min_val=1, max_val=50)
        validate_range(width, "Width", min_val=0.1, max_val=100.0)
        validate_range(depth, "Depth", min_val=0.1, max_val=100.0)
        validate_range(window_size, "Window size", min_val=0.1, max_val=10.0)

        print("\n" + "=" * 50)
        print("  CREATING BUILDING")
        print("  Type: " + btype["label"])
        print("  Roof: " + ROOF_TYPES[roof_type]["label"])
        print("  Count: " + str(num_buildings))
        print("  Floors: " + str(num_floors))
        print("  Width: " + str(width))
        print("  Depth: " + str(depth))
        print("  Windows per floor: " + str(windows_per_floor))
        print("  Window size: " + str(window_size))
        print("=" * 50 + "\n")

        clear_scene()

        gap = 2.0
        total_width = (num_buildings * width) + ((num_buildings - 1) * gap)
        start_x = -total_width / 2.0 + width / 2.0

        for i in range(num_buildings):
            x_pos = start_x + (i * (width + gap))
            create_building(
                building_index=i + 1,
                btype=btype,
                roof_type=roof_type,
                num_floors=num_floors,
                width=width,
                depth=depth,
                windows_per_floor=windows_per_floor,
                window_size=window_size,
                x_position=x_pos
            )

        cmds.viewFit(all=True)
        print("\n[DONE] Created " + str(num_buildings) + " building(s).\n")

    except (TypeError, ValueError) as e:
        print("\n[ERROR] " + str(e) + "\n")
        cmds.warning(str(e))


def create_building(building_index, btype, roof_type, num_floors, width, depth,
                    windows_per_floor, window_size, x_position):
    building_name = "BuildingSim_Building_" + str(building_index)
    floor_height = btype["floor_height"]
    building_height = num_floors * floor_height

    # Building body
    body = _safe_polyCube(
        name=building_name + "_Body",
        width=width,
        height=building_height,
        depth=depth
    )[0]
    _safe_move(x_position, building_height / 2.0, 0, body)

    # Roof
    roof_height = min(width, depth) * 0.3
    roof = create_roof(roof_type, building_name, width, depth, roof_height,
                       building_height, x_position)

    # Windows — flush against walls, rotated to face outward
    # polyPlane default: lies on XZ plane (normal = +Y)
    # Front/back walls: rotate 90 around X -> normal faces +Z / -Z
    # Left/right walls: rotate 90 around Y -> normal faces -X / +X
    window_nodes = []
    window_offset = 0.02  # Slight offset to prevent z-fighting

    for floor in range(num_floors):
        y_pos = (floor * floor_height) + (floor_height * 0.55)

        for w in range(windows_per_floor):
            if windows_per_floor == 1:
                x_offset = 0
            else:
                spacing = (width - window_size - 0.4) / (windows_per_floor - 1)
                x_offset = -((width - window_size - 0.4) / 2.0) + (w * spacing)

            # Front wall windows — face +Z
            win_front = _safe_polyPlane(
                name=building_name + "_Win_F" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_rotate(90, 0, 0, win_front)
            _safe_move(x_position + x_offset, y_pos,
                       (depth / 2.0) + window_offset, win_front)
            window_nodes.append(win_front)

            # Back wall windows — face -Z
            win_back = _safe_polyPlane(
                name=building_name + "_Win_B" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_rotate(90, 0, 0, win_back)
            _safe_move(x_position + x_offset, y_pos,
                       -(depth / 2.0) - window_offset, win_back)
            window_nodes.append(win_back)

            # Left wall windows — face -X
            win_left = _safe_polyPlane(
                name=building_name + "_Win_L" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_rotate(0, 90, 0, win_left)
            _safe_move(x_position - (width / 2.0) - window_offset, y_pos,
                       x_offset, win_left)
            window_nodes.append(win_left)

            # Right wall windows — face +X
            win_right = _safe_polyPlane(
                name=building_name + "_Win_R" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_rotate(0, 90, 0, win_right)
            _safe_move(x_position + (width / 2.0) + window_offset, y_pos,
                       x_offset, win_right)
            window_nodes.append(win_right)

    # Door (only for building types that have one)
    if btype["has_door"]:
        door = _safe_polyPlane(
            name=building_name + "_Door",
            width=window_size * 0.8,
            height=window_size * 1.5
        )[0]
        _safe_rotate(90, 0, 0, door)
        _safe_move(x_position, (window_size * 1.5) / 2.0,
                   (depth / 2.0) + window_offset, door)
        window_nodes.append(door)

    # Group everything
    all_parts = [body, roof] + window_nodes
    building_group = _safe_group(all_parts, name=building_name)

    print("[Building " + str(building_index) + "] " + btype["label"] +
          " - " + str(num_floors) + " floors, " +
          str(windows_per_floor) + " windows/floor, " +
          ROOF_TYPES[roof_type]["label"])
    return building_group


def generate_buildings(building_count_slider, building_type_menu, roof_type_menu,
                       floors_slider, width_slider, depth_slider,
                       windows_slider, window_size_slider):
    create_building_from_sliders(
        building_count_slider, building_type_menu, roof_type_menu,
        floors_slider, width_slider, depth_slider,
        windows_slider, window_size_slider
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 50)
    print("  BUILDING SIMULATOR LOADED (SAFE VERSION)")
    print("=" * 50 + "\n")
    create_ui()


main()
