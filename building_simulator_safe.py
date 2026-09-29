#!/usr/bin/env python3
"""
building_simulator_safe.py — Building Simulator with error prevention.

This version prevents "Invalid flag" errors by:
1. Using only verified Maya command flags
2. Validating all inputs before passing them to cmds
3. Wrapping Maya calls in try/except with helpful error messages
4. Using a flag-checking helper to catch mistakes early
"""

import maya.cmds as cmds
import functools
import inspect


# ---------------------------------------------------------------------------
# Flag validation system — prevents "Invalid flag" errors before they happen
# ---------------------------------------------------------------------------

# Registry of known-good flags for Maya commands we use.
# If a command isn't listed here, we skip validation (to avoid false positives
# when Autodesk adds new flags in future versions).
KNOWN_FLAGS = {
    "polyCube": {"width", "height", "depth", "name", "axis", "cuv", "ch"},
    "polyPlane": {"width", "height", "name", "axis", "cuv", "ch", "sx", "sy"},
    "polyPrism": {"length", "width", "height", "name", "subdivisions", "axis", "cuv", "ch"},
    "polyCylinder": {"radius", "height", "name", "axis", "subdivisionsX", "subdivisionsY", "subdivisionsCap", "cuv", "ch"},
    "move": {"x", "y", "z", "absolute", "relative", "worldSpace", "objectSpace"},
    "group": {"name", "parent", "relative", "absolute"},
    "window": {"title", "widthHeight", "sizeable", "minimizeButton", "maximizeButton", "menuBar", "toolbox", "titleBar", "resizeToFitChildren", "sizeable"},
    "columnLayout": {"adjustableColumn", "rowSpacing", "columnAttach", "columnWidth", "columnAlign", "parent", "childArray", "numberOfChildren", "exists", "visible", "enable", "width", "height", "backgroundColor", "attachControl", "attachNone", "attachOppositeControl", "attachOppositeNone", "attachPosition", "attachControl", "attachNone", "attachOppositeControl", "attachOppositeNone", "attachPosition"},
    "rowColumnLayout": {"numberOfColumns", "columnWidth", "columnAlign", "columnAttach", "rowSpacing", "parent", "childArray", "numberOfChildren", "exists", "visible", "enable", "width", "height", "backgroundColor"},
    "intSliderGrp": {"field", "label", "minValue", "maxValue", "value", "fieldMinValue", "fieldMaxValue", "columnWidth", "columnAlign", "parent", "changeCommand", "dragCommand", "fieldStep", "sliderStep", "exists", "visible", "enable", "width", "height", "backgroundColor", "annotation", "noBackground"},
    "floatSliderGrp": {"field", "label", "minValue", "maxValue", "value", "fieldMinValue", "fieldMaxValue", "columnWidth", "columnAlign", "parent", "changeCommand", "dragCommand", "fieldStep", "sliderStep", "exists", "visible", "enable", "width", "height", "backgroundColor", "annotation", "noBackground"},
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


# Wrap the most error-prone commands
_safe_polyCube = safe_cmds_call(cmds.polyCube)
_safe_polyPlane = safe_cmds_call(cmds.polyPlane)
_safe_polyPrism = safe_cmds_call(cmds.polyPrism)
_safe_polyCylinder = safe_cmds_call(cmds.polyCylinder)
_safe_move = safe_cmds_call(cmds.move)
_safe_group = safe_cmds_call(cmds.group)
_safe_window = safe_cmds_call(cmds.window)
_safe_columnLayout = safe_cmds_call(cmds.columnLayout)
_safe_rowColumnLayout = safe_cmds_call(cmds.rowColumnLayout)
_safe_intSliderGrp = safe_cmds_call(cmds.intSliderGrp)
_safe_floatSliderGrp = safe_cmds_call(cmds.floatSliderGrp)
_safe_button = safe_cmds_call(cmds.button)
_safe_text = safe_cmds_call(cmds.text)
_safe_separator = safe_cmds_call(cmds.separator)


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def validate_positive(value, name):
    """Ensure a numeric value is positive."""
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_range(value, name, min_val=None, max_val=None):
    """Ensure a numeric value falls within an optional range."""
    if min_val is not None and value < min_val:
        raise ValueError(f"{name} must be >= {min_val}, got {value}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{name} must be <= {max_val}, got {value}")
    return value


def validate_int(value, name):
    """Ensure a value is an integer."""
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    return value


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def create_ui():
    if cmds.window("BuildingSimulatorWin", exists=True):
        cmds.deleteUI("BuildingSimulatorWin")

    win = _safe_window("BuildingSimulatorWin", title="Building Simulator", widthHeight=(350, 500))
    _safe_columnLayout(adjustableColumn=True, rowSpacing=8, columnAttach=("both", 10))

    _safe_text(label="Building Simulator", font="boldLabelFont", height=30)
    _safe_separator(height=10)

    _safe_text(label="Number of Buildings", align="left")
    building_count_slider = _safe_intSliderGrp(
        field=True, label="", minValue=1, maxValue=10, value=3,
        fieldMinValue=1, fieldMaxValue=20, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=5)
    _safe_text(label="Building Height (Floors)", align="left")
    floors_slider = _safe_intSliderGrp(
        field=True, label="", minValue=1, maxValue=50, value=5,
        fieldMinValue=1, fieldMaxValue=100, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Building Width (Fat/Thin)", align="left")
    width_slider = _safe_floatSliderGrp(
        field=True, label="", minValue=1.0, maxValue=10.0, value=4.0,
        fieldMinValue=0.5, fieldMaxValue=20.0, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Building Depth", align="left")
    depth_slider = _safe_floatSliderGrp(
        field=True, label="", minValue=1.0, maxValue=10.0, value=4.0,
        fieldMinValue=0.5, fieldMaxValue=20.0, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=5)
    _safe_text(label="Windows Per Floor", align="left")
    windows_slider = _safe_intSliderGrp(
        field=True, label="", minValue=1, maxValue=10, value=3,
        fieldMinValue=1, fieldMaxValue=20, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_text(label="Window Size", align="left")
    window_size_slider = _safe_floatSliderGrp(
        field=True, label="", minValue=0.2, maxValue=2.0, value=0.8,
        fieldMinValue=0.1, fieldMaxValue=5.0, columnWidth=[(1, 120), (2, 80)]
    )

    _safe_separator(height=10)
    btn_layout = _safe_rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 160), (2, 160)])
    _safe_button(
        label="Generate Buildings", height=40,
        command=lambda *args: generate_buildings(
            building_count_slider, floors_slider, width_slider,
            depth_slider, windows_slider, window_size_slider
        )
    )
    _safe_button(label="Clear All", height=40, command=lambda *args: clear_scene())
    cmds.setParent("..")

    _safe_separator(height=10)
    _safe_button(
        label="Create", height=50,
        command=lambda *args: create_building_from_sliders(
            building_count_slider, floors_slider, width_slider,
            depth_slider, windows_slider, window_size_slider
        ),
        backgroundColor=(0.3, 0.6, 0.3)
    )

    _safe_separator(height=10)
    _safe_text(label="Tip: Adjust sliders, then click Create.", align="center", font="smallPlainLabelFont")

    cmds.showWindow(win)
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
# Building generation
# ---------------------------------------------------------------------------

def create_building_from_sliders(building_count_slider, floors_slider, width_slider,
                                  depth_slider, windows_slider, window_size_slider):
    try:
        num_buildings = cmds.intSliderGrp(building_count_slider, query=True, value=True)
        num_floors = cmds.intSliderGrp(floors_slider, query=True, value=True)
        width = cmds.floatSliderGrp(width_slider, query=True, value=True)
        depth = cmds.floatSliderGrp(depth_slider, query=True, value=True)
        windows_per_floor = cmds.intSliderGrp(windows_slider, query=True, value=True)
        window_size = cmds.floatSliderGrp(window_size_slider, query=True, value=True)

        # Validate all inputs before creating anything
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


def create_building(building_index, num_floors, width, depth, windows_per_floor,
                    window_size, x_position):
    building_name = "BuildingSim_Building_" + str(building_index)
    floor_height = 3.0

    # Building body — polyCube supports width, height, depth
    body = _safe_polyCube(
        name=building_name + "_Body",
        width=width,
        height=num_floors * floor_height,
        depth=depth
    )[0]
    _safe_move(x_position, (num_floors * floor_height) / 2.0, 0, body)

    # Roof — polyCube (NOT polyPrism, which has no width/depth flags)
    roof_height = min(width, depth) * 0.3
    roof = _safe_polyCube(
        name=building_name + "_Roof",
        width=width + 0.5,
        depth=depth + 0.5,
        height=roof_height
    )[0]
    _safe_move(x_position, (num_floors * floor_height) + (roof_height / 2.0), 0, roof)

    # Windows
    window_nodes = []
    for floor in range(num_floors):
        y_pos = (floor * floor_height) + 1.5

        for w in range(windows_per_floor):
            if windows_per_floor == 1:
                x_offset = 0
            else:
                spacing = (width - window_size - 0.4) / (windows_per_floor - 1)
                x_offset = -((width - window_size - 0.4) / 2.0) + (w * spacing)

            win_front = _safe_polyPlane(
                name=building_name + "_Win_F" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_move(x_position + x_offset, y_pos, (depth / 2.0) + 0.01, win_front)
            window_nodes.append(win_front)

            win_back = _safe_polyPlane(
                name=building_name + "_Win_B" + str(floor) + "_" + str(w),
                width=window_size,
                height=window_size * 1.2
            )[0]
            _safe_move(x_position + x_offset, y_pos, -(depth / 2.0) - 0.01, win_back)
            window_nodes.append(win_back)

    # Door
    door = _safe_polyPlane(
        name=building_name + "_Door",
        width=window_size * 0.8,
        height=window_size * 1.5
    )[0]
    _safe_move(x_position, (window_size * 1.5) / 2.0, (depth / 2.0) + 0.01, door)
    window_nodes.append(door)

    # Group everything
    all_parts = [body, roof] + window_nodes
    building_group = _safe_group(all_parts, name=building_name)

    print("[Building " + str(building_index) + "] Created: " +
          str(num_floors) + " floors, " + str(windows_per_floor) + " windows/floor")
    return building_group


def generate_buildings(building_count_slider, floors_slider, width_slider,
                       depth_slider, windows_slider, window_size_slider):
    create_building_from_sliders(
        building_count_slider, floors_slider, width_slider,
        depth_slider, windows_slider, window_size_slider
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
