"""
    Script to compare inertial and relative equations of motion

"""
import numpy as np
from scipy import integrate
import pdb

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import dynamics.asteroid as asteroid
import dynamics.dumbbell as dumbbell
import kinematics.attitude as attitude
import plotting

def inertial2relative(time, state, ast, dum):
    """Convert inertial state to the asteroid fixed frame

    """

    # figure out transformation from inertial frame to relative frame
    Rast2int = np.zeros((3,3,time.shape[0]))
    Rint2ast = np.zeros((3,3,time.shape[0]))

    relative_state = np.zeros(state.shape)

    for ii,t in np.ndenumerate(time):
        Rast2int[:,:,ii] = attitude.rot3(ast.omega*t, 'c')[:,:,np.newaxis] # asteroid body frame to inertial frame
        Rint2ast[:,:,ii] = attitude.rot3(ast.omega*t, 'c').T[:,:,np.newaxis]

        Ra = np.squeeze(Rast2int[:,:,ii])
        # convert inertial states to relative states
        inertial_pos = np.squeeze(state[ii,0:3])
        inertial_vel = np.squeeze(state[ii,3:6])
        inertial_R = np.squeeze(state[ii,6:15].reshape(3,3))
        inertial_w = np.squeeze(state[ii,15:18])

        relative_pos = Ra.T.dot(inertial_pos)
        relative_vel = Ra.T.dot(inertial_vel)
        relative_R = Ra.T.dot(inertial_R).reshape(9)
        relative_w = relative_R.reshape((3,3)).dot(inertial_w)

        relative_state[ii,:] = np.hstack((relative_pos, relative_vel, relative_R, relative_w))

    return relative_state,Rast2int, Rint2ast

def relative2inertial(time, state, ast, dum):
    """Convert relative state to the inertial frame
    
    Inputs:
        time
        state - state defined wrt asteroid body fixed frame
        ast
        dum
    """

    # transformation between asteroid fixed frame and inertial frame
    # figure out transformation from inertial frame to relative frame
    Rast2int = np.zeros((3, 3, time.shape[0]))
    Rint2ast = np.zeros((3, 3, time.shape[0]))

    inertial_state = np.zeros(state.shape)

    for ii, t in np.ndenumerate(time):
        Rast2int[:, :, ii] = attitude.rot3(ast.omega*t, 'c')[:, :, np.newaxis] # asteroid body frame to inertial frame
        Rint2ast[:, :, ii] = attitude.rot3(ast.omega*t, 'c').T[:, :, np.newaxis]

        Ra = np.squeeze(Rast2int[:, :, ii])
        # convert the relative state to the inertial frame
        relative_pos = np.squeeze(state[ii, 0:3])
        relative_vel = np.squeeze(state[ii, 3:6])
        relative_R = np.squeeze(state[ii, 6:15].reshape(3, 3))
        relative_w = np.squeeze(state[ii, 15:18])

        inertial_pos = Ra.dot(relative_pos)
        inertial_vel = Ra.dot(relative_vel)
        inertial_R = Ra.dot(relative_R).reshape(9)
        inertial_w = relative_R.reshape((3, 3)).dot(relative_w)

        inertial_state[ii, :] = np.hstack((inertial_pos, inertial_vel, inertial_R, inertial_w))

    return inertial_state, Rast2int, Rint2ast

def load_data(inertial_filename, relative_filename, mode):
    # load simulation data
    # inertial_filename = 'inertial_energy_test.npz'
    # relative_filename = 'relative_energy_test.npz'
    # mode = 0
    with np.load(inertial_filename, allow_pickle=True) as data:
        inertial_state = data['state']
        inertial_time = data['time']
        inertial_KE = data['KE']
        inertial_PE = data['PE']
        ast_name = data['ast_name'][()]
        num_faces = data['num_faces'][()]
        tf = data['tf'][()]
        num_steps = data['num_steps'][()]

    with np.load(relative_filename, allow_pickle=True) as data:
        relative_state = data['state']
        relative_time = data['time']
        relative_KE = data['KE']
        relative_PE = data['PE']
        relative_ast_name = data['ast_name'][()]
        relative_num_faces = data['num_faces'][()]
        relative_tf = data['tf'][()]
        relative_num_steps = data['num_steps'][()]

    # make sure we're dealing with the same simulation results or else the comparison is meaningless
    np.testing.assert_string_equal(relative_ast_name, ast_name)
    np.testing.assert_allclose(relative_num_faces, num_faces)
    np.testing.assert_allclose(relative_tf, tf)
    np.testing.assert_allclose(relative_num_steps, num_steps)
    np.testing.assert_allclose(relative_state.shape, inertial_state.shape)

    ast = asteroid.Asteroid(ast_name,num_faces)
    dum = dumbbell.Dumbbell()

    return relative_time, inertial_time, relative_state, inertial_state, ast, dum

