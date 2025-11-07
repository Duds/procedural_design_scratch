"""Command-line interface commands."""

import click
from pathlib import Path
import json

from ..algorithms.gray_scott import GrayScottConfig
from ..algorithms.space_colonization import SpaceColonizationConfig
from ..pipelines.vase import VasePipeline, VaseConfig
from ..pipelines.moss_pole import MossPolePipeline, MossPoleConfig
from ..geometry.mesh_ops import validate_mesh
import trimesh


@click.group()
@click.version_option()
def cli():
    """Procedural Design CLI - Generate organic 3D structures."""
    pass


@cli.command()
@click.option('--feed', '-f', default=0.055, type=float, help='Gray-Scott feed rate')
@click.option('--kill', '-k', default=0.062, type=float, help='Gray-Scott kill rate')
@click.option('--height', '-h', default=200.0, type=float, help='Vase height (mm)')
@click.option('--size', '-s', default=100.0, type=float, help='Base size (mm)')
@click.option('--profile', '-p', type=click.Choice(['square', 'circular']), default='square', help='Cross-section profile')
@click.option('--amplitude', '-a', default=8.0, type=float, help='Displacement amplitude (mm)')
@click.option('--resolution', '-r', default=256, type=int, help='Field resolution')
@click.option('--steps', default=20000, type=int, help='Simulation steps')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output STL file')
@click.option('--visualize/--no-visualize', default=False, help='Show field visualization')
def generate_vase(feed, kill, height, size, profile, amplitude, resolution, steps, output, visualize):
    """Generate a reaction-diffusion textured vase.
    
    Example:
        procedural-design generate-vase -f 0.055 -k 0.062 -o vase.stl
    """
    click.echo("🎨 Generating vase with Gray-Scott pattern...")
    click.echo(f"   Feed: {feed}, Kill: {kill}")
    click.echo(f"   Dimensions: {size}mm × {height}mm")
    
    # Create configuration
    gs_config = GrayScottConfig(
        feed_rate=feed,
        kill_rate=kill,
        Du=0.16,
        Dv=0.08
    )
    
    config = VaseConfig(
        height=height,
        base_size=size,
        profile_type=profile,
        displacement_amplitude=amplitude,
        gray_scott_config=gs_config,
        field_resolution=resolution,
        simulation_steps=steps
    )
    
    # Generate
    pipeline = VasePipeline(config)
    
    if visualize:
        click.echo("📊 Visualizing field...")
        pipeline.visualize_field()
    
    click.echo("🔨 Building mesh...")
    output_path = Path(output)
    pipeline.export_with_metadata(output_path)
    
    # Validate
    mesh = trimesh.load(output_path)
    results = validate_mesh(mesh)
    
    click.echo(f"\n✅ Generated: {output_path}")
    click.echo(f"   Vertices: {results['num_vertices']:,}")
    click.echo(f"   Faces: {results['num_faces']:,}")
    click.echo(f"   Watertight: {'Yes' if results['is_watertight'] else 'No'}")
    
    if not results['is_valid']:
        click.echo("\n⚠️  Warnings:")
        for warning in results.get('warnings', []):
            click.echo(f"   - {warning}")


@cli.command()
@click.option('--diameter', '-d', default=50.0, type=float, help='Outer diameter (mm)')
@click.option('--wall', '-w', default=2.0, type=float, help='Wall thickness (mm)')
@click.option('--height', '-h', default=200.0, type=float, help='Height (mm)')
@click.option('--tunnel-radius', '-t', default=1.5, type=float, help='Perforation radius (mm)')
@click.option('--attractors', '-a', default=3000, type=int, help='Number of attractors')
@click.option('--influence', '-i', default=16.0, type=float, help='Influence radius (mm)')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output STL file')
@click.option('--visualize/--no-visualize', default=False, help='Show pattern visualization')
def generate_moss_pole(diameter, wall, height, tunnel_radius, attractors, influence, output, visualize):
    """Generate a perforated moss pole using space colonization.
    
    Example:
        procedural-design generate-moss-pole -d 50 -h 200 -o pole.stl
    """
    click.echo("🌿 Generating moss pole with space colonization pattern...")
    click.echo(f"   Diameter: {diameter}mm, Wall: {wall}mm, Height: {height}mm")
    
    # Create configuration
    sc_config = SpaceColonizationConfig(
        attractor_count=attractors,
        influence_radius=influence,
        kill_radius=3.5,
        step_size=1.8
    )
    
    config = MossPoleConfig(
        outer_diameter=diameter,
        wall_thickness=wall,
        height=height,
        tunnel_radius=tunnel_radius,
        space_col_config=sc_config
    )
    
    # Generate
    pipeline = MossPolePipeline(config)
    
    click.echo("🌱 Growing branching pattern...")
    nodes, parents = pipeline._generate_pattern()
    
    if visualize:
        click.echo("📊 Visualizing pattern...")
        pipeline.visualize_pattern(nodes, parents)
    
    click.echo("🔨 Building mesh...")
    mesh = pipeline.generate()
    
    output_path = Path(output)
    mesh.export(output_path)
    
    # Validate
    results = validate_mesh(mesh)
    
    click.echo(f"\n✅ Generated: {output_path}")
    click.echo(f"   Vertices: {results['num_vertices']:,}")
    click.echo(f"   Faces: {results['num_faces']:,}")
    click.echo(f"   Pattern nodes: {len(nodes)}")


