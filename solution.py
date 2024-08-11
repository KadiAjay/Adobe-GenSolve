import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
import svgwrite
import cairosvg

# Define colors for visualizing shapes
colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#FFB833', '#8D33FF', '#33FFB3']

# Step 1: Reading the CSV File
def read_csv_data(csv_path):
    data_points = np.genfromtxt(csv_path, delimiter=',')
    shape_groups = []
    for unique_shape in np.unique(data_points[:, 0]):
        shape_data = data_points[data_points[:, 0] == unique_shape][:, 1:]
        grouped_shapes = []
        for unique_group in np.unique(shape_data[:, 0]):
            group_data = shape_data[shape_data[:, 0] == unique_group][:, 1:]
            grouped_shapes.append(group_data)
        shape_groups.append(grouped_shapes)
    return shape_groups

# Step 2: Visualizing the Shapes
def plot_shapes(shape_groups):
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    for index, shapes in enumerate(shape_groups):
        color = colors[index % len(colors)]
        for shape in shapes:
            ax.plot(shape[:, 0], shape[:, 1], color=color, linewidth=2)
    ax.set_aspect('equal')
    plt.show()

# Step 3: Regularizing Shapes
def apply_convex_hull(shape_groups):
    regularized_shapes = []
    for shapes in shape_groups:
        new_shapes = []
        for shape in shapes:
            if len(shape) >= 3:  # Only apply ConvexHull if there are at least 3 points
                hull = ConvexHull(shape)
                new_shapes.append(shape[hull.vertices])
            else:
                new_shapes.append(shape)  # If not enough points, use the original
        regularized_shapes.append(new_shapes)
    return regularized_shapes

# Step 4: Exploring Symmetry
def symmetry_analysis(shape_groups):
    for shapes in shape_groups:
        for shape in shapes:
            if len(shape) > 1:
                pca = PCA(n_components=2)
                pca.fit(shape)
                explained_variance = pca.explained_variance_ratio_
                print(f"Explained Variance Ratio: {explained_variance}")

# Step 5: Completing Incomplete Shapes (Optional, if required)
def complete_shapes(shape_groups):
    completed_shapes = []
    for shapes in shape_groups:
        completed_group = []
        for shape in shapes:
            if not np.allclose(shape[0], shape[-1]):
                shape = np.vstack([shape, shape[0]])  # Close the shape by adding the first point at the end
            completed_group.append(shape)
        completed_shapes.append(completed_group)
    return completed_shapes

# Step 6: Converting to SVG and Exporting
def save_to_svg(shape_groups, svg_path):
    max_width, max_height = 0, 0
    for shapes in shape_groups:
        for shape in shapes:
            max_width = max(max_width, np.max(shape[:, 0]))
            max_height = max(max_height, np.max(shape[:, 1]))

    padding = 0.1
    max_width, max_height = int(max_width + padding * max_width), int(max_height + padding * max_height)
    drawing = svgwrite.Drawing(svg_path, profile='tiny', shape_rendering='crispEdges')
    svg_group = drawing.g()

    for index, shapes in enumerate(shape_groups):
        path_commands = []
        color = colors[index % len(colors)]
        for shape in shapes:
            path_commands.append(("M", (shape[0, 0], shape[0, 1])))
            for point in range(1, len(shape)):
                path_commands.append(("L", (shape[point, 0], shape[point, 1])))
            if not np.allclose(shape[0], shape[-1]):
                path_commands.append(("Z", None))
        svg_group.add(drawing.path(d=path_commands, fill=color, stroke='none', stroke_width=2))
    
    drawing.add(svg_group)
    drawing.save()

    png_output_path = svg_path.replace('.svg', '.png')
    scale_factor = max(1, 1024 // min(max_height, max_width))
    cairosvg.svg2png(url=svg_path, write_to=png_output_path,
                     parent_width=max_width, parent_height=max_height,
                     output_width=scale_factor * max_width, output_height=scale_factor * max_height,
                     background_color='white')

# Main processing function for multiple files
def process_multiple_files(csv_paths, svg_paths):
    for csv_path, svg_path in zip(csv_paths, svg_paths):
        print(f"\nProcessing {csv_path} -> {svg_path}")
        # Step 1: Read the CSV
        shape_groups = read_csv_data(csv_path)

        # Step 2: Visualize the shapes
        plot_shapes(shape_groups)

        # Step 3: Regularize shapes
        shape_groups = apply_convex_hull(shape_groups)

        # Step 4: Explore symmetry (optional)
        symmetry_analysis(shape_groups)

        # Step 5: Complete incomplete shapes (optional, if required)
        shape_groups = complete_shapes(shape_groups)

        # Step 6: Convert to SVG and export
        save_to_svg(shape_groups, svg_path)

# Example list of CSV and SVG paths
csv_paths = ['frag0.csv', 'frag01_sol.csv', 'frag1.csv', 'frag2_sol.csv', 'frag2.csv', 
             'isolated_sol.csv', 'isolated.csv', 'occlusion1_sol.csv', 'occlusion1.csv', 
             'occlusion2.csv', 'occlusion2_sol.csv']  # Replace with actual paths
svg_paths = ['frag0.svg', 'frag01_sol.svg', 'frag1.svg', 'frag2_sol.svg', 'frag2.svg', 
             'isolated_sol.svg', 'isolated.svg', 'occlusion1_sol.svg', 'occlusion1.svg', 
             'occlusion2.svg', 'occlusion2_sol.svg']  # Replace with actual paths

# Ensure the lists are of the same length
assert len(csv_paths) == len(svg_paths), "CSV paths and SVG paths lists must be of the same length."

# Process each CSV to generate the corresponding SVG
process_multiple_files(csv_paths, svg_paths)