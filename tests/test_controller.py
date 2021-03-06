from __future__ import absolute_import, division, print_function, unicode_literals
from dynamics import dumbbell, asteroid, controller
import kinematics.attitude as attitude
import pdb
import numpy as np

angle = (2*np.pi- 0) * np.random.rand(1) + 0

# generate a random initial state that is outside of the asteroid
pos = np.random.rand(3)+np.array([2,2,2])
R = attitude.rot1(angle).reshape(9)
vel = np.random.rand(3)
ang_vel = np.random.rand(3)
t = np.random.rand()*100

state = np.hstack((pos,vel, R, ang_vel))
 
ast = asteroid.Asteroid('castalia',32)

dum = dumbbell.Dumbbell()

class TestInertialDesiredAttitude():
    
    alpha = np.random.rand()
    axis = np.array([1, 0, 0])
    Rd, Rd_dot, ang_vel_d, ang_vel_d_dot = controller.desired_attitude(1, alpha, axis)

    def test_desired_rotation_matrix_determinant(self):
        np.testing.assert_almost_equal(np.linalg.det(self.Rd), 1) 
    
    def test_desired_rotation_matrix_orthogonal(self):
        np.testing.assert_array_almost_equal(self.Rd.T.dot(self.Rd), 
                np.eye(3,3))

    def test_desired_attitude_satifies_kinematics(self):
        np.testing.assert_array_almost_equal(self.Rd_dot,
                self.Rd.dot(attitude.hat_map(self.ang_vel_d)))
 
class TestInertialDesiredAttitudePerurbedBodyFixedHovering():
    
    Rd, Rd_dot, ang_vel_d, ang_vel_d_dot = controller.random_sweep_attitude(1, state, cone_angle=2)

    def test_desired_rotation_matrix_determinant(self):
        np.testing.assert_almost_equal(np.linalg.det(self.Rd), 1) 
    
    def test_desired_rotation_matrix_orthogonal(self):
        np.testing.assert_array_almost_equal(self.Rd.T.dot(self.Rd), 
                np.eye(3,3))

    def test_desired_attitude_satifies_kinematics(self):
        np.testing.assert_array_almost_equal(self.Rd_dot,
                self.Rd.dot(attitude.hat_map(self.ang_vel_d)))

    def test_z_axis_aligned_with_positive_pole(self):
        bodyz_inertial = self.Rd[:,2]
        z_inertial = np.array([0, 0, 1])
        angle = np.arccos(np.dot(bodyz_inertial, z_inertial))
        np.testing.assert_array_less(angle, np.pi/2)

    def test_angle_less_than_required(self):
        b1 = - pos/ np.linalg.norm(pos)
        b1pert = np.squeeze(self.Rd[:, 0])
        
        np.testing.assert_array_less(np.arccos(np.dot(b1, b1pert)), np.deg2rad(2))

class TestInertialDesiredAttitudeBodyFixedHovering():
    
    Rd, Rd_dot, ang_vel_d, ang_vel_d_dot = controller.body_fixed_pointing_attitude(1, state)

    def test_desired_rotation_matrix_determinant(self):
        np.testing.assert_almost_equal(np.linalg.det(self.Rd), 1) 
    
    def test_desired_rotation_matrix_orthogonal(self):
        np.testing.assert_array_almost_equal(self.Rd.T.dot(self.Rd), 
                np.eye(3,3))

    def test_desired_attitude_satifies_kinematics(self):
        np.testing.assert_array_almost_equal(self.Rd_dot,
                self.Rd.dot(attitude.hat_map(self.ang_vel_d)))

    def test_x_axis_anti_aligned_with_position_vector(self):
        dot_product = np.dot(self.Rd[:, 0], pos / np.linalg.norm(pos))
        np.testing.assert_almost_equal(dot_product, -1)

    def test_z_axis_aligned_with_positive_pole(self):
        bodyz_inertial = self.Rd[:,2]
        z_inertial = np.array([0, 0, 1])
        angle = np.arccos(np.dot(bodyz_inertial, z_inertial))
        np.testing.assert_array_less(angle, np.pi/2)


class TestInertialAttitudeController():
    """Test the attitude controller for the inertial eoms
    """
    des_att_tuple = controller.body_fixed_pointing_attitude(1, state)
    u_m = controller.attitude_controller(t, state, np.zeros(3), dum, ast, des_att_tuple)

    def test_control_moment_size(self):
        np.testing.assert_equal(self.u_m.shape, (3,))

class TestDumbbellInertialTranslationalController():
    
    des_tran_tuple = controller.traverse_then_land_vertically(0, ast)
    u_f = controller.translation_controller(t, state, np.zeros(3), dum, ast, des_tran_tuple)

    def test_control_force_size(self):
        np.testing.assert_equal(self.u_f.shape, (3,))

class TestDumbbellAsteroidTranslationalController():
    
    # this assumes we're dealing with the asteroid fixed dynamics - so the state
    # is defined in the asteroid fixed frame.

    des_tran_tuple = controller.asteroid_circumnavigate(0)
    u_f = controller.translation_controller_asteroid(t, state, np.zeros(3), dum, ast, des_tran_tuple)

    def test_control_force_size(self):
        np.testing.assert_equal(self.u_f.shape, (3,))

    def test_desired_translation_x_des_size(self):
        xd = self.des_tran_tuple[0]
        np.testing.assert_equal(xd.shape, (3,))

    def test_desired_translation_xd_des_size(self):
        xd_des = self.des_tran_tuple[1]
        np.testing.assert_equal(xd_des.shape, (3,))

    def test_desired_translation_xdd_des_size(self):
        xdd_des = self.des_tran_tuple[2]
        np.testing.assert_equal(xdd_des.shape, (3,))

class TestAsteroidRotationalController():
    """Test the attitude control for the asteroid fixed frame
    """

    des_att_tuple = controller.asteroid_pointing(0, state, ast)
    u_m = controller.attitude_controller(0, state, np.zeros(3), dum, ast, des_att_tuple)

    def test_desired_attitude_Rd_size(self):
        Rd = self.des_att_tuple[0]
        np.testing.assert_equal(Rd.shape, (3, 3))

    def test_desired_attitude_Rd_SO3(self):
        Rd = self.des_att_tuple[0]
        attitude.test_rot_mat_in_special_orthogonal_group(Rd)

    def test_control_moment_size(self):
       np.testing.assert_equal(self.u_m.shape, (3,))

class TestDumbbellAsteroidTranslationalLissajous():
    
    # this assumes we're dealing with the asteroid fixed dynamics - so the state
    # is defined in the asteroid fixed frame.

    des_tran_tuple = controller.inertial_lissajous_yz_plane(0)
    u_f = controller.translation_controller_asteroid(t, state, np.zeros(3), dum, ast, des_tran_tuple)

    def test_control_force_size(self):
        np.testing.assert_equal(self.u_f.shape, (3,))

    def test_desired_translation_x_des_size(self):
        xd = self.des_tran_tuple[0]
        np.testing.assert_equal(xd.shape, (3,))

    def test_desired_translation_xd_des_size(self):
        xd_des = self.des_tran_tuple[1]
        np.testing.assert_equal(xd_des.shape, (3,))

    def test_desired_translation_xdd_des_size(self):
        xdd_des = self.des_tran_tuple[2]
        np.testing.assert_equal(xdd_des.shape, (3,))

