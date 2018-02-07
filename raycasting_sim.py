"""Simulation of a spacecraft with a LIDAR taking measurements 
around an asteroid
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb
import logging
from collections import defaultdict
import os

import numpy as np
from scipy import integrate

from dynamics import asteroid, dumbbell, eoms, controller
from kinematics import attitude
from visualization import plotting, graphics, animation
from point_cloud import wavefront, raycaster

# simulate dumbbell moving aroudn asteroid

# TODO Add logger everywhere to know what stuff is happening

# TODO Look into the profiler for speed

# TODO Save the ast, dum, objects to the numpy


def initialize():
    """Initialize all the things for the simulation
    """
    logger = logging.getLogger(__name__)
    logger.info('Initialize asteroid and dumbbell objects')

    ast = asteroid.Asteroid('itokawa', 0, 'obj')
    dum = dumbbell.Dumbbell(m1=500, m2=500, l=0.003)
    des_att_func = controller.random_sweep_attitude
    des_tran_func = controller.inertial_fixed_state
    AbsTol = 1e-9
    RelTol = 1e-9

    return ast, dum, des_att_func, des_tran_func, AbsTol, RelTol


def simulate():

    logger = logging.getLogger(__name__)

    ast, dum, des_att_func, des_tran_func, AbsTol, RelTol = initialize()

    num_steps = int(1e3)
    time = np.linspace(0, num_steps, num_steps)
    t0, tf = time[0], time[-1]
    dt = time[1] - time[0]

    initial_pos = np.array([1.5, 0, 0])
    initial_vel = np.array([0, 0, 0])
    initial_R = attitude.rot3(np.pi / 2).reshape(-1)
    initial_w = np.array([0, 0, 0])
    initial_state = np.hstack((initial_pos, initial_vel, initial_R, initial_w))

    # TODO Initialize a coarse asteroid mesh model and combine with piont cloud data

    # initialize the raycaster and lidar
    polydata = wavefront.meshtopolydata(ast.V, ast.F)
    caster = raycaster.RayCaster(polydata)
    sensor = raycaster.Lidar(dist=5)
    # try both a controlled and uncontrolled simulation
    # t, istate, astate, bstate = eoms.inertial_eoms_driver(initial_state, time, ast, dum)

    # TODO Dynamics should be based on the course model
    # TODO Asteroid class will need a method to update mesh
    system = integrate.ode(eoms.eoms_controlled_inertial)
    system.set_integrator('lsoda', atol=AbsTol, rtol=RelTol, nsteps=1e4)
    system.set_initial_value(initial_state, t0)
    system.set_f_params(ast, dum, des_att_func, des_tran_func)

    point_cloud = defaultdict(list)

    state = np.zeros((num_steps + 1, 18))
    t = np.zeros(num_steps + 1)
    int_array = []
    state[0, :] = initial_state

    ii = 1
    while system.successful() and system.t < tf:

        # integrate the system and save state to an array
        t[ii] = (system.t + dt)
        state[ii, :] = system.integrate(system.t + dt)

        logger.info('Step : {} Time: {}'.format(ii, t[ii]))
        # now do the raycasting
        if not (np.floor(t[ii]) % 1):
            logger.info('Raycasting at t = {}'.format(t[ii]))

            targets = sensor.define_targets(state[ii, 0:3],
                                            state[ii, 6:15].reshape((3, 3)),
                                            np.linalg.norm(state[ii, 0:3]))

            # new asteroid rotation with vertices
            nv = ast.rotate_vertices(t[ii])
            Ra = ast.rot_ast2int(t[ii])
            # update the mesh inside the caster
            caster = raycaster.RayCaster.updatemesh(nv, ast.F)

            # these intersections are points in the inertial frame
            intersections = caster.castarray(state[ii, 0:3], targets)

            point_cloud['time'].append(t[ii])
            point_cloud['ast_state'].append(Ra.reshape(-1))
            point_cloud['sc_state'].append(state[ii, :])
            point_cloud['targets'].append(targets)
            point_cloud['inertial_ints'].append(intersections)

            logger.info('Found {} intersections'.format(len(intersections)))

            ast_ints = []
            for pt in intersections:
                if pt.size > 0:
                    pt_ast = Ra.T.dot(pt)
                else:
                    logger.info('No intersection for this point')
                    pt_ast = np.array([np.nan, np.nan, np.nan])

                ast_ints.append(pt_ast)

            point_cloud['ast_ints'].append(np.asarray(ast_ints))

        # TODO Eventually call the surface reconstruction function and update asteroid model

        # create an asteroid and dumbbell
        ii += 1

    # plot the simulation
    # plotting.animate_inertial_trajectory(t, istate, ast, dum)
    # plotting.plot_controlled_inertial(t, istate, ast, dum, fwidth=1)

    return time, state, point_cloud


def animate(time, state, ast, dum, point_cloud):
    graphics.point_cloud_asteroid_frame(point_cloud)

    mfig = graphics.mayavi_figure(size=(800, 600))
    mesh, ast_axes = graphics.draw_polyhedron_mayavi(ast.V, ast.F, mfig)

    com, dum_axes = graphics.draw_dumbbell_mayavi(state[0, :], dum, mfig)

    pc_lines = [graphics.mayavi_addLine(
        mfig, state[0, 0:3], p) for p in point_cloud['inertial_ints'][0]]

    animation.inertial_asteroid_trajectory(time, state, ast, dum, point_cloud,
                                           (mesh, ast_axes, com, dum_axes,
                                            pc_lines))


def reconstruct(time, state, ast, dum, point_cloud):
    """Reconstruct the shape given the simulation results
    """

    # transform all the point cloud to a consistent reference frame (ast frame)
    rot_ast2int = point_cloud['ast_state']
    intersections = point_cloud['ast_ints']
    ast_pts = []

    for pcs in intersections:
        for pt in pcs:
            if not np.isnan(pt).any():
                ast_pts.append(pt)

    ast_pts = np.asarray(ast_pts)

    # pick a subset of the total amount point cloud

    # load the ellipsoid mesh
    # ve, _ = wavefront.ellipsoid_mesh(ast.axes[0], ast.axes[1], ast.axes[2], density=20)

    # TODO Need an intelligent method of combining shape models to fill in gaps
    # call the reconstruct function
    # ast_pts = np.concatenate((ast_pts, ve), axis=0)

    v, f = wavefront.reconstruct_numpy(ast_pts)

    # plot and visualize
    mfig = graphics.mayavi_figure(size=(800, 600), bg=(0, 0, 0))
    mesh, ast_axes = graphics.draw_polyhedron_mayavi(v, f, mfig)
    # points = graphics.mayavi_points3d(ve, mfig, scale=0.01)

    return v, f


def incremental_reconstruction(filename, asteroid_name='castalia'):
    """Incrementally update the mesh
    """
    logger = logging.getLogger(__name__)
    output_filename = filename[0:-4] + '_reconstruct.npz'

    logger.info('Loading {}'.format(filename))
    data = np.load(filename)
    point_cloud = data['point_cloud'][()]

    # define the asteroid and dumbbell objects
    ast = asteroid.Asteroid(asteroid_name, 4092, 'mat')
    dum = dumbbell.Dumbbell(m1=500, m2=500, l=0.003)
    
    logger.info('Creating ellipsoid mesh')
    # define a simple mesh to start
    v, f = wavefront.ellipsoid_mesh(
        ast.axes[0], ast.axes[1], ast.axes[2], density=20)
    v_est, f_est = v, f

    v_array = []
    f_array = []

    # extract out all the points in the asteroid frame
    time = point_cloud['time']
    ast_ints = point_cloud['ast_ints']

    # loop over the points in order and update the mesh
    # mfig = graphics.mayavi_figure()
    # mesh = graphics.mayavi_addMesh(mfig, v, f)

    # points = graphics.mayavi_points3d(mfig, ast_ints[0], scale_factor=0.1)
    # ms = mesh.mlab_source
    
    logger.info('Starting loop over point cloud')
    for ii, (t, points) in enumerate(zip(time, ast_ints)):
        # check if points is empty
        logger.info('Current : t = {} with {} points'.format(t, len(points)))
        for pt in points:
            # incremental update for each point in points
            # check to make sure each pt is not nan
            if not np.any(np.isnan(pt)):
                v_est, f_est = wavefront.mesh_incremental_update(pt, v_est, f_est)

        # input("Press enter to continue")
        v_array.append(v_est)
        f_array.append(f_est)

        # save every so often and delete v_array,f_array to save memory
        if (ii % 1000) == 0:  
            logger.info('Saving data to file. ii = {}, t = {}'.format(ii, t))
            if os.path.exists(output_filename):
                logger.info('Exisiting data file. Now appending')
                data = np.load(output_filename) 
                v_array_old = data['v_array'][()]
                f_array_old = data['f_array'][()]

                v_array_old.append(v_array)
                f_array_old.append(f_array)

                np.savez(output_filename, v_array=v_array_old, f_array=f_array_old,
                        time=time)

                v_array = []
                f_array = []
            else:
                logger.info('No data file. Creating new one')

                np.savez(output_filename, v_array=v_array, f_array=f_array,
                         time=time)
                v_array = []
                f_array = []

    logger.info('Completed the reconstruction')
    return v_array, f_array

if __name__ == "__main__":
    # TODO Measure time for run
    # logging.basicConfig(filename='raycasting.txt',
                        # filemode='w', level=logging.INFO)
    # time, state, point_cloud = simulate()

    # save data to a file
    # np.savez('20180131_itokawa_raycasting_sim', time=time, state=state,
    #          point_cloud=point_cloud)

    # to access the data again
    # data = np.load(filename)
    # point_cloud = data['point_cloud'][()]

    # now reconstruct
    filename = './data/raycasting/20180110_raycasting_castalia.npz'
    logging.basicConfig(filename='reconstruct.txt',
                        filemode='w', level=logging.INFO)
    
    v_array, f_array = incremental_reconstruction(filename, 'castalia')
    np.savez('20180110_raycasting_reconstruct.npz', v_array=v_array,
             f_array=f_array)