def plot_relative_comparison(relative_time, inertial_time, relative_state, inertial_state, ast, dum):
    """Compare the EOMS in the relative frame (asteroid fixed frame)
    
    Inputs:
        relative_time
        inertial_time
        relative_state
        inertial_state
        ast
        dum

    Outputs:

    """
    # extract out the state
    inertial_pos = inertial_state[:,0:3]
    inertial_vel = inertial_state[:,3:6]
    inertial_R = inertial_state[:,6:15]
    inertial_w = inertial_state[:,15:18]

    relative_pos = relative_state[:,0:3]
    relative_vel = relative_state[:,3:6]
    relative_R = relative_state[:,6:15]
    relative_w = relative_state[:,15:18]

    # convert inertial to relative frame
    inertial2relative_state,_,_ = inertial2relative(inertial_time, inertial_state, ast, dum)

    i2r_pos = inertial2relative_state[:,0:3]
    i2r_vel = inertial2relative_state[:,3:6]
    i2r_R = inertial2relative_state[:,6:15]
    i2r_w = inertial2relative_state[:,15:18]

    # position comparison
    pos_fig, pos_axarr = plt.subplots(3,1, sharex=True)
    pos_axarr[0].plot(relative_time, relative_pos[:,0], label='Relative EOMs')
    pos_axarr[0].plot(inertial_time, i2r_pos[:,0], label='Transformed Inertial')
    pos_axarr[0].set_ylabel(r'$X$ (km)')
        
    pos_axarr[1].plot(relative_time, relative_pos[:,1], label='Relative EOMs')
    pos_axarr[1].plot(inertial_time, i2r_pos[:,1], label='Transformed Inertial')
    pos_axarr[1].set_ylabel(r'$Y$ (km)')
        
    pos_axarr[2].plot(relative_time, relative_pos[:,2], label='Relative EOMs')
    pos_axarr[2].plot(inertial_time, i2r_pos[:,2], label='Transformed Inertial')
    pos_axarr[2].set_ylabel(r'$Z$ (km)')
     
    pos_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Comparison')
    plt.legend()  

    posdiff_fig, posdiff_axarr = plt.subplots(3,1, sharex=True)
    posdiff_axarr[0].plot(relative_time, np.absolute(relative_pos[:,0]-i2r_pos[:,0]))
    posdiff_axarr[0].set_ylabel(r'$\Delta X$ (km)')
        
    posdiff_axarr[1].plot(relative_time, np.absolute(relative_pos[:,1]-i2r_pos[:,1]))
    posdiff_axarr[1].set_ylabel(r'$\Delta Y$ (km)')
        
    posdiff_axarr[2].plot(relative_time, np.absolute(relative_pos[:,2]-i2r_pos[:,2]))
    posdiff_axarr[2].set_ylabel(r'$\Delta Z$ (km)')
     
    posdiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Difference')

    # velocity comparison
    vel_fig, vel_axarr = plt.subplots(3,1, sharex=True)
    vel_axarr[0].plot(relative_time, relative_vel[:,0], label='Relative EOMs')
    vel_axarr[0].plot(inertial_time, i2r_vel[:,0], label='Transformed Inertial')
    vel_axarr[0].set_ylabel(r'$\dot X$ (km)')
        
    vel_axarr[1].plot(relative_time, relative_vel[:,1], label='Relative EOMs')
    vel_axarr[1].plot(inertial_time, i2r_vel[:,1], label='Transformed Inertial')
    vel_axarr[1].set_ylabel(r'$\dot Y$ (km)')
        
    vel_axarr[2].plot(relative_time, relative_vel[:,2], label='Relative EOMs')
    vel_axarr[2].plot(inertial_time, i2r_vel[:,2], label='Transformed Inertial')
    vel_axarr[2].set_ylabel(r'$\dot Z$ (km)')
     
    vel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Comparison')
    plt.legend()

    veldiff_fig, veldiff_axarr = plt.subplots(3,1, sharex=True)
    veldiff_axarr[0].plot(relative_time, np.absolute(relative_vel[:,0]-i2r_vel[:,0]))
    veldiff_axarr[0].set_ylabel(r'$\Delta \dot X$ (km)')
        
    veldiff_axarr[1].plot(relative_time, np.absolute(relative_vel[:,1]-i2r_vel[:,1]))
    veldiff_axarr[1].set_ylabel(r'$\Delta \dot Y$ (km)')
        
    veldiff_axarr[2].plot(relative_time, np.absolute(relative_vel[:,2]-i2r_vel[:,2]))
    veldiff_axarr[2].set_ylabel(r'$\Delta \dot Z$ (km)')
     
    veldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Difference')

    # angular velocity comparison
    angvel_fig, angvel_axarr = plt.subplots(3,1, sharex=True)
    angvel_axarr[0].plot(relative_time, relative_w[:,0], label='Relative EOMs')
    angvel_axarr[0].plot(inertial_time, i2r_w[:,0], label='Transformed Inertial')
    angvel_axarr[0].set_ylabel(r'$\dot \Omega_1$ (rad/sec)')
        
    angvel_axarr[1].plot(relative_time, relative_w[:,1], label='Relative EOMs')
    angvel_axarr[1].plot(inertial_time, i2r_w[:,1], label='Transformed Inertial')
    angvel_axarr[1].set_ylabel(r'$\dot \Omega_2$ (rad/sec)')
        
    angvel_axarr[2].plot(relative_time, relative_w[:,2], label='Relative EOMs')
    angvel_axarr[2].plot(inertial_time, i2r_w[:,2], label='Transformed Inertial')
    angvel_axarr[2].set_ylabel(r'$\dot \Omega_3$ (rad/sec)')
     
    angvel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Comparison')
    plt.legend()

    angveldiff_fig, angveldiff_axarr = plt.subplots(3,1, sharex=True)
    angveldiff_axarr[0].plot(relative_time, np.absolute(relative_w[:,0]-i2r_w[:,0]))
    angveldiff_axarr[0].set_ylabel(r'$\Delta \dot \Omega$ (rad/sec)')
        
    angveldiff_axarr[1].plot(relative_time, np.absolute(relative_w[:,1]-i2r_w[:,1]))
    angveldiff_axarr[1].set_ylabel(r'$\Delta \dot \Omega_2$ (rad/sec)')
        
    angveldiff_axarr[2].plot(relative_time, np.absolute(relative_w[:,2]-i2r_w[:,2]))
    angveldiff_axarr[2].set_ylabel(r'$\Delta \dot \Omega_3$ (rad/sec)')
     
    angveldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Difference')

    # attitude matrix comparison
    att_fig, att_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        att_axarr[row,col].plot(relative_time, relative_R[:,ii])
        att_axarr[row,col].plot(relative_time, i2r_R[:,ii])

    # attitude matrix difference
    attdiff_fig, attdiff_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix Difference')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        attdiff_axarr[row,col].plot(relative_time, np.absolute(relative_R[:,ii]-i2r_R[:,ii]))

    plt.show()

    return 0

