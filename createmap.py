import argparse

import gpxpy
import gpxpy.gpx
import prettymaps
import matplotlib.pyplot as plt

import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic


def calculate_enclosing_circle(gpx_file_path):
    # Parse the GPX file
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Extract the coordinates from the GPX file
    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))

    # Calculate the center of the bounding box
    min_lat = min(coordinates, key=lambda x: x[0])[0]
    max_lat = max(coordinates, key=lambda x: x[0])[0]
    min_lon = min(coordinates, key=lambda x: x[1])[1]
    max_lon = max(coordinates, key=lambda x: x[1])[1]

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    center = (center_lat, center_lon)

    # Calculate the radius as the maximum distance from the center to any point
    radius = max(geodesic(center, coord).meters for coord in coordinates)

    return center, radius


def create_map_from_gpx(gpx_file_path):
    # Parse the GPX file
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Extract the coordinates from the GPX file
    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))

    # Create the map using prettymaps
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    center, radius = calculate_enclosing_circle(gpx_file_path)

    layers = prettymaps.plot(ax=ax, query=f"{center[0]}, {center[1]}", radius=radius)

    output_image_path = gpx_file_path.replace(".gpx", "_map.png")
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    # Create the map using prettymaps
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    lats, lons = zip(*coordinates)
    ax.plot(lons, lats, color='red', linewidth=2)
    output_image_path = gpx_file_path.replace(".gpx", "_track.png")
    #plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a map from a GPX file.")
    parser.add_argument("gpx_file_path", type=str, help="Path to the input GPX file.")
    args = parser.parse_args()

    create_map_from_gpx(args.gpx_file_path)

    # TODO: overlay doesn't work,
    # TODO: try bounding box instead of circle
    # TODO: add track to the map
    # TODO: https://github.com/marceloprates/prettymaps/issues/8
    # TODO: try - https://github.com/ThomasParistech/pretty-gpx
    # TODO: own implementation of prettymaps that works with newer python
