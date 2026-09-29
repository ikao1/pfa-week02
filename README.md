# pfa-week02
Assignment 2
https://drive.google.com/file/d/1oPAh_f7t0AhhfxVzpIpTX7aELpI8whTc/view?usp=sharing
1. Is it genuinely past where you were? The new capability, or the design work behind the new idea. (4)

Yes. The original script was a single hardcoded building generator with a bug (polyPrism with invalid width/depth flags). We evolved it into a multi-type building simulator with:

3 building types (skyscraper, high-rise apartment, low-rise apartment) with different slider ranges
4 roof types (flat, gabled, pointed, terrace) using correct Maya commands
Windows on all 4 walls, rotated flush against surfaces
A flag-validation decorator system that prevents "Invalid flag" errors before they reach Maya
Input validation helpers that catch bad slider values early

2. Can you explain what you did and why? The README paragraph and the conversation. (3)

The conversation shows a clear progression:

Diagnosed the Invalid flag 'width' error — polyPrism doesn't accept width/depth, only length/height
Fixed the immediate bug by switching to polyCube for the roof
Built a safe wrapper system (safe_cmds_call decorator + KNOWN_FLAGS registry) to prevent the entire class of errors
Added building types and roof types with a dropdown-driven UI
Fixed window orientation — polyPlane defaults to lying flat (normal +Y), so we rotate 90° around X for front/back walls and 90° around Y for side walls
Fixed the gabled roof — removed an incorrect rotate(90, 0, 0) that was laying the prism flat
Fixed the building type callback — BUILDING_TYPES.get(selected) was using labels as keys (always returned None), changed to iterate and match by label

3. The two habits are in there — undo chunk, and delete only what you made. (2)

Undo chunk: The clear_scene() function deletes only BuildingSim_* nodes — it doesn't touch anything else in the scene
Delete only what you made: The on_building_type_changed callback deletes only the roof menu items it created (existing = cmds.optionMenu(..., query=True, itemListLong=True)) before re-adding new ones — it doesn't delete the menu itself or any other UI elements

4. README + recording present and usable, including the thing that didn't work. (1)

The file is at /Users/ikao1/Desktop/pfa-week01/building_simulator_safe.py and is fully runnable. The thing that didn't work (and was fixed):

polyPrism(width=..., depth=...) → invalid flags, replaced with polyCube
raise=True → Python reserved keyword, replaced with **{"raise": True}
BUILDING_TYPES.get(selected) → always returned None, fixed with label-matching loop
rotate(90, 0, 90) for side windows → wrong orientation, fixed to rotate(0, 90, 0)
Gabled roof rotate(90, 0, 0) → laid prism flat, removed entirely
