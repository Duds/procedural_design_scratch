#!/usr/bin/env python3
"""Command-line tool for generating perforated moss poles."""

import argparse
from pathlib import Path
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.moss_pole import MossPolePipeline, MossPoleConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate perforated moss poles using space colonisation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Geometry parameters
    parser.add_argument(
        '--diameter',
        type=float,
        default=50.0,
        help='Outer diameter in mm'
    )
    parser.add_argument(
        '--wall-thickness',
        type=float,
        default=2.0,
        help='Wall thickness in mm'
    )
    parser.add_argument(
        '--height',
        type=float,
        default=200.0,
        help='Pole height in mm'
    )
    parser.add_argument(
        '--tunnel-radius',
        type=float,
        default=1.5,
        help='Perforation tunnel radius in mm'
    )
    
    # Pattern parameters
    parser.add_argument(
        '--attractors',
        type=int,
        default=2000,
        help='Number of space colonisation attractors'
    )
    parser.add_argument(
        '--influence-radius',
        type=float,
        default=16.0,
        help='Attractor influence radius in mm'
    )
    parser.add_argument(
        '--kill-radius',
        type=float,
        default=3.5,
        help='Attractor kill radius in mm'
    )
    parser.add_argument(
        '--step-size',
        type=float,
        default=1.8,
        help='Branch growth step size in mm'
    )
    
    # Structural parameters
    parser.add_argument(
        '--ribs',
        type=int,
        default=4,
        help='Number of structural ribs (no-cut zones)'
    )
    parser.add_argument(
        '--rib-width',
        type=float,
        default=10.0,
        help='Rib width in degrees'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    
    # Output parameters
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output file path'
    )
    parser.add_argument(
        '--format',
        choices=['stl', 'obj', 'ply', '3mf'],
        default='stl',
        help='Output file format'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print mesh statistics'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate mesh for 3D printing'
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = MossPoleConfig(
        outer_diameter=args.diameter,
        wall_thickness=args.wall_thickness,
        height=args.height,
        tunnel_radius=args.tunnel_radius,
        attractor_count=args.attractors,
        influence_radius=args.influence_radius,
        kill_radius=args.kill_radius,
        step_size=args.step_size,
        n_ribs=args.ribs,
        rib_width_degrees=args.rib_width,
        random_seed=args.random_seed,
    )
    
    # Create pipeline
    print("="*60)
    print("Moss Pole Generation Pipeline")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Diameter: {config.outer_diameter} mm")
    print(f"  Wall thickness: {config.wall_thickness} mm")
    print(f"  Height: {config.height} mm")
    print(f"  Tunnel radius: {config.tunnel_radius} mm")
    print(f"  Attractors: {config.attractor_count}")
    print(f"  Ribs: {config.n_ribs}")
    print()
    
    pipeline = MossPolePipeline(config)
    
    # Generate
    mesh = pipeline.generate()
    
    # Export mesh
    print(f"\nExporting mesh...")
    pipeline.export(args.output, file_format=args.format)
    
    # Statistics
    if args.stats:
        stats = pipeline.get_stats()
        print(f"\nMesh Statistics:")
        print(f"  Vertices: {stats['vertices']:,}")
        print(f"  Faces: {stats['faces']:,}")
        print(f"  Volume: {stats['volume_mm3']:.2f} mm³")
        print(f"  Surface area: {stats['surface_area_mm2']:.2f} mm²")
        print(f"  Open fraction: {stats['open_fraction']:.1%}")
        print(f"  Branches: {stats['n_branches']}")
        print(f"  Watertight: {stats['is_watertight']}")
        
        # Save stats to JSON
        stats_path = args.output.with_suffix('.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\nStatistics saved to {stats_path}")
    
    # Validation
    if args.validate:
        print(f"\nValidating mesh...")
        validation = pipeline.validate()
        print(f"  Watertight: {'✓' if validation['is_watertight'] else '✗'}")
        print(f"  Winding consistent: {'✓' if validation['is_winding_consistent'] else '✗'}")
        print(f"  Degenerate faces: {'✗' if validation['has_degenerate_faces'] else '✓'}")
        print(f"  Valid for 3D printing: {'✓' if validation['is_valid'] else '✗'}")
    
    print(f"\n{'='*60}")
    print("✓ Generation complete!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()

