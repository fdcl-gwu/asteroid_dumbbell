"""Test out the incremental mesh updating
"""
import numpy as np
from point_cloud import wavefront

import pdb

class TestVertexInsertion():
    v, f = wavefront.read_obj('./integration/cube.obj')
    pt = np.array([1, 1, 1])
    mesh_parameters = wavefront.polyhedron_parameters(v, f)
    D, P, V, E, F, primitive = wavefront.distance_to_mesh(
        pt, v, f, mesh_parameters)
    nv, nf = wavefront.vertex_insertion(pt, v, f, D, P, V, E, F)

    # expected solutions
    nv_exp = np.array([[-0.5, -0.5, -0.5],
                       [-0.5, -0.5, 0.5],
                       [-0.5, 0.5, -0.5],
                       [-0.5, 0.5, 0.5],
                       [0.5, -0.5, -0.5],
                       [0.5, -0.5, 0.5],
                       [0.5, 0.5, -0.5],
                       [1., 1., 1.]])

    nf_exp = np.array([[0, 6, 4],
                       [0, 2, 6],
                       [0, 3, 2],
                       [0, 1, 3],
                       [2, 7, 6],
                       [2, 3, 7],
                       [4, 6, 7],
                       [4, 7, 5],
                       [0, 4, 5],
                       [0, 5, 1],
                       [1, 5, 7],
                       [1, 7, 3]])

    def test_last_vertex(self):
        np.testing.assert_allclose(self.nv[-1, :], self.pt)

    def test_vertices(self):
        np.testing.assert_allclose(self.nv, self.nv_exp)

    def test_faces(self):
        np.testing.assert_allclose(self.nf, self.nf_exp)

    def test_vertices_shape(self):
        np.testing.assert_allclose(self.nv.shape, self.v.shape)


class TestEdgeInsertion():
    v, f = wavefront.read_obj('./integration/cube.obj')
    pt = np.array([1, 1, 0])
    mesh_parameters = wavefront.polyhedron_parameters(v, f)
    D, P, V, E, F, primitive = wavefront.distance_to_mesh(
        pt, v, f, mesh_parameters)
    nv, nf = wavefront.edge_insertion(pt, v, f, D, P, V, E, F)

    # expected solutions
    nv_exp = np.array([[-0.5, -0.5, -0.5],
                       [-0.5, -0.5,  0.5],
                       [-0.5,  0.5, -0.5],
                       [-0.5,  0.5,  0.5],
                       [0.5, -0.5, -0.5],
                       [0.5, -0.5,  0.5],
                       [0.5,  0.5, -0.5],
                       [0.5,  0.5,  0.5],
                       [1.,  1.,  0.]])

    nf_exp = np.array([[0, 6, 4],
                       [0, 2, 6],
                       [0, 3, 2],
                       [0, 1, 3],
                       [2, 3, 7],
                       [4, 7, 5],
                       [0, 4, 5],
                       [0, 5, 1],
                       [1, 5, 7],
                       [1, 7, 3],
                       [2, 7, 8],
                       [2, 8, 6],
                       [4, 8, 7],
                       [4, 6, 8]])

    def test_vertices(self):
        np.testing.assert_allclose(self.nv, self.nv_exp)

    def test_faces(self):
        np.testing.assert_allclose(self.nf, self.nf_exp)

    def test_vertices_shape(self):
        np.testing.assert_allclose(self.nv.shape, (self.v.shape[0] + 1, 3))


class TestFaceInsertion():
    v, f = wavefront.read_obj('./integration/cube.obj')
    pt = np.array([1, 0.1, 0])
    mesh_parameters = wavefront.polyhedron_parameters(v, f)
    D, P, V, E, F, primitive = wavefront.distance_to_mesh(
        pt, v, f, mesh_parameters)
    nv, nf = wavefront.face_insertion(pt, v, f, D, P, V, E, F)

    # expected solutions
    nv_exp = np.array([[-0.5, -0.5, -0.5],
                       [-0.5, -0.5,  0.5],
                       [-0.5,  0.5, -0.5],
                       [-0.5,  0.5,  0.5],
                       [0.5, -0.5, -0.5],
                       [0.5, -0.5,  0.5],
                       [0.5,  0.5, -0.5],
                       [0.5,  0.5,  0.5],
                       [1.,  0.1,  0.]])

    nf_exp = np.array([[0, 6, 4],
                       [0, 2, 6],
                       [0, 3, 2],
                       [0, 1, 3],
                       [2, 7, 6],
                       [2, 3, 7],
                       [4, 7, 5],
                       [0, 4, 5],
                       [0, 5, 1],
                       [1, 5, 7],
                       [1, 7, 3],
                       [4, 6, 8],
                       [6, 7, 8],
                       [7, 4, 8]])

    def test_vertices(self):
        np.testing.assert_allclose(self.nv, self.nv_exp)

    def test_faces(self):
        np.testing.assert_allclose(self.nf, self.nf_exp)

    def test_vertices_shape(self):
        np.testing.assert_allclose(self.nv.shape, (self.v.shape[0] + 1, 3))


