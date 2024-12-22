from PIL import Image

def overlay_images(map_image_path, track_image_path, output_image_path, alpha=0.3):
    # Open the map and track images
    map_image = Image.open(map_image_path).convert("RGBA")
    track_image = Image.open(track_image_path).convert("RGBA")
    
    # Resize track image to match map image size
    track_image = track_image.resize(map_image.size, Image.LANCZOS)
    
    # Blend the images
    blended_image = Image.blend(map_image, track_image, alpha=alpha)
    
    # Save the blended image
    blended_image.save(output_image_path)

# Example usage
map_image_path = 'Blue_Ridge_Half_Marathon_map.png'
track_image_path = 'Blue_Ridge_Half_Marathon_track.png'
output_image_path = 'Blue_Ridge_Half_Marathon_overlay.png'
overlay_images(map_image_path, track_image_path, output_image_path)