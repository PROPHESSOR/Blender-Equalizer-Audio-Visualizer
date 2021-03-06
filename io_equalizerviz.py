# EqualizerViz - Audio visualization plugin
# Created by PROPHESSOR for Blender 2.80 (04.01.2020)
#
# Based on sirrandalot's "Audio visualisation script" for Blender 2.71

import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras.wm_utils.progress_report import ProgressReport

bl_info = {
    "name": "Import Equalizer Audio",
    "author": "PROPHESSOR",
    "description": "Imports the audio file to create equalizer visualization. Wav import is more faster.",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import > Equalizer",
    "url": "https://github.com/PROPHESSOR/Blender-Equalizer-Audio-Visualizer",
    "tracker_url": "https://github.com/Blender/Blender-Equalizer-Audio-Visualizer/issues",
    "category": "Import-Export"
}

def menu_func_import(self, context):
    self.layout.operator(ImportEqualizerAudioFile.bl_idname, text="Audio for EqualizerViz")

def register():
    bpy.utils.register_class(ImportEqualizerAudioFile)

    # Add import menu item
    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        #2.8+
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    else:
        bpy.types.INFO_MT_file_import.append(menu_func_import)

class ImportEqualizerAudioFile(Operator, ImportHelper):
    """Imports the audio file to visualize using equalizer simulator"""
    bl_idname = "equalizerviz_blender.import_audio"
    bl_label = "Import audio file to visualize. Wav is more faster."

    filename_ext = ".wav" # Wav import is more faster

    #filter_glob = StringProperty(
    #    default = "*.wav",
    #    options = { 'HIDDEN' },
    #    maxlen= 255
    #)
    
    numbars = IntProperty(
        name="Number of equalizer bars",
        description=(
            "Number of bars and frequency ranges."
        ),
        default=64
    )


    def execute(self, context):
        with ProgressReport(context.window_manager) as progress:
            progress.enter_substeps(self.numbars, "Importing frequency %d ranges as bars %r..." % (self.numbars, self.filepath))

            for i in range(0, self.numbars):
                # Add a plane and set it's origin to one of its edges
                bpy.ops.mesh.primitive_plane_add(location=((i + (i * 0.5)), 0, 0))
                bpy.context.scene.cursor.location = bpy.context.active_object.location
                bpy.context.scene.cursor.location.y -= 1
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                # Scale the plane on the x and y axis, then apply the transformation
                bpy.context.active_object.scale.x = 0.5
                bpy.context.active_object.scale.y = 20
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
                # Insert a scaling keyframe and lock the x and z axis
                bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                bpy.context.active_object.animation_data.action.fcurves[0].lock = True
                bpy.context.active_object.animation_data.action.fcurves[2].lock = True
                
                # Set the window context to the graph editor
                bpy.context.area.type = 'GRAPH_EDITOR'
                
                # Expression to determine the frequency range of the bars
                low = i**2 + 20
                high = (i + 1)**2 + 20
                
                progress.step("Bar %d of %d: %d Hz - %d Hz. Baking..." % (i, self.numbars, low, high))
                
                # Bake that range of frequencies to the current plane (along the y axis)
                bpy.ops.graph.sound_bake(filepath=self.filepath, low=(low), high=(high))
                
                # Lock the y axis
                bpy.context.active_object.animation_data.action.fcurves[1].lock = True

            progress.leave_substeps("Done.")
            
        return { "FINISHED" }
            
            
if __name__ == "__main__":
    register()