def plot_inertial_comparison(relative_time, inertial_time, relative_state, inertial_state, ast, dum):
    """Compare the EOMS in the inertial frame, everything transformed to the inertial frame
    
    Inputs:
        relative_time
        inertial_time
        relative_state
        inertial_state
        ast
        dum

    Outputs:

    """
    # extract out the state
    inertial_pos = inertial_state[:,0:3]
    inertial_vel = inertial_state[:,3:6]
    inertial_R = inertial_state[:,6:15]
    inertial_w = inertial_state[:,15:18]

    relative_pos = relative_state[:,0:3]
    relative_vel = relative_state[:,3:6]
    relative_R = relative_state[:,6:15]
    relative_w = relative_state[:,15:18]

    # convert inertial to relative frame
    relative2inertial_state,_,_ = relative2inertial(relative_time, relative_state, ast, dum)

    r2i_pos = relative2inertial_state[:,0:3]
    r2i_vel = relative2inertial_state[:,3:6]
    r2i_R = relative2inertial_state[:,6:15]
    r2i_w = relative2inertial_state[:,15:18]

    # position comparison
    pos_fig, pos_axarr = plt.subplots(3,1, sharex=True)
    pos_axarr[0].plot(inertial_time, inertial_pos[:,0], label='Inertial EOMs')
    pos_axarr[0].plot(relative_time, r2i_pos[:,0], label='Transformed Relative')
    pos_axarr[0].set_ylabel(r'$X$ (km)')
        
    pos_axarr[1].plot(inertial_time, inertial_pos[:,1], label='Inertial EOMs')
    pos_axarr[1].plot(relative_time, r2i_pos[:,1], label='Transformed Relative')
    pos_axarr[1].set_ylabel(r'$Y$ (km)')
        
    pos_axarr[2].plot(inertial_time, inertial_pos[:,2], label='Inertial EOMs')
    pos_axarr[2].plot(relative_time, r2i_pos[:,2], label='Transformed Relative')
    pos_axarr[2].set_ylabel(r'$Z$ (km)')
     
    pos_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Comparison')
    plt.legend()  

    posdiff_fig, posdiff_axarr = plt.subplots(3,1, sharex=True)
    posdiff_axarr[0].plot(inertial_time, np.absolute(inertial_pos[:,0]-r2i_pos[:,0]))
    posdiff_axarr[0].set_ylabel(r'$\Delta X$ (km)')
        
    posdiff_axarr[1].plot(inertial_time, np.absolute(inertial_pos[:,1]-r2i_pos[:,1]))
    posdiff_axarr[1].set_ylabel(r'$\Delta Y$ (km)')
        
    posdiff_axarr[2].plot(inertial_time, np.absolute(inertial_pos[:,2]-r2i_pos[:,2]))
    posdiff_axarr[2].set_ylabel(r'$\Delta Z$ (km)')
     
    posdiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Difference')

    # velocity comparison
    vel_fig, vel_axarr = plt.subplots(3,1, sharex=True)
    vel_axarr[0].plot(inertial_time, inertial_vel[:,0], label='inertial EOMs')
    vel_axarr[0].plot(relative_time, r2i_vel[:,0], label='Transformed relative')
    vel_axarr[0].set_ylabel(r'$\dot X$ (km)')
        
    vel_axarr[1].plot(inertial_time, inertial_vel[:,1], label='inertial EOMs')
    vel_axarr[1].plot(relative_time, r2i_vel[:,1], label='Transformed relative')
    vel_axarr[1].set_ylabel(r'$\dot Y$ (km)')
        
    vel_axarr[2].plot(inertial_time, inertial_vel[:,2], label='inertial EOMs')
    vel_axarr[2].plot(relative_time, r2i_vel[:,2], label='Transformed relative')
    vel_axarr[2].set_ylabel(r'$\dot Z$ (km)')
     
    vel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Comparison')
    plt.legend()

    veldiff_fig, veldiff_axarr = plt.subplots(3,1, sharex=True)
    veldiff_axarr[0].plot(inertial_time, np.absolute(inertial_vel[:,0]-r2i_vel[:,0]))
    veldiff_axarr[0].set_ylabel(r'$\Delta \dot X$ (km)')
        
    veldiff_axarr[1].plot(inertial_time, np.absolute(inertial_vel[:,1]-r2i_vel[:,1]))
    veldiff_axarr[1].set_ylabel(r'$\Delta \dot Y$ (km)')
        
    veldiff_axarr[2].plot(inertial_time, np.absolute(inertial_vel[:,2]-r2i_vel[:,2]))
    veldiff_axarr[2].set_ylabel(r'$\Delta \dot Z$ (km)')
     
    veldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Difference')

    # angular velocity comparison
    angvel_fig, angvel_axarr = plt.subplots(3,1, sharex=True)
    angvel_axarr[0].plot(inertial_time, inertial_w[:,0], label='Inertial EOMs')
    angvel_axarr[0].plot(relative_time, r2i_w[:,0], label='Transformed Relative')
    angvel_axarr[0].set_ylabel(r'$\dot \Omega_1$ (rad/sec)')
        
    angvel_axarr[1].plot(inertial_time, inertial_w[:,1], label='Inertial EOMs')
    angvel_axarr[1].plot(relative_time, r2i_w[:,1], label='Transformed Relative')
    angvel_axarr[1].set_ylabel(r'$\dot \Omega_2$ (rad/sec)')
        
    angvel_axarr[2].plot(inertial_time, inertial_w[:,2], label='Inertial EOMs')
    angvel_axarr[2].plot(relative_time, r2i_w[:,2], label='Transformed Relative')
    angvel_axarr[2].set_ylabel(r'$\dot \Omega_3$ (rad/sec)')
     
    angvel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Comparison')
    plt.legend()

    angveldiff_fig, angveldiff_axarr = plt.subplots(3,1, sharex=True)
    angveldiff_axarr[0].plot(inertial_time, np.absolute(inertial_w[:,0]-r2i_w[:,0]))
    angveldiff_axarr[0].set_ylabel(r'$\Delta \dot \Omega$ (rad/sec)')
        
    angveldiff_axarr[1].plot(inertial_time, np.absolute(inertial_w[:,1]-r2i_w[:,1]))
    angveldiff_axarr[1].set_ylabel(r'$\Delta \dot \Omega_2$ (rad/sec)')
        
    angveldiff_axarr[2].plot(inertial_time, np.absolute(inertial_w[:,2]-r2i_w[:,2]))
    angveldiff_axarr[2].set_ylabel(r'$\Delta \dot \Omega_3$ (rad/sec)')
     
    angveldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Difference')

    # attitude matrix comparison
    att_fig, att_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        att_axarr[row,col].plot(inertial_time, inertial_R[:,ii])
        att_axarr[row,col].plot(relative_time, i2r_R[:,ii])

    # attitude matrix difference
    attdiff_fig, attdiff_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix Difference')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        attdiff_axarr[row,col].plot(inertial_time, np.absolute(inertial_R[:,ii]-r2i_R[:,ii]))

    plt.show()

    return 0

def relative_frame_comparision():
    """Compare the EOMs in the asteroid fixed frame

    Inputs:

    Outputs:

    Dependencies:


    """
    import inertial_driver as id
    import relative_driver as rd

    ast_name = 'castalia'
    num_faces = 64
    tf = 1e4
    num_steps = 1e4

    i_time, i_state = id.inertial_eoms_driver(ast_name, num_faces, tf, num_steps)
    r_time, r_state = rd.relative_eoms_driver(ast_name, num_faces, tf, num_steps)

    ast = asteroid.Asteroid(ast_name,num_faces)
    dum = dumbbell.Dumbbell()

    # also compute and compare the energy behavior

    # also look at the animation of both and the converted form as well
    
    plot_relative_comparison(r_time, i_time, r_state, i_state, ast, dum) 

    return 0
    
def inertial_frame_comparison():
    """Compare EOMs in the inertial frame

    """
    import inertial_driver as id
    import relative_driver as rd

    ast_name = 'castalia'
    num_faces = 64
    tf = 1e4
    num_steps = 1e4

    i_time, i_state = id.inertial_eoms_driver(ast_name, num_faces, tf, num_steps)
    r_time, r_state = rd.relative_eoms_driver(ast_name, num_faces, tf, num_steps)

    ast = asteroid.Asteroid(ast_name,num_faces)
    dum = dumbbell.Dumbbell()

    # also compute and compare the energy behavior

    # also look at the animation of both and the converted form as well
    
    plot_relative_comparison(r_time, i_time, r_state, i_state, ast, dum) 

    return 0

if __name__ == '__main__':
    pass