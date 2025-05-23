#!/usr/bin/env python3
"""
Minecraft World Block Reader - Working Version
Based on the approach from your provided code
"""

import anvil
import os

class WorkingMinecraftReader:
    def __init__(self, world_path: str = "minecraft_saves/cs2_test"):
        """
        Initialise the world reader
        
        Args:
            world_path: Path to the Minecraft world folder
        """
        self.world_directory = os.path.join(world_path, "region")
        self.region_cache = {}  # Cache for region files
        self.chunk_cache = {}   # Cache for chunks
        
        if not os.path.exists(self.world_directory):
            raise FileNotFoundError(f"Region folder not found at {self.world_directory}")
            
        print(f"Initialised world reader for: {world_path}")
    
    def get_block(self, x: int, y: int, z: int) -> str:
        """
        Get the block at world coordinates (x, y, z)
        
        Args:
            x, y, z: World block coordinates
            
        Returns:
            Block name as string
        """
        try:
            # Calculate chunk coordinates
            chunk_x = x >> 4  # x // 16
            chunk_z = z >> 4  # z // 16
            
            # Calculate block position within chunk
            block_x = x & 15  # x % 16
            block_z = z & 15  # z % 16
            
            # Get the chunk (with caching)
            chunk = self._get_chunk(chunk_x, chunk_z)
            if chunk is None:
                return "minecraft:air"  # Default to air if chunk doesn't exist
            
            # Get the block
            block = chunk.get_block(block_x, y, block_z)
            return block.id
            
        except Exception as e:
            print(f"Error reading block at ({x}, {y}, {z}): {e}")
            return "minecraft:air"
    
    def _get_chunk(self, chunk_x: int, chunk_z: int):
        """Get chunk with caching, following the working example's approach"""
        
        # Check if chunk is already cached
        if (chunk_x, chunk_z) in self.chunk_cache:
            return self.chunk_cache[(chunk_x, chunk_z)]
        
        # Determine which region file this chunk belongs to
        region_x = chunk_x // 32
        region_z = chunk_z // 32
        
        # Get the region (with caching)
        region = self._get_region(region_x, region_z)
        if region is None:
            return None
        
        try:
            # Get the chunk using the same method as the working code
            chunk = region.get_chunk(chunk_x % 32, chunk_z % 32)
            self.chunk_cache[(chunk_x, chunk_z)] = chunk  # Cache the chunk
            return chunk
            
        except Exception as e:
            print(f"Error loading chunk at ({chunk_x}, {chunk_z}): {e}")
            return None
    
    def _get_region(self, region_x: int, region_z: int):
        """Get region with caching"""
        
        # Check if region is already cached
        if (region_x, region_z) in self.region_cache:
            return self.region_cache[(region_x, region_z)]
        
        # Build region file path
        region_file = os.path.join(self.world_directory, f"r.{region_x}.{region_z}.mca")
        
        try:
            # Load region using the same method as the working code
            region = anvil.Region.from_file(region_file)
            self.region_cache[(region_x, region_z)] = region  # Cache the region
            return region
            
        except Exception as e:
            print(f"Error loading region file: {region_file}. Exception: {e}")
            return None
    
    def get_multiple_blocks(self, coordinates: list) -> dict:
        """
        Get multiple blocks at once
        
        Args:
            coordinates: List of (x, y, z) tuples
            
        Returns:
            Dictionary mapping coordinates to block names
        """
        results = {}
        for x, y, z in coordinates:
            block = self.get_block(x, y, z)
            results[(x, y, z)] = block
        
        return results
    
    def list_available_regions(self):
        """List all available region files"""
        if not os.path.exists(self.world_directory):
            print("Region path does not exist")
            return
        
        region_files = [f for f in os.listdir(self.world_directory) if f.endswith('.mca')]
        print(f"Found {len(region_files)} region files:")
        for file in sorted(region_files):
            print(f"  {file}")
    
    def scan_area(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int):
        """
        Scan an area and return all non-air blocks
        
        Args:
            x1, y1, z1: Start coordinates
            x2, y2, z2: End coordinates
            
        Returns:
            Dictionary of coordinates to block types
        """
        blocks = {}
        
        # All possible air block types to filter out
        air_blocks = {
            "minecraft:air", 
            "minecraft:cave_air", 
            "minecraft:void_air",
            "air", 
            "cave_air", 
            "void_air"
        }
        
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    block = self.get_block(x, y, z)
                    # Only include if it's NOT any type of air block
                    if block not in air_blocks:
                        blocks[(x, y, z)] = block
        
        return blocks

def main():
    try:
        reader = WorkingMinecraftReader()  # Uses default path
        
        # List available regions
        print("Available regions:")
        reader.list_available_regions()
        
        print("\nEnter scan command in format: scan x1 y1 z1 x2 y2 z2")
        print("Example: scan 0 128 0 16 150 16")
        
        user_input = input("Command: ").strip()
        
        if user_input.startswith('scan '):
            # Parse scan command
            coords = user_input[5:].split()
            if len(coords) != 6:
                print("Please enter exactly 6 coordinates for scan: x1 y1 z1 x2 y2 z2")
                return
            
            x1, y1, z1, x2, y2, z2 = map(int, coords)
            print(f"Scanning area from ({x1}, {y1}, {z1}) to ({x2}, {y2}, {z2})...")
            
            blocks = reader.scan_area(x1, y1, z1, x2, y2, z2)
            
            if blocks:
                print(f"Found {len(blocks)} non-air blocks")
                
                # Generate filename with hash underscore
                import hashlib
                scan_string = f"{x1}_{y1}_{z1}_{x2}_{y2}_{z2}"
                hash_hex = hashlib.md5(scan_string.encode()).hexdigest()[:8]
                filename = f"minecraft_out_{hash_hex}.txt"
                
                # Write to file with coordinates multiplied by 48
                with open(filename, 'w') as f:
                    for (x, y, z), block in blocks.items():
                        scaled_x = x * 48
                        scaled_y = y * 48
                        scaled_z = z * 48
                        f.write(f"{scaled_z} {scaled_x} {scaled_y}\n")
                
                print(f"Saved {len(blocks)} block positions to {filename}")
                print(f"Coordinates scaled by 48x")
                
                # Show first few entries as preview
                print("\nFirst few entries:")
                count = 0
                for (x, y, z), block in blocks.items():
                    if count >= 5:
                        break
                    scaled_x = x * 48
                    scaled_y = y * 48
                    scaled_z = z * 48
                    print(f"  {scaled_z} {scaled_x} {scaled_y}")
                    count += 1
                
                if len(blocks) > 5:
                    print(f"  ... and {len(blocks) - 5} more")
                    
            else:
                print("No non-air blocks found in the specified area")
        else:
            print("Please start your command with 'scan'")
    
    except ValueError:
        print("Please enter valid integer coordinates")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the world path 'minecraft_saves/cs2_test' exists and contains a 'region' folder")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()