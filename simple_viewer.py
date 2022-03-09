####
# Much of this code is from the open3d example code
###
import sys, os, glob, platform
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
from gui3d import Gui3DApp

isMacOS = (platform.system() == "Darwin")

def main():
    # We need to initalize the application, which finds the necessary shaders
    # for rendering and prepares the cross-platform window abstraction.
    gui.Application.instance.initialize()

    w = Gui3DApp(1024, 768)

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "/home/equant/work/sandbox/3D/ariyan_segmentation/test_full_leaf_index.ply"

    if os.path.exists(path):
        w.load(path)
    else:
        w.window.show_message_box("Error",
                                  "Could not open file '" + path + "'")

    # Run the event loop. This will not return until the last window is closed.
    gui.Application.instance.run()


if __name__ == "__main__":
    main()
