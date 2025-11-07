#!/usr/bin/env python3
"""Command-line tool for generating Gray-Scott patterned vases."""

import argparse
from pathlib import Path
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.vase import VasePipeline, VaseConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Gray-Scott patterned vases',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Geometry parameters
    parser.add_argument(
        '--height',
        type=float,
        default=150.0,
        help='Vase height in mm'
    )
    parser.add_argument(
        '--base-size',
        type=float,
        default=80.0,
        help='Base dimension in mm'
    )
    parser.add_argument(
        '--profile',
        choices=['circle', 'square', 'hexagon'],
        default='square',
        help='Base profile shape'
    )
    parser.add_argument(
        '--displacement',
        type=float,
        default=6.0,
        help='Maximum displacement amplitude in mm'
    )
    parser.add_argument(
        '--corner-radius',
        type=float,
        default=20.0,
        help='Corner radius for square profile in mm'
    )
    
    # Pattern parameters
    parser.add_argument(
        '--pattern',
        choices=['spots', 'stripes', 'waves', 'holes', 'custom'],
        default='spots',
        help='Pattern type preset'
    )
    parser.add_argument(
        '--feed-rate',
        type=float,
        help='Feed rate (F) for custom pattern (0.01-0.08)'
    )
    parser.add_argument(
        '--kill-rate',
        type=float,
        help='Kill rate (k) for custom pattern (0.045-0.065)'
    )
    parser.add_argument(
        '--resolution',
        type=int,
        default=256,
        help='Field resolution'
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=10000,
        help='Simulation steps'
    )
    parser.add_argument(
        '--seeds',
        type=int,
        default=5,
        help='Number of initial seed patches'
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
        '--visualize',
        action='store_true',
        help='Save pattern visualization'
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
    config = VaseConfig(
        height=args.height,
        base_size=args.base_size,
        profile_type=args.profile,
        displacement_amplitude=args.displacement,
        field_resolution=args.resolution,
        simulation_steps=args.steps,
        n_seeds=args.seeds,
        pattern_type=args.pattern,
        random_seed=args.random_seed,
        corner_radius=args.corner_radius,
    )
    
    # Create pipeline
    print("="*60)
    print("Vase Generation Pipeline")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Height: {config.height} mm")
    print(f"  Base size: {config.base_size} mm")
    print(f"  Profile: {config.profile_type}")
    print(f"  Pattern: {config.pattern_type}")
    print(f"  Resolution: {config.field_resolution}")
    print(f"  Steps: {config.simulation_steps}")
    print()
    
    pipeline = VasePipeline(config)
    
    # Generate
    mesh = pipeline.generate()
    
    # Visualize if requested
    if args.visualize:
        viz_path = args.output.with_suffix('.png')
        print(f"\nSaving visualization to {viz_path}")
        pipeline.visualize_field(save_path=viz_path)
    
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

