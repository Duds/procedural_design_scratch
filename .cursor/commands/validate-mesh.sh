#!/bin/bash
# Validate exported mesh files for 3D printing and quality

set -e

if [ -z "$1" ]; then
    echo "Usage: validate-mesh.sh <mesh-file.stl>"
    exit 1
fi

MESH_FILE="$1"

if [ ! -f "$MESH_FILE" ]; then
    echo "Error: Mesh file not found: $MESH_FILE"
    exit 1
fi

# Create temporary Python script for validation
SCRIPT=$(cat <<'EOF'
import sys
import trimesh
import numpy as np

mesh_path = sys.argv[1]
print(f"Validating mesh: {mesh_path}")
print("=" * 60)

try:
    mesh = trimesh.load(mesh_path)
    
    # Basic properties
    print(f"\n📊 Basic Properties:")
    print(f"   Vertices: {len(mesh.vertices):,}")
    print(f"   Faces: {len(mesh.faces):,}")
    print(f"   Edges: {len(mesh.edges):,}")
    
    # Bounding box
    bounds = mesh.bounds
    size = bounds[1] - bounds[0]
    print(f"\n📏 Dimensions (mm):")
    print(f"   X: {size[0]:.2f}")
    print(f"   Y: {size[1]:.2f}")
    print(f"   Z: {size[2]:.2f}")
    print(f"   Volume: {mesh.volume:.2f} mm³")
    print(f"   Surface Area: {mesh.area:.2f} mm²")
    
    # Quality checks
    print(f"\n✓ Quality Checks:")
    
    is_valid = True
    
    # Watertight check
    if mesh.is_watertight:
        print("   ✓ Mesh is watertight")
    else:
        print("   ✗ Mesh is NOT watertight - may have holes")
        is_valid = False
    
    # Winding check
    if mesh.is_winding_consistent:
        print("   ✓ Face winding is consistent")
    else:
        print("   ✗ Face winding is inconsistent")
        is_valid = False
    
    # Check for degenerate faces
    degenerate = np.isclose(mesh.area_faces, 0).sum()
    if degenerate == 0:
        print("   ✓ No degenerate faces")
    else:
        print(f"   ⚠ {degenerate} degenerate faces found")
        is_valid = False
    
    # Check for duplicate vertices
    unique_verts = len(np.unique(mesh.vertices, axis=0))
    duplicates = len(mesh.vertices) - unique_verts
    if duplicates == 0:
        print("   ✓ No duplicate vertices")
    else:
        print(f"   ⚠ {duplicates} duplicate vertices")
    
    # Check for self-intersections (expensive, skip for large meshes)
    if len(mesh.faces) < 50000:
        if mesh.is_volume:
            print("   ✓ Valid volume (likely no self-intersections)")
        else:
            print("   ⚠ May have self-intersections or is not a volume")
    else:
        print("   ⊘ Self-intersection check skipped (mesh too large)")
    
    # 3D Printing checks
    print(f"\n🖨️  3D Printing Checks:")
    
    # Check minimum wall thickness (assume 1mm minimum)
    print("   ⊘ Wall thickness check not implemented")
    
    # Check for overhangs (rough estimate)
    normals = mesh.face_normals
    downward_facing = normals[:, 2] < -0.7  # Roughly >45° overhang
    overhang_pct = (downward_facing.sum() / len(normals)) * 100
    if overhang_pct < 20:
        print(f"   ✓ Minimal overhangs ({overhang_pct:.1f}% of faces)")
    else:
        print(f"   ⚠ Significant overhangs ({overhang_pct:.1f}% of faces) - may need supports")
    
    # Final verdict
    print("\n" + "=" * 60)
    if is_valid:
        print("✓ Mesh is valid and ready for export!")
        sys.exit(0)
    else:
        print("⚠ Mesh has issues that should be addressed")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Error validating mesh: {e}")
    sys.exit(2)
EOF
)

# Run validation
python3 -c "$SCRIPT" "$MESH_FILE"

