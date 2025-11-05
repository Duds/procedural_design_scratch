# test_mesh.py

import unittest
from src.utils.mesh import create_mesh, export_mesh

class TestMeshFunctions(unittest.TestCase):

    def test_create_mesh(self):
        # Test mesh creation with valid parameters
        vertices, faces = create_mesh(radius=5, height=10)
        self.assertEqual(len(vertices), expected_vertex_count)
        self.assertEqual(len(faces), expected_face_count)

    def test_export_mesh(self):
        # Test exporting mesh to STL format
        vertices, faces = create_mesh(radius=5, height=10)
        result = export_mesh(vertices, faces, 'test_mesh.stl')
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()