@cli.command()
@click.argument('mesh_file', type=click.Path(exists=True))
@click.option('--detailed/--summary', default=False, help='Show detailed analysis')
def validate(mesh_file, detailed):
    """Validate a mesh file for 3D printing.
    
    Example:
        procedural-design validate model.stl --detailed
    """
    click.echo(f"🔍 Validating: {mesh_file}")
    
    mesh = trimesh.load(mesh_file)
    results = validate_mesh(mesh)
    
    # Summary
    click.echo("\n📊 Mesh Statistics:")
    click.echo(f"   Vertices: {results['num_vertices']:,}")
    click.echo(f"   Faces: {results['num_faces']:,}")
    
    if results.get('volume'):
        click.echo(f"   Volume: {results['volume']:.2f} mm³")
    click.echo(f"   Surface Area: {results['surface_area']:.2f} mm²")
    
    # Dimensions
    dims = results['dimensions']
    click.echo(f"\n📏 Dimensions:")
    click.echo(f"   X: {dims['x']:.2f} mm")
    click.echo(f"   Y: {dims['y']:.2f} mm")
    click.echo(f"   Z: {dims['z']:.2f} mm")
    
    # Quality checks
    click.echo("\n✓ Quality Checks:")
    click.echo(f"   Watertight: {'✅ Yes' if results['is_watertight'] else '❌ No'}")
    click.echo(f"   Winding Consistent: {'✅ Yes' if results['is_winding_consistent'] else '⚠️  No'}")
    
    if results.get('degenerate_faces', 0) > 0:
        click.echo(f"   Degenerate Faces: ❌ {results['degenerate_faces']}")
    else:
        click.echo(f"   Degenerate Faces: ✅ None")
    
    # Warnings and errors
    if results.get('warnings'):
        click.echo("\n⚠️  Warnings:")
        for warning in results['warnings']:
            click.echo(f"   - {warning}")
    
    if results.get('errors'):
        click.echo("\n❌ Errors:")
        for error in results['errors']:
            click.echo(f"   - {error}")
    
    # Overall verdict
    click.echo()
    if results['is_valid']:
        click.echo("✅ Mesh is valid and ready for export!")
        return 0
    else:
        click.echo("❌ Mesh has issues that should be fixed")
        return 1


@cli.command()
@click.option('--output-dir', '-o', default='parameter_sweep', type=click.Path(), help='Output directory')
@click.option('--feed-min', default=0.02, type=float, help='Minimum feed rate')
@click.option('--feed-max', default=0.08, type=float, help='Maximum feed rate')
@click.option('--kill-min', default=0.045, type=float, help='Minimum kill rate')
@click.option('--kill-max', default=0.065, type=float, help='Maximum kill rate')
@click.option('--grid-size', '-g', default=3, type=int, help='Grid resolution (NxN)')
def parameter_sweep(output_dir, feed_min, feed_max, kill_min, kill_max, grid_size):
    """Generate a grid of vases exploring Gray-Scott parameter space.
    
    Useful for finding interesting pattern regimes.
    
    Example:
        procedural-design parameter-sweep -g 5 -o sweep_results/
    """
    import numpy as np
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"🔬 Running {grid_size}×{grid_size} parameter sweep...")
    click.echo(f"   Feed: [{feed_min}, {feed_max}]")
    click.echo(f"   Kill: [{kill_min}, {kill_max}]")
    
    feed_values = np.linspace(feed_min, feed_max, grid_size)
    kill_values = np.linspace(kill_min, kill_max, grid_size)
    
    total = grid_size * grid_size
    count = 0
    
    with click.progressbar(length=total, label='Generating') as bar:
        for i, feed in enumerate(feed_values):
            for j, kill in enumerate(kill_values):
                count += 1
                
                # Create config
                gs_config = GrayScottConfig(
                    feed_rate=feed,
                    kill_rate=kill,
                    Du=0.16,
                    Dv=0.08
                )
                
                config = VaseConfig(
                    height=150.0,
                    base_size=80.0,
                    gray_scott_config=gs_config,
                    field_resolution=128,
                    simulation_steps=10000
                )
                
                # Generate
                pipeline = VasePipeline(config)
                mesh = pipeline.generate()
                
                # Save
                filename = f"vase_f{feed:.3f}_k{kill:.3f}.stl"
                mesh.export(output_path / filename)
                
                bar.update(1)
    
    click.echo(f"\n✅ Generated {total} vases in {output_path}/")
    click.echo(f"   Parameter combinations saved")


if __name__ == '__main__':
    cli()

