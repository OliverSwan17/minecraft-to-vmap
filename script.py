#!/usr/bin/env python3
import sys
import re
import uuid
import argparse
import hashlib
import os
import subprocess

def generate_new_uid():
    return str(uuid.uuid4())

def generate_new_reference_id():
    import random
    return f"0x{random.randint(0, 2**64-1):016x}"

def replace_uids_in_content(content):
    elementid_pattern = r'"id" "elementid" "([a-f0-9-]+)"'
    elementids = re.findall(elementid_pattern, content)
    
    uid_mapping = {}
    for old_uid in set(elementids):
        uid_mapping[old_uid] = generate_new_uid()
    
    for old_uid, new_uid in uid_mapping.items():
        content = content.replace(f'"id" "elementid" "{old_uid}"', f'"id" "elementid" "{new_uid}"')
    
    reference_pattern = r'"referenceID" "uint64" "(0x[a-f0-9]+)"'
    references = re.findall(reference_pattern, content)
    
    for old_ref in set(references):
        if old_ref != "0x0":
            new_ref = generate_new_reference_id()
            content = content.replace(f'"referenceID" "uint64" "{old_ref}"', f'"referenceID" "uint64" "{new_ref}"')
    
    return content

def update_origin_in_mesh(mesh_content, x, y, z):
    origin_pattern = r'"origin" "vector3" "[^"]+"'
    new_origin = f'"origin" "vector3" "{x} {y} {z}"'
    return re.sub(origin_pattern, new_origin, mesh_content)

def update_node_id_in_mesh(mesh_content, new_node_id):
    node_id_pattern = r'"nodeID" "int" "\d+"'
    new_node_id_str = f'"nodeID" "int" "{new_node_id}"'
    return re.sub(node_id_pattern, new_node_id_str, mesh_content)

def read_coordinates_from_file(filename):
    coordinates = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 3:
                    coordinates.append((float(parts[0]), float(parts[1]), float(parts[2])))
    return coordinates

def insert_meshes_after_nav_data(template_content, mesh_insertions):
    nav_data_end_pattern = r'(\s*"editorOnly" "bool" "0"\s*\}\s*)(,?\s*)\]'
    match = re.search(nav_data_end_pattern, template_content)
    
    if not match:
        return template_content
    
    insertion_point = match.end() - 1
    all_meshes = ''.join(mesh_insertions)
    
    return (template_content[:insertion_point] + 
            all_meshes + 
            template_content[insertion_point:])

def generate_output_filename(coordinates):
    coords_string = '_'.join([f"{x}_{y}_{z}" for x, y, z in coordinates])
    hash_object = hashlib.md5(coords_string.encode())
    hash_hex = hash_object.hexdigest()[:12]
    return f"{hash_hex}.dmx"

def main():
    parser = argparse.ArgumentParser(description='Generate VMAP world with multiple meshes from coordinates')
    parser.add_argument('--template', default='config/template.dmx')
    parser.add_argument('--mesh', default='config/mesh.dmx')
    parser.add_argument('--coords', default='config/squares.txt')
    parser.add_argument('--output')
    
    args = parser.parse_args()
    
    try:
        output_dir_dmx = 'out/dmx'
        output_dir_vmap = 'out/vmap'
        os.makedirs(output_dir_dmx, exist_ok=True)
        os.makedirs(output_dir_vmap, exist_ok=True)
        
        with open(args.template, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        with open(args.mesh, 'r', encoding='utf-8') as f:
            mesh_template = f.read()
        
        coordinates = read_coordinates_from_file(args.coords)
        
        template_content = replace_uids_in_content(template_content)
        
        mesh_insertions = []
        base_node_id = 200
        
        for i, (x, y, z) in enumerate(coordinates):
            mesh_copy = mesh_template
            mesh_copy = replace_uids_in_content(mesh_copy)
            mesh_copy = update_origin_in_mesh(mesh_copy, x, y, z)
            mesh_copy = update_node_id_in_mesh(mesh_copy, base_node_id + i)
            mesh_insertions.append(f",\n\t\t\t{mesh_copy}")
        
        final_content = insert_meshes_after_nav_data(template_content, mesh_insertions)
        
        if args.output:
            output_filename = os.path.join(output_dir_dmx, args.output)
        else:
            hashed_filename = generate_output_filename(coordinates)
            output_filename = os.path.join(output_dir_dmx, hashed_filename)
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # Convert to binary vmap
        base_name = os.path.splitext(os.path.basename(output_filename))[0]
        vmap_output = os.path.join(output_dir_vmap, f"{base_name}.vmap")
        
        subprocess.run(['dmxconvert', '-i', output_filename, '-o', vmap_output, '-oe', 'binary'], check=True)
        
        print(f"Success: {output_filename} -> {vmap_output}")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()