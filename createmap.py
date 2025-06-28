import argparse
import os
from pathlib import Path
from typing import List, Tuple, Optional

import gpxpy
import gpxpy.gpx
import prettymaps
import matplotlib.pyplot as plt
from geopy.distance import geodesic


class GPXMapGenerator:
    """Generates maps from GPX files using prettymaps."""
    
    def __init__(self, dpi: int = 300, figure_size: Tuple[int, int] = (10, 10)):
        self.dpi = dpi
        self.figure_size = figure_size
    
    def parse_gpx_file(self, gpx_file_path: str) -> gpxpy.gpx.GPX:
        """Parse GPX file and return GPX object."""
        if not os.path.exists(gpx_file_path):
            raise FileNotFoundError(f"GPX file not found: {gpx_file_path}")
        
        try:
            with open(gpx_file_path, 'r', encoding='utf-8') as gpx_file:
                return gpxpy.parse(gpx_file)
        except Exception as e:
            raise ValueError(f"Failed to parse GPX file: {e}")
    
    def extract_coordinates(self, gpx: gpxpy.gpx.GPX) -> List[Tuple[float, float]]:
        """Extract all coordinates from GPX tracks."""
        coordinates = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coordinates.append((point.latitude, point.longitude))
        
        if not coordinates:
            raise ValueError("No coordinates found in GPX file")
        
        return coordinates
    
    def calculate_map_bounds(self, coordinates: List[Tuple[float, float]]) -> Tuple[Tuple[float, float], float]:
        """Calculate center point and radius for map bounds."""
        if not coordinates:
            raise ValueError("No coordinates provided")
        
        lats, lons = zip(*coordinates)
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        center = (center_lat, center_lon)
        
        radius = max(geodesic(center, coord).meters for coord in coordinates)
        
        return center, radius
    
    def create_base_map(self, center: Tuple[float, float], radius: float) -> Tuple[plt.Figure, plt.Axes]:
        """Create base map using prettymaps."""
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        try:
            layers = prettymaps.plot(ax=ax, query=f"{center[0]}, {center[1]}", radius=radius)
        except Exception as e:
            print(f"Warning: Failed to create prettymaps background: {e}")
            ax.set_xlim(center[1] - 0.01, center[1] + 0.01)
            ax.set_ylim(center[0] - 0.01, center[0] + 0.01)
        
        return fig, ax
    
    def overlay_track(self, ax: plt.Axes, coordinates: List[Tuple[float, float]], 
                     color: str = 'red', linewidth: float = 3, alpha: float = 0.8) -> None:
        """Overlay GPS track on the map."""
        if not coordinates:
            return
        
        lats, lons = zip(*coordinates)
        ax.plot(lons, lats, color=color, linewidth=linewidth, alpha=alpha, zorder=10)
    
    def create_map_from_gpx(self, gpx_file_path: str, overlay_track: bool = True, 
                           output_path: Optional[str] = None) -> str:
        """Create a complete map from GPX file with optional track overlay."""
        gpx = self.parse_gpx_file(gpx_file_path)
        coordinates = self.extract_coordinates(gpx)
        center, radius = self.calculate_map_bounds(coordinates)
        
        if output_path is None:
            output_path = str(Path(gpx_file_path).with_suffix('').with_name(
                Path(gpx_file_path).stem + '_map.png'
            ))
        
        # Create base map first (similar to original approach)
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        try:
            layers = prettymaps.plot(ax=ax, query=f"{center[0]}, {center[1]}", radius=radius)
            
            # If overlay_track is True, add the track on top
            if overlay_track:
                self.overlay_track(ax, coordinates)
                
        except Exception as e:
            print(f"Warning: Failed to create prettymaps background: {e}")
            # Fallback: create a simple coordinate plot
            ax.set_xlim(center[1] - 0.01, center[1] + 0.01)
            ax.set_ylim(center[0] - 0.01, center[0] + 0.01)
            if overlay_track:
                self.overlay_track(ax, coordinates)
        
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        return output_path
    
    def create_track_only(self, gpx_file_path: str, output_path: Optional[str] = None) -> str:
        """Create a track-only visualization."""
        gpx = self.parse_gpx_file(gpx_file_path)
        coordinates = self.extract_coordinates(gpx)
        
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        lats, lons = zip(*coordinates)
        ax.plot(lons, lats, color='red', linewidth=2)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('GPS Track')
        
        if output_path is None:
            output_path = str(Path(gpx_file_path).with_suffix('').with_name(
                Path(gpx_file_path).stem + '_track.png'
            ))
        
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        return output_path


def main():
    """Main function to handle command line arguments and generate maps."""
    parser = argparse.ArgumentParser(
        description="Create beautiful maps from GPX files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python createmap.py track.gpx                    # Create map with track overlay
  python createmap.py track.gpx --no-overlay       # Create map without track
  python createmap.py track.gpx --track-only       # Create track-only visualization
  python createmap.py track.gpx --output custom.png # Specify output filename
        """
    )
    
    parser.add_argument(
        "gpx_file_path", 
        type=str, 
        help="Path to the input GPX file"
    )
    
    parser.add_argument(
        "--no-overlay", 
        action="store_true", 
        help="Create map without track overlay"
    )
    
    parser.add_argument(
        "--track-only", 
        action="store_true", 
        help="Create track-only visualization (no map background)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file path (default: input_map.png or input_track.png)"
    )
    
    parser.add_argument(
        "--dpi", 
        type=int, 
        default=300, 
        help="Output resolution in DPI (default: 300)"
    )
    
    parser.add_argument(
        "--size", 
        type=int, 
        nargs=2, 
        default=[10, 10], 
        metavar=("WIDTH", "HEIGHT"), 
        help="Figure size in inches (default: 10 10)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = GPXMapGenerator(dpi=args.dpi, figure_size=tuple(args.size))
        
        if args.track_only:
            output_path = generator.create_track_only(args.gpx_file_path, args.output)
            print(f"Track visualization saved to: {output_path}")
        else:
            overlay_track = not args.no_overlay
            output_path = generator.create_map_from_gpx(
                args.gpx_file_path, 
                overlay_track=overlay_track, 
                output_path=args.output
            )
            print(f"Map {'with track overlay' if overlay_track else 'without overlay'} saved to: {output_path}")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
