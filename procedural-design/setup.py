Sure, here's the contents for the file: /procedural-design/procedural-design/setup.py

from setuptools import setup, find_packages

setup(
    name='procedural-design',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A project for generating decorative moss poles using reaction-diffusion patterns.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'scipy',
        'scikit-image',
        'trimesh',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)