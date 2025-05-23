#!/usr/bin/env python3
"""
Texture Material Generator
Loops through a directory of .png textures and creates corresponding material files
"""

import os
import sys
from pathlib import Path

def create_material_file(texture_name, output_dir):
    """Create a material file for the given texture name"""
    
    material_content = f"""// THIS FILE IS AUTO-GENERATED
Layer0
{{
	shader "csgo_complex.vfx"
	//---- Ambient Occlusion ----
	TextureAmbientOcclusion "materials/default/default_ao.tga"
	//---- Color ----
	g_flModelTintAmount "1.000"
	g_flTexCoordRotation "0.000"
	g_nScaleTexCoordUByModelScaleAxis "0" // None
	g_nScaleTexCoordVByModelScaleAxis "0" // None
	g_vColorTint "[1.000000 1.000000 1.000000 0.000000]"
	g_vTexCoordCenter "[0.500 0.500]"
	g_vTexCoordOffset "[0.000 0.000]"
	g_vTexCoordScale "[1.000 1.000]"
	g_vTexCoordScrollSpeed "[0.000 0.000]"
	TextureColor "materials/{texture_name}.png"
	//---- Fog ----
	g_bFogEnabled "1"
	//---- Lighting ----
	g_flMetalness "0.000"
	TextureRoughness "materials/default/default_rough.tga"
	//---- Normal Map ----
	TextureNormal "materials/default/default_normal.tga"
	//---- Texture Address Mode ----
	g_nTextureAddressModeU "0" // Wrap
	g_nTextureAddressModeV "0" // Wrap
	VariableState
	{{
		"Ambient Occlusion"
		{{
		}}
		"Color"
		{{
		}}
		"Fog"
		{{
		}}
		"Lighting"
		{{
			"Roughness" 0
			"Metalness" 0
		}}
		"Normal Map"
		{{
		}}
		"Texture Address Mode"
		{{
		}}
	}}
}}"""
    
    # Create output file path
    output_file = output_dir / f"{texture_name}.vmat"
    
    # Write the material file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(material_content)
    
    print(f"Created: {output_file}")

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
    
    # Create output directory (same as input directory by default)
    output_dir = texture_dir
    
    # Find all PNG files
    png_files = list(texture_dir.glob("*.png"))
    
    if not png_files:
        print(f"No PNG files found in '{texture_dir}'")
        return
    
    print(f"Found {len(png_files)} PNG files in '{texture_dir}'")
    print("Generating material files...")
    
    # Process each PNG file
    for png_file in png_files:
        # Get filename without extension
        texture_name = png_file.stem
        
        # Create the material file
        create_material_file(texture_name, output_dir)
    
    print(f"\nCompleted! Generated {len(png_files)} material files.")

if __name__ == "__main__":
    main()