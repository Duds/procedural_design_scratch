#!/usr/bin/env python3
"""Interactive Streamlit app for procedural design exploration."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from pipelines.vase import VasePipeline, VaseConfig
from pipelines.moss_pole import MossPolePipeline, MossPoleConfig


def render_mesh_preview(mesh):
    """Render a simple mesh preview using matplotlib."""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot mesh
    vertices = mesh.vertices
    faces = mesh.faces
    
    ax.plot_trisurf(
        vertices[:, 0],
        vertices[:, 1],
        faces,
        vertices[:, 2],
        cmap='viridis',
        alpha=0.8,
        edgecolor='none'
    )
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('Mesh Preview')
    
    # Equal aspect ratio
    max_range = np.array([
        vertices[:, 0].max() - vertices[:, 0].min(),
        vertices[:, 1].max() - vertices[:, 1].min(),
        vertices[:, 2].max() - vertices[:, 2].min()
    ]).max() / 2.0
    
    mid_x = (vertices[:, 0].max() + vertices[:, 0].min()) * 0.5
    mid_y = (vertices[:, 1].max() + vertices[:, 1].min()) * 0.5
    mid_z = (vertices[:, 2].max() + vertices[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    return fig


def vase_generator_page():
    """Vase generator page."""
    st.header("Gray-Scott Vase Generator")
    st.markdown("""
    Generate decorative vases with reaction-diffusion patterns.
    Adjust parameters below and click Generate to create your design.
    """)
    
    # Sidebar controls
    st.sidebar.header("Geometry")
    
    height = st.sidebar.slider(
        "Height (mm)",
        min_value=50.0,
        max_value=300.0,
        value=150.0,
        step=10.0
    )
    
    base_size = st.sidebar.slider(
        "Base Size (mm)",
        min_value=40.0,
        max_value=150.0,
        value=80.0,
        step=5.0
    )
    
    profile_type = st.sidebar.selectbox(
        "Profile Shape",
        options=['square', 'circle', 'hexagon'],
        index=0
    )
    
    displacement = st.sidebar.slider(
        "Displacement Amplitude (mm)",
        min_value=0.0,
        max_value=15.0,
        value=6.0,
        step=0.5
    )
    
    if profile_type == 'square':
        corner_radius = st.sidebar.slider(
            "Corner Radius (mm)",
            min_value=5.0,
            max_value=40.0,
            value=20.0,
            step=5.0
        )
    else:
        corner_radius = 20.0
    
    st.sidebar.header("Pattern")
    
    pattern_type = st.sidebar.selectbox(
        "Pattern Type",
        options=['spots', 'stripes', 'waves', 'holes'],
        index=0
    )
    
    resolution = st.sidebar.select_slider(
        "Field Resolution",
                                      options=[64, 128, 256, 512],
        value=128
    )
    
    steps = st.sidebar.slider(
        "Simulation Steps",
        min_value=1000,
        max_value=20000,
        value=10000,
        step=1000
    )
    
    n_seeds = st.sidebar.slider(
        "Seed Patches",
        min_value=1,
        max_value=10,
        value=5
    )
    
    random_seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        max_value=9999,
        value=42
    )
    
    # Generate button
    if st.button("Generate Vase", type="primary"):
        with st.spinner("Generating pattern..."):
                config = VaseConfig(
                    height=height,
                    base_size=base_size,
                profile_type=profile_type,
                displacement_amplitude=displacement,
                corner_radius=corner_radius,
                    field_resolution=resolution,
                    simulation_steps=steps,
                n_seeds=n_seeds,
                pattern_type=pattern_type,
                random_seed=random_seed
                )
                
                pipeline = VasePipeline(config)
                
            # Generate pattern
            field = pipeline.generate_pattern()
                
            # Show pattern
            st.subheader("Generated Pattern")
                fig, ax = plt.subplots(figsize=(8, 8))
            im = ax.imshow(field, cmap='viridis', origin='lower')
            ax.set_title('Reaction-Diffusion Pattern')
            ax.axis('off')
            plt.colorbar(im, ax=ax)
                st.pyplot(fig)
                
                # Generate mesh
            with st.spinner("Generating mesh..."):
                mesh = pipeline.generate_mesh()
                    
            # Show statistics
                    st.subheader("Mesh Statistics")
            stats = pipeline.get_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vertices", f"{stats['vertices']:,}")
            with col2:
                st.metric("Faces", f"{stats['faces']:,}")
            with col3:
                st.metric("Volume", f"{stats['volume_mm3']:.1f} mm³")
            
            # Validation
            validation = pipeline.validate()
            st.subheader("Validation")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("✓ Watertight" if validation['is_watertight'] else "✗ Not watertight")
                st.write("✓ Valid winding" if validation['is_winding_consistent'] else "✗ Invalid winding")
            with col2:
                st.write("✓ No degenerate faces" if not validation['has_degenerate_faces'] else "✗ Has degenerate faces")
                st.write("✓ 3D Print Ready" if validation['is_valid'] else "✗ Needs fixing")
            
            # Export options
            st.subheader("Export")
            export_format = st.selectbox(
                "File Format",
                options=['stl', 'obj', 'ply'],
                index=0
            )
            
            # Create download button
            buffer = BytesIO()
            mesh.export(buffer, file_type=export_format)
            buffer.seek(0)
            
            st.download_button(
                label=f"Download {export_format.upper()}",
                data=buffer,
                file_name=f"vase_{random_seed}.{export_format}",
                mime=f"application/{export_format}"
            )


def moss_pole_generator_page():
    """Moss pole generator page."""
    st.header("Perforated Moss Pole Generator")
            st.markdown("""
    Generate organic perforated moss poles using space colonisation algorithm.
    Adjust parameters below and click Generate to create your design.
    """)
    
    # Sidebar controls
    st.sidebar.header("Geometry")
    
    diameter = st.sidebar.slider(
        "Outer Diameter (mm)",
        min_value=30.0,
        max_value=100.0,
        value=50.0,
        step=5.0
    )
    
    wall_thickness = st.sidebar.slider(
        "Wall Thickness (mm)",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5
    )
    
    height = st.sidebar.slider(
        "Height (mm)",
        min_value=100.0,
        max_value=400.0,
        value=200.0,
        step=10.0
    )
    
    tunnel_radius = st.sidebar.slider(
        "Tunnel Radius (mm)",
        min_value=0.5,
        max_value=3.0,
        value=1.5,
        step=0.1
    )
    
    st.sidebar.header("Pattern")
    
    attractor_count = st.sidebar.slider(
        "Attractor Count",
        min_value=500,
        max_value=5000,
        value=2000,
        step=100
    )
    
    influence_radius = st.sidebar.slider(
        "Influence Radius (mm)",
        min_value=5.0,
        max_value=30.0,
        value=16.0,
        step=1.0
    )
    
    kill_radius = st.sidebar.slider(
        "Kill Radius (mm)",
        min_value=1.0,
        max_value=10.0,
        value=3.5,
        step=0.5
    )
    
    step_size = st.sidebar.slider(
        "Step Size (mm)",
        min_value=0.5,
        max_value=5.0,
        value=1.8,
        step=0.1
    )
    
    st.sidebar.header("Structure")
    
    n_ribs = st.sidebar.slider(
        "Number of Ribs",
        min_value=0,
        max_value=8,
        value=4
    )
    
    rib_width = st.sidebar.slider(
        "Rib Width (degrees)",
        min_value=5.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    )
    
    random_seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        max_value=9999,
        value=42
    )
    
    # Generate button
    if st.button("Generate Moss Pole", type="primary"):
                config = MossPoleConfig(
                    outer_diameter=diameter,
            wall_thickness=wall_thickness,
                    height=height,
                    tunnel_radius=tunnel_radius,
            attractor_count=attractor_count,
            influence_radius=influence_radius,
            kill_radius=kill_radius,
            step_size=step_size,
            n_ribs=n_ribs,
            rib_width_degrees=rib_width,
            random_seed=random_seed
                )
                
                pipeline = MossPolePipeline(config)
                
        # Generate
        with st.spinner("Generating shell and branch pattern..."):
                    mesh = pipeline.generate()
                    
        # Show statistics
        st.subheader("Mesh Statistics")
        stats = pipeline.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Vertices", f"{stats['vertices']:,}")
        with col2:
            st.metric("Faces", f"{stats['faces']:,}")
        with col3:
            st.metric("Volume", f"{stats['volume_mm3']:.1f} mm³")
        with col4:
            st.metric("Open Fraction", f"{stats['open_fraction']:.1%}")
        
        st.metric("Branches", stats['n_branches'])
        
        # Validation
        validation = pipeline.validate()
        st.subheader("Validation")
        
        col1, col2 = st.columns(2)
    with col1:
            st.write("✓ Watertight" if validation['is_watertight'] else "✗ Not watertight")
            st.write("✓ Valid winding" if validation['is_winding_consistent'] else "✗ Invalid winding")
        with col2:
            st.write("✓ No degenerate faces" if not validation['has_degenerate_faces'] else "✗ Has degenerate faces")
            st.write("✓ 3D Print Ready" if validation['is_valid'] else "✗ Needs fixing")
        
        # Export options
        st.subheader("Export")
        export_format = st.selectbox(
            "File Format",
            options=['stl', 'obj', 'ply'],
            index=0
        )
        
        # Create download button
        buffer = BytesIO()
        mesh.export(buffer, file_type=export_format)
        buffer.seek(0)
        
        st.download_button(
            label=f"Download {export_format.upper()}",
            data=buffer,
            file_name=f"moss_pole_{random_seed}.{export_format}",
            mime=f"application/{export_format}"
        )


def main():
    """Main app entry point."""
    st.set_page_config(
        page_title="Procedural Design Studio",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎨 Procedural Design Studio")
    st.markdown("Interactive parameter exploration for generative design")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Select Generator",
        options=["Vase Generator", "Moss Pole Generator"],
        index=0
    )
    
    if page == "Vase Generator":
        vase_generator_page()
        else:
        moss_pole_generator_page()

# Footer
st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### About
    
    This app provides interactive parameter exploration for procedural design.
    
    **Algorithms:**
    - Gray-Scott Reaction-Diffusion
    - Space Colonisation
    
    **Features:**
    - Real-time parameter adjustment
    - Mesh validation
    - Export to STL/OBJ/PLY
    """)


if __name__ == '__main__':
    main()
