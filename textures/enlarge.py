#!/usr/bin/env python3
"""
Texture Upscaler Script
Scales 16x16 PNG textures to 512x512 without blur using nearest-neighbor interpolation
"""

import os
import sys
from pathlib import Path
from PIL import Image

def upscale_texture(png_path, target_size=(512, 512)):
    """
    Upscale a texture using nearest-neighbor interpolation (no blur)
    """
    try:
        # Open the image
        with Image.open(png_path) as img:
            print(f"Upscaling {png_path.name} from {img.size} to {target_size}")
            
            # Use NEAREST (nearest-neighbor) resampling for crisp pixel scaling
            upscaled = img.resize(target_size, Image.NEAREST)
            
            # Save over the original file
            upscaled.save(png_path)
            print(f"Overwritten: {png_path}")
            return True
                
    except Exception as e:
        print(f"Error processing {png_path}: {e}")
        return False

def main():
    # Get directory path from command line argument or use current directory
    if len(sys.argv) > 1:
        texture_dir = Path(sys.argv[1])
    else:
        texture_dir = Path.cwd()
    
    # Check if directory exists
    if not texture_dir.exists():
        print(f"Error: Directory '{texture_dir}' does not exist!")
        sys.exit(1)
    
    if not texture_dir.is_dir():
        print(f"Error: '{texture_dir}' is not a directory!")
        sys.exit(1)
    
    # Create output directory
    print(f"Processing PNG files in: {texture_dir}")
    
    # Find all PNG files
    png_files = list(texture_dir.glob("*.png"))
    
    if not png_files:
        print(f"No PNG files found in '{texture_dir}'")
        return
    
    print(f"Found {len(png_files)} PNG files")
    print("Upscaling textures...\n")
    
    # Track statistics
    processed_count = 0
    
    # Process each PNG file
    for png_file in png_files:
        if upscale_texture(png_file):
            processed_count += 1
    
    print(f"\nCompleted!")
    print(f"✓ Processed: {processed_count} textures")
    print(f"All files have been overwritten with 512x512 versions")

if __name__ == "__main__":
    main()