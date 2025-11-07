#!/usr/bin/env python3
"""CLI tool for processing template meshes with procedural algorithms."""

import argparse
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.mesh_processor import MeshProcessorPipeline, MeshProcessorConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Apply Gray-Scott patterns to template meshes',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'template',
        type=Path,
        help='Path to template STL file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output file path'
    )
    parser.add_argument(
        '--pattern',
        choices=['spots', 'stripes', 'waves', 'holes', 'custom'],
        default='spots',
        help='Pattern type preset'
    )
    parser.add_argument(
        '--displacement',
        type=float,
        default=8.0,
        help='Displacement amplitude in mm'
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
        default=7,
        help='Number of seed patches'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--taper-top',
        type=float,
        default=0.3,
        help='Top taper amount (0.0-1.0)'
    )
    parser.add_argument(
        '--taper-bottom',
        type=float,
        default=0.15,
        help='Bottom taper amount (0.0-1.0)'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Show pattern visualization'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print statistics'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate mesh for 3D printing'
    )
    parser.add_argument(
        '--format',
        choices=['stl', 'obj', 'ply', '3mf'],
        default='stl',
        help='Output file format'
    )
    
    args = parser.parse_args()
    
    # Check template exists
    if not args.template.exists():
        print(f"❌ Error: Template file not found: {args.template}")
        sys.exit(1)
    
    # Create configuration
    config = MeshProcessorConfig(
        template_path=args.template,
        displacement_amplitude=args.displacement,
        field_resolution=args.resolution,
        simulation_steps=args.steps,
        n_seeds=args.seeds,
        pattern_type=args.pattern,
        random_seed=args.random_seed,
        taper_top=args.taper_top,
        taper_bottom=args.taper_bottom
    )
    
    # Run pipeline
    print("="*60)
    print("Template Mesh Processor")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Template: {config.template_path.name}")
    print(f"  Pattern: {config.pattern_type}")
    print(f"  Displacement: {config.displacement_amplitude} mm")
    print(f"  Resolution: {config.field_resolution}")
    print(f"  Steps: {config.simulation_steps}")
    print()
    
    pipeline = MeshProcessorPipeline(config)
    
    # Generate
    mesh = pipeline.generate()
    
    # Visualize if requested
    if args.visualize:
        viz_path = args.output.with_suffix('.png')
        print(f"\nSaving visualization to {viz_path}")
        pipeline.visualize_field(save_path=viz_path)
    
    # Export
    print(f"\nExporting mesh...")
    pipeline.export(args.output, file_format=args.format)
    
    # Stats
    if args.stats:
        stats = pipeline.get_stats()
        print(f"\nMesh Statistics:")
        print(f"  Template:")
        print(f"    Vertices: {stats['template_vertices']:,}")
        print(f"    Faces: {stats['template_faces']:,}")
        print(f"    Watertight: {stats['template_watertight']}")
        print(f"  Output:")
        print(f"    Vertices: {stats['output_vertices']:,}")
        print(f"    Faces: {stats['output_faces']:,}")
        print(f"    Volume: {stats['volume_mm3']:.2f} mm³")
        print(f"    Surface area: {stats['surface_area_mm2']:.2f} mm²")
        print(f"    Watertight: {stats['is_watertight']}")
        
        # Save stats to JSON
        stats_path = args.output.with_suffix('.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\n  ✓ Statistics saved to {stats_path}")
    
    # Validation
    if args.validate:
        print(f"\nValidating mesh...")
        validation = pipeline.validate()
        print(f"  Watertight: {'✓' if validation['is_watertight'] else '✗'}")
        print(f"  Winding consistent: {'✓' if validation['is_winding_consistent'] else '✗'}")
        print(f"  Degenerate faces: {'✗' if validation['has_degenerate_faces'] else '✓'}")
        print(f"  Valid for 3D printing: {'✓' if validation['is_valid'] else '✗'}")
    
    print(f"\n{'='*60}")
    print("✓ Processing complete!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()

