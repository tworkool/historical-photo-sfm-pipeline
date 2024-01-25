import json
import bpy
import bmesh
from mathutils import Matrix, Vector
import os
from random import uniform
import time

root_dir = os.getcwd()

MAX_POINT_CAP = None
ITERATION_BATCH_SIZE = 1000
DOWNSAMPLING = None


def adjust_scene(data):
    w = data["w"]
    h = data["h"]
    bpy.context.scene.render.resolution_x = w
    bpy.context.scene.render.resolution_y = h


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
            camera_obj.data.lens = frame_metadata["focal_length"]
            if (
                "lens_sensor_size" in frame_metadata
                and frame_metadata["lens_sensor_size"]
            ):
                camera_obj.data.sensor_width = frame_metadata["lens_sensor_size"]

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
        color = tuple(point["rgb"]) + (1,)  # Add alpha component

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
                loop[color_layer] = [uniform(0, 1) for c in "rgb"] + [1]

        # Assign color to the vertex directly
        # for loop in vert.link_loops:
        #    loop[color_layer] = color

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
        draw_points(start_point, new_end_point, downsampling)
        print(
            f"Iteration finished | {int(((start_point + 1) / max_points) * 100)}% done\t | elapsed it time {round(time.time() - i_start_time, 2)}s\t | elapsed total {round(time.time() - start_time, 2)}s"
        )
        start_point = new_end_point
        iterarion += 1


if __name__ == "__main__":
    # Load the data from the JSON file
    with open(
        "D:\\dev\\python\\historical-photo-sfm-pipeline\\data\\test\\transforms_withpoints.json"
    ) as f:
        transformations = json.load(f)

    adjust_scene(transformations)
    draw_frames(transformations)
    draw_point_batches(
        transformations, ITERATION_BATCH_SIZE, MAX_POINT_CAP, DOWNSAMPLING
    )