class TestRadiusMeshUpdate():
    """Test out the incremental mesh update using the radius modification
    """
    v, f = wavefront.read_obj('./integration/cube.obj')

    def test_vertex_radial_change(self):
        pt = np.array([1, 1, 1])
        mesh_parameters = wavefront.polyhedron_parameters(self.v, self.f)
        nv, nf = wavefront.radius_mesh_incremental_update(pt, self.v, self.f,
                                                          mesh_parameters,
                                                          max_angle=np.deg2rad(5))
        nv_exp = self.v.copy()
        nv_exp[-1, :] = pt
        np.testing.assert_allclose(nv, nv_exp)
        np.testing.assert_allclose(nf, self.f)

    def test_edge_insertion(self):
        """Point is out of view of any vertices. Need to modify the edge
        """
        pt = np.array([1, 0, 0])
        mesh_parameters = wavefront.polyhedron_parameters(self.v, self.f)
        nv, nf = wavefront.radius_mesh_incremental_update(pt, self.v, self.f,
                                                          mesh_parameters,
                                                          max_angle=np.deg2rad(5))
        nv_exp = np.array([[-0.5, -0.5, -0.5],
                           [-0.5, -0.5,  0.5],
                           [-0.5,  0.5, -0.5],
                           [-0.5,  0.5,  0.5],
                           [0.5, -0.5, -0.5],
                           [0.5, -0.5,  0.5],
                           [0.5,  0.5, -0.5],
                           [0.5,  0.5,  0.5],
                           [1.,  0.,  0.]])
        nf_exp = np.array([[0, 6, 4],
                           [0, 2, 6],
                           [0, 3, 2],
                           [0, 1, 3],
                           [2, 7, 6],
                           [2, 3, 7],
                           [0, 4, 5],
                           [0, 5, 1],
                           [1, 5, 7],
                           [1, 7, 3],
                           [4, 6, 8],
                           [8, 6, 7],
                           [4, 8, 5],
                           [8, 7, 5]])

        np.testing.assert_allclose(nv, nv_exp)
        np.testing.assert_allclose(nf, nf_exp)

    def test_face_insertion(self):
        """Point is out of view of any vertices. Need to modify the edge
        """
        pt = np.array([1, 0.1, 0])
        mesh_parameters = wavefront.polyhedron_parameters(self.v, self.f)
        nv, nf = wavefront.radius_mesh_incremental_update(pt, self.v, self.f,
                                                          mesh_parameters,
                                                          max_angle=np.deg2rad(5))
        nv_exp = self.v.copy()
        nv_exp = np.concatenate((nv_exp, pt[np.newaxis]))
        nf_exp = np.array([[0, 6, 4],
                           [0, 2, 6],
                           [0, 3, 2],
                           [0, 1, 3],
                           [2, 7, 6],
                           [2, 3, 7],
                           [4, 7, 5],
                           [0, 4, 5],
                           [0, 5, 1],
                           [1, 5, 7],
                           [1, 7, 3],
                           [4, 6, 8],
                           [6, 7, 8],
                           [7, 4, 8]])

        np.testing.assert_allclose(nv, nv_exp)
        np.testing.assert_allclose(nf, nf_exp)

class TestSphericalMeshUpdate():
    """Test out the spherical mesh update function
    """
    v, f = wavefront.read_obj('./integration/cube.obj')
    weight = np.full(v.shape[0], 1)
    max_angle = 1

    def test_mesh_update(self):
        pt = np.array([1, 1, 1])
        nv, nw = wavefront.spherical_incremental_mesh_update(pt, 
                                                             self.v, self.f,
                                                             self.weight, self.max_angle)
        np.testing.assert_allclose(nv[-1, :], pt)        
        np.testing.assert_allclose(nw[-1], 0)

