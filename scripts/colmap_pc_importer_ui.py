bl_info = {
    "name": "COLMAP Point Cloud Importer",
    "blender": (2, 90, 0),
    "category": "Object",
}

import json
import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
)
from bpy.types import (
    Operator,
    PropertyGroup,
)
import bmesh
from mathutils import Matrix, Vector
import os
from random import uniform
import time

root_dir = os.getcwd()

TRANSFORMATIONS_JSON = None
MAX_POINT_CAP = None
ITERATION_BATCH_SIZE = 1000
DOWNSAMPLING = None
DEFAULT_FOCAL_LENGTH = 27
DEFAULT_SENSOR_WIDTH = 35
all_cameras = []
selected_camera = 0


def get_cameras():
    return [obj for obj in bpy.context.scene.objects if obj.type == "CAMERA"]


def set_active_camera(index=0):
    global selected_camera
    global all_cameras
    print(len(all_cameras))
    if len(all_cameras) == 0:
        return
    selected_camera = index
    bpy.context.scene.camera = all_cameras[index]
    return


all_cameras = get_cameras()
set_active_camera()
print(selected_camera)


def adjust_scene(data):
    w = data["w"]
    h = data["h"]
    bpy.context.scene.render.resolution_x = w
    bpy.context.scene.render.resolution_y = h
    return


def draw_frames(data):
    # Extract the data
    frames = data["frames"]
    # Create meshes
    frames_mesh = bpy.data.meshes.new("PointCloud")
    # Link the mesh to the scene
    frames_mesh_obj = bpy.data.objects.new("PointCloud", frames_mesh)
    bpy.context.collection.objects.link(frames_mesh_obj)
    # Create a new BMesh object and link it to the mesh
    frames_bmesh = bmesh.new()
    frames_bmesh.from_mesh(frames_mesh)

    # FRAMES
    for frame in frames:
        # Get the transformation matrix
        transform_matrix = Matrix(frame["transform_matrix"])
        # Extract the position from the last column of the matrix
        position = transform_matrix.translation
        # Add the point to the BMesh object
        frames_bmesh.verts.new(position)

        # Create a new camera
        camera = bpy.data.cameras.new("Camera")
        # Create a new object and link the camera to it
        camera_obj = bpy.data.objects.new("Camera", camera)
        bpy.context.collection.objects.link(camera_obj)
        # Set the location of the camera object to the translation part of the matrix
        camera_obj.location = transform_matrix.translation
        # Set the rotation of the camera object to the rotation part of the matrix
        camera_obj.rotation_euler = transform_matrix.to_euler("XYZ")
        # Scale the camera object
        camera_obj.scale = (0.2, 0.2, 0.2)

        # set intrinsics
        frame_metadata = frame["metadata"] if "metadata" in frame else None
        if frame_metadata:
            # Set the background image for the camera
            background_image_path = frame["metadata"][
                "full_path"
            ]  # Set the path to your background image
            camera_obj.data.show_background_images = True
            background_image = camera_obj.data.background_images.new()
            background_image.image = bpy.data.images.load(background_image_path)
            # background_image.image.use_alpha = False  # Set to True if your image has an alpha channel

            # other camera intrinsics
            camera_obj.data.lens = (
                "focal_length" in frame_metadata and frame_metadata["focal_length"]
                if frame_metadata["focal_length"]
                else float(DEFAULT_FOCAL_LENGTH)
            )
            camera_obj.data.sensor_width = (
                frame_metadata["lens_sensor_size"]
                if "lens_sensor_size" in frame_metadata
                and frame_metadata["lens_sensor_size"]
                else float(DEFAULT_SENSOR_WIDTH)
            )

    # Update the mesh with the new data
    frames_bmesh.to_mesh(frames_mesh)
    frames_bmesh.free()


def draw_points(data, start_p, end_p, downsampling=2):
    # Extract the data
    _points = data["points"][
        start_p : end_p if end_p <= len(data["points"]) else len(data["points"])
    ]
    # Create meshes
    points_mesh = bpy.data.meshes.new("PointCloud")
    # Link the mesh to the scene
    points_mesh_obj = bpy.data.objects.new("PointCloud", points_mesh)
    bpy.context.collection.objects.link(points_mesh_obj)
    # Create a new BMesh object and link it to the mesh
    points_bmesh = bmesh.new()
    points_bmesh.from_mesh(points_mesh)

    # POINTS
    for i, point in enumerate(_points):
        if downsampling and i % downsampling == 0:
            continue

        # Get the position and color of the point
        position = Vector(point["xyz"])
        color = (
            point["rgb"][0] / 255.0,
            point["rgb"][1] / 255.0,
            point["rgb"][2] / 255.0,
            1,
        )  # Add alpha component

        # Add the point to the BMesh object
        vert = points_bmesh.verts.new(position)
        vert.normal = (
            position.normalized()
        )  # Normal is required for color to be displayed
        # vert.index = len(points_bmesh.verts)  # Assign index to loop for color assignment

        # Add the color to the vertex color layer
        color_layer = points_bmesh.loops.layers.color.new("Color")

        for face in points_bmesh.faces:
            for loop in face.loops:
                loop[color_layer] = color  # = [uniform(0, 1) for c in "rgb"] + [1]

        # Assign color to the vertex directly
        for loop in vert.link_loops:
            loop[color_layer] = color

    # Update the mesh with the new data
    points_bmesh.to_mesh(points_mesh)
    points_bmesh.free()


