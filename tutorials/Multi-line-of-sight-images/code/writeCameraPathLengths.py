#get a depth map for all cameras in Blender workspace.
#inspired by https://blender.stackexchange.com/questions/42579/render-depth-map-to-image-with-python-script 
#by default we assume there is only one "scene" in the Blender environment

import os
import bpy
#set the output directory
outDir = "cameraPathLengths/"

scene = bpy.context.scene

#set renderer options
bpy.data.scenes[0].render.engine = "CYCLES"
bpy.data.scenes[0].render.image_settings.file_format = "TIFF"
bpy.data.scenes[0].render.image_settings.color_depth = "16"
bpy.data.scenes[0].render.image_settings.color_mode = "BW"
bpy.data.scenes[0].render.image_settings.tiff_codec = "NONE"
bpy.data.scenes[0].render.resolution_x = 160
bpy.data.scenes[0].render.resolution_y = 120
bpy.data.scenes[0].render.resolution_percentage = 100
bpy.data.scenes[0].display_settings.display_device = "None"
bpy.data.scenes[0].sequencer_colorspace_settings.name = "Linear"

#set min render distance to zero
minRenderDist = 0.001
#set maximum render distance to 5000 m
maxRenderDist = 2000
#Set up rendering of depth map:
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

print("Saving to " + outDir + "...")

#clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)
	
#configure the renderer nodes
rl = tree.nodes.new('CompositorNodeRLayers')
map = tree.nodes.new(type = "CompositorNodeMath")
map.operation = "DIVIDE"
map.inputs[1].default_value = maxRenderDist
links.new(rl.outputs[2], map.inputs[0])
compositeOutput = tree.nodes.new(type = "CompositorNodeComposite")
links.new(map.outputs[0], compositeOutput.inputs[0])

#iterate over each camera and render the z buffer
for ob in scene.objects:
    if ob.type == 'CAMERA':
        bpy.context.scene.camera = ob
        ob.data.clip_start = minRenderDist
        ob.data.clip_end = maxRenderDist
        filePath = outDir + "/" + ob.name + ".tiff"
        print(filePath)
        bpy.data.scenes['Scene'].render.filepath = filePath
        bpy.ops.render.render(write_still = True) 

