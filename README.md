# DragonFF (2.79 compatibility branch)

This repository contains a port scaffold of the DragonFF addon for Blender with compatibility
wrappers for Blender 2.79. The initial commit adds minimal gui, ops, and gtaLib stubs so the
package can be installed and the menus/operators are discoverable. Full parsing of DFF/TXD/COL
is not yet implemented — gtaLib contains placeholder functions to be replaced with real parsers.

Installation
1. Download the repository as a ZIP (Code → Download ZIP) or clone it.
2. In Blender 2.79, install the addon via File → User Preferences → Add-ons → Install from File and
   select the repository folder or zip.
3. Enable the addon. You should see a "DragonFF" panel in the Tool shelf (VIEW3D Tools) and
   Import/Export entries under File → Import / Export.

Next steps
- Implement real DFF/TXD/COL binary format parsing and material/mesh creation in gtaLib.
- Port gui panels’ advanced functionality and any gizmo behaviour to 2.79-compatible UI.
- Add example model and IPL files under assets/ for testing.