def draw_point_batches(data, batch_size=1000, cap=None, downsampling=None):
    points = data["points"]
    max_points = cap if cap else len(points)
    start_point = 0
    iterarion = 1
    start_time = time.time()
    while start_point <= max_points:
        new_end_point = start_point + batch_size
        print(
            f"Starting iteration {iterarion} (points from {start_point}-{new_end_point})"
        )
        i_start_time = time.time()
        draw_points(data, start_point, new_end_point, downsampling)
        print(
            f"Iteration finished | {int(((start_point + 1) / max_points) * 100)}% done\t | elapsed it time {round(time.time() - i_start_time, 2)}s\t | elapsed total {round(time.time() - start_time, 2)}s"
        )
        start_point = new_end_point
        iterarion += 1


# if __name__ == "__main__":
#    adjust_scene()
#    draw_frames()
#    draw_point_batches(ITERATION_BATCH_SIZE, MAX_POINT_CAP, DOWNSAMPLING)


class MyProperties(PropertyGroup):
    """
    slider bar, path, and everything else ....
    """

    colmap_path: StringProperty(
        name="File",
        description="Choose a file:",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
    )


class ColmapPCImporter_StartImport(Operator):
    bl_idname = "colmap_pc_importer.start_import"
    bl_label = "Import Point Cloud"

    def execute(self, context):
        if not TRANSFORMATIONS_JSON:
            print("ERROR: Colmap Transformations JSON not loaded")
            self.report({"ERROR"}, "Colmap Transformations JSON not loaded")
        else:
            adjust_scene(TRANSFORMATIONS_JSON)
            draw_frames(TRANSFORMATIONS_JSON)
            draw_point_batches(
                TRANSFORMATIONS_JSON, ITERATION_BATCH_SIZE, MAX_POINT_CAP, DOWNSAMPLING
            )
            global all_cameras
            all_cameras = get_cameras()
            set_active_camera(0)
        return {"FINISHED"}


class ColmapPCImporter_Downsampling(Operator):
    bl_idname = "colmap_pc_importer.downsampling"
    bl_label = "Downsampling"
    number = bpy.props.IntProperty(name="Downsampling Factor: ")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class ColmapPCImporter_NextCamera(Operator):
    bl_idname = "colmap_pc_importer.next_camera"
    bl_label = "Next Camera"

    def execute(self, context):
        global selected_camera
        print(selected_camera)
        set_active_camera((selected_camera + 1) % len(all_cameras))
        return {"FINISHED"}


class ColmapPCImporter_PreviousCamera(Operator):
    bl_idname = "colmap_pc_importer.previous_camera"
    bl_label = "Previous Camera"

    def execute(self, context):
        global selected_camera
        set_active_camera((selected_camera - 1) % len(all_cameras))
        return {"FINISHED"}


class ColmapPCImporter_LoadData(Operator):
    bl_idname = "colmap_pc_importer.load_data"
    bl_label = "Load Data"
    # somewhere to remember the address of the file

    def execute(self, context):
        path = context.scene.my_tool.colmap_path
        display = "filepath = " + path
        print(display)  # Prints to console
        global TRANSFORMATIONS_JSON
        # Load the data from the JSON file
        with open(path) as f:
            TRANSFORMATIONS_JSON = json.load(f)
        # Window>>>Toggle systen console

        return {"FINISHED"}


class ColmapPCImporterPanel(bpy.types.Panel):
    bl_label = "Colmap Point Cloud Importer"
    bl_idname = "PT_ColmapPCImportPanel"
    bl_space_type = "VIEW_3D"  # display in 3D viewer
    bl_region_type = "UI"
    bl_category = "Colmap Point Cloud Tools"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        mytool = scene.my_tool

        layout.label(text="Step 1: Load Transformations", icon="CUBE")
        layout.prop(mytool, "colmap_path")
        layout.operator(ColmapPCImporter_LoadData.bl_idname)
        layout.separator()

        layout.label(text="Step 2: Settings", icon="CUBE")
        layout.operator(ColmapPCImporter_Downsampling.bl_idname)
        layout.separator()

        layout.label(text="Step 3: Start Import", icon="CUBE")
        layout.operator(ColmapPCImporter_StartImport.bl_idname)
        layout.separator()

        layout.label(text="Step 4: Navigation", icon="CUBE")
        row = layout.row()
        row.operator(ColmapPCImporter_PreviousCamera.bl_idname)
        row.operator(ColmapPCImporter_NextCamera.bl_idname)
        layout.separator()

        # bpy.props.IntProperty(name = "Downsampling Factor")


classes = (
    MyProperties,
    ColmapPCImporter_NextCamera,
    ColmapPCImporter_PreviousCamera,
    ColmapPCImporter_StartImport,
    ColmapPCImporter_Downsampling,
    ColmapPCImporter_LoadData,
    ColmapPCImporterPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
