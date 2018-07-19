"""Plot the data from explore_main or explore_control

Author
------
Shankar Kulumani		GWU		skulumani@gwu.edu
"""
import pdb
import numpy as np
import os
import h5py
import argparse
import subprocess
import datetime

from point_cloud import wavefront
from visualization import graphics, publication
import utilities

from lib import stats

import matplotlib.pyplot as plt
from matplotlib import colors, cm

def exploration_generate_plots(data_path, img_path='/tmp/diss_explore', 
                               magnification=4, step=1, show=True):
    """Given a HDF5 file generated by explore (C++) this will generate some plots
    """

    if not os.path.exists(img_path):
        os.makedirs(img_path)

    with h5py.File(data_path, 'r') as hf:
        rv = hf['reconstructed_vertex']
        rw = hf['reconstructed_weight']
        
        # get all the keys
        v_keys = np.array(utilities.sorted_nicely(list(rv.keys())))
        w_keys = np.array(utilities.sorted_nicely(list(rw.keys())))

        v_initial = hf['initial_vertex'][()]
        f_initial = hf['initial_faces'][()]
        w_initial = np.squeeze(hf['initial_weight'][()])

        # determine the maximum extents of the mesh and add some margin
        scale = 1.25
        max_x = scale*np.max(v_initial[:, 0])
        min_x = scale*np.min(v_initial[:, 0])
        max_y = scale*np.max(v_initial[:, 1])
        min_y = scale*np.min(v_initial[:, 1])
        max_z = scale*np.max(v_initial[:, 2])
        min_z = scale*np.min(v_initial[:, 2])

        """Partial images during the reconstruction"""
        mfig = graphics.mayavi_figure(offscreen=(not show))
        mesh = graphics.mayavi_addMesh(mfig, v_initial, f_initial)
        ms = mesh.mlab_source
        graphics.mayavi_axes(mfig, [min_x, max_x, min_x, max_x, min_x, max_x], line_width=5, color=(1, 0, 0))
        graphics.mayavi_view(fig=mfig)
        partial_index = np.array([0, v_keys.shape[0]*1/4, v_keys.shape[0]*1/2,
                                  v_keys.shape[0]*3/4, v_keys.shape[0]*4/4-1],
                                 dtype=np.int)
        for img_index, vk in enumerate(partial_index):
            filename = os.path.join(img_path, 'partial_' + str(vk) + '.jpg')
            v = rv[str(vk)][()]
            # generate an image and save it 
            ms.reset(x=v[:, 0], y=v[:, 1], z=v[:,2], triangles=f_initial)
            graphics.mlab.savefig(filename, magnification=magnification)
        
        """Plot the truth asteroid"""
        v_true = hf['truth_vertex'][()]
        f_true = hf['truth_faces'][()]
        ms.reset(x=v_true[:, 0], y=v_true[:, 1], z=v_true[:,2], triangles=f_true)
        graphics.mayavi_axes(mfig, [min_x, max_x, min_x, max_x, min_x, max_x], line_width=5, color=(1, 0, 0))
        graphics.mayavi_view(fig=mfig)
        graphics.mlab.savefig(os.path.join(img_path, 'truth.jpg' ), magnification=magnification)

        # """Create a bunch of images for animation"""
        # animation_path = os.path.join(img_path, 'animation')
        # if not os.path.exists(animation_path):
        #     os.makedirs(animation_path)
        # ms.reset(x=v_initial[:, 0], y=v_initial[:, 1], z=v_initial[:, 2], triangles=f_initial,
        #          scalars=w_initial)
        # graphics.mayavi_view(mfig)
        # for ii, vk in enumerate(v_keys[::step]):
        #     filename = os.path.join(animation_path, str(ii).zfill(7) + '.jpg')
        #     v = rv[vk][()]
        #     w = np.squeeze(rw[str(vk)][()])
        #     ms.reset(x=v[:, 0], y=v[:, 1], z=v[:, 2], triangles=f_initial, scalars=w)
        #     graphics.mayavi_savefig(mfig, filename, magnification=magnification)

def plot_uncertainty(filename, img_path="/tmp/diss_explore", show=True):
    """Compute the sum of uncertainty and plot as function of time"""

    with h5py.File(filename, 'r') as hf:
        rv = hf['reconstructed_vertex']
        rw = hf['reconstructed_weight']

        # get all the keys for the groups
        v_keys = np.array(utilities.sorted_nicely(list(rv.keys())))
        w_keys = np.array(utilities.sorted_nicely(list(rw.keys())))
    
        t_array = []
        w_array = []

        for ii, wk in enumerate(w_keys):
            t_array.append(ii)
            w_array.append(np.sum(rw[wk][()]))

        t_array = np.array(t_array)
        w_array = np.array(w_array)

        print(w_array[-1])
    
    # now call the plotting function
    publication.plot_uncertainty(t_array, w_array, img_path=img_path, pgf_save=True,
                                 show=show)

def plot_state_trajectory(filename):
    """Plot the state trajectory

    Plot state in 3D
    Plot state in cartesian map project
    """

    # load the hdf5
    with h5py.File(filename, 'r') as hf:
        state_group = hf['state']

        # get all the keys for the groups
        state_keys = np.array(utilities.sorted_nicely(list(state_group.keys())))
    
        t_array = np.zeros(len(state_keys))
        state_inertial_array = np.zeros((len(state_keys), 18))
        state_asteroid_array = np.zeros((len(state_keys), 18))

        for ii, sk in enumerate(state_keys):
            t_array[ii] = ii
            state_inertial_array[ii, :] = state_group[sk][()]
            state_asteroid_array[ii, :] = state_group[sk][()]

    
    # pass to the plotting function
    publication.plot_state(t_array, state_inertial_array, state_asteroid_array)

def plot_volume(filename, img_path="/tmp/diss_explore", show=True):
    """Compute the volume of the asteroid at each time step
    """
    with h5py.File(filename, 'r') as hf:
        rv_group = hf['reconstructed_vertex']
        f_initial = hf['initial_faces'][()]

        rv_keys = np.array(utilities.sorted_nicely(list(rv_group.keys())))

        t_array = np.zeros(len(rv_keys))
        vol_array = np.zeros(len(rv_keys))

        for ii, key in enumerate(rv_keys):
            t_array[ii] = ii
            vol_array[ii] = stats.volume(rv_group[key][()], f_initial)

        true_vertices = hf['truth_vertex'][()]
        true_faces = hf['truth_faces'][()]
        true_volume = stats.volume(true_vertices, true_faces)

    publication.plot_volume(t_array, vol_array, true_volume, img_path=img_path, pgf_save=True,
                            show=show)

def save_animation(filename, output_path, mesh_weight=False, magnification=4):
    
    output_path = os.path.join(output_path, 'animation')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with h5py.File(filename, 'r') as hf:
        rv = hf['reconstructed_vertex']
        rw = hf['reconstructed_weight']
        
        # get all the keys
        v_keys = np.array(utilities.sorted_nicely(list(rv.keys())))
        w_keys = np.array(utilities.sorted_nicely(list(rw.keys())))

        v_initial = hf['initial_vertex'][()]
        f_initial = hf['initial_faces'][()]
        w_initial = np.squeeze(hf['initial_weight'][()])
            
        # think about a black background as well
        mfig = graphics.mayavi_figure(bg=(0, 0, 0), size=(800,600), offscreen=True)
        
        if mesh_weight:
            mesh = graphics.mayavi_addMesh(mfig, v_initial, f_initial,
                                           scalars=w_initial,
                                           color=None, colormap='viridis')
        else:
            mesh = graphics.mayavi_addMesh(mfig, v_initial, f_initial)

        # xaxis = graphics.mayavi_addLine(mfig, np.array([0, 0, 0]), np.array([2, 0, 0]), color=(1, 0, 0)) 
        # yaxis = graphics.mayavi_addLine(mfig, np.array([0, 0, 0]), np.array([0, 2, 0]), color=(0, 1, 0)) 
        # zaxis = graphics.mayavi_addLine(mfig, np.array([0, 0, 0]), np.array([0, 0, 2]), color=(0, 0, 1)) 
        # ast_axes = (xaxis, yaxis, zaxis)
        
        print("Images will be saved to {}".format(output_path))
        ms = mesh.mlab_source
        # determine the maximum extents of the mesh and add some margin
        scale = 1.25
        max_x = scale*np.max(v_initial[:, 0])
        min_x = scale*np.min(v_initial[:, 0])
        max_y = scale*np.max(v_initial[:, 1])
        min_y = scale*np.min(v_initial[:, 1])
        max_z = scale*np.max(v_initial[:, 2])
        min_z = scale*np.min(v_initial[:, 2])

        graphics.mayavi_axes(mfig, [min_x, max_x, min_x, max_x, min_x, max_x], line_width=5, color=(1, 0, 0))
        graphics.mayavi_view(fig=mfig)

        # loop over keys and save images
        for img_index, vk in enumerate(v_keys):
            filename = os.path.join(output_path, str(vk).zfill(7) + '.jpg')
            new_vertices = rv[str(vk)][()]
            new_faces = f_initial
            new_weight = rw[str(vk)][()]

            # generate an image and save it 
            if mesh_weight:
                ms.set(x=new_vertices[:, 0],y=new_vertices[:, 1],
                       z=new_vertices[:,2], triangles=new_faces,
                       scalars=new_weight)
            else:
                ms.set(x=new_vertices[:, 0],y=new_vertices[:, 1],
                       z=new_vertices[:,2], triangles=new_faces)

            graphics.mlab.savefig(filename, magnification=magnification)

    # now call ffmpeg
    fps = 60
    name_str = "reconstruction_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S") + ".mp4"

    name = os.path.join(output_path, name_str)
    ffmpeg_fname = os.path.join(output_path, '%07d.jpg')
    cmd = "ffmpeg -framerate {} -i {} -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' {}".format(fps, ffmpeg_fname, name)
    print(cmd)
    subprocess.check_output(['bash', '-c', cmd])

    # remove folder now
    for file in os.listdir(output_path): 
        file_path = os.path.join(output_path, file)
        if file_path.endswith('.jpg'):
            os.remove(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate plots from explore",
                                     formatter_class=argparse.RawTextHelpFormatter)

    # add options
    parser.add_argument("hdf5_file", help="The data file to read", type=str)
    parser.add_argument("img_path", help="The path to save images", type=str)
    parser.add_argument("--show", help="Show the plots", action="store_true",
                        default=False)
    parser.add_argument("-m", "--magnification", help="Magnification for images",
                       action="store", type=int, const=4, nargs='?', default=4)
    parser.add_argument("-mc", "--move_cam", help="For use with the -a, --animate option. This will translate the camera and give you a view from the satellite",
                        action="store_true")
    parser.add_argument("-mw", "--mesh_weight", help="For use with the -a, --animate option. This will add the uncertainty as a colormap to the asteroid",
                        action="store_true")
     
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--reconstruct", help="Reconstruction plots for video",
                       action="store_true")
    group.add_argument("-u", "--uncertainty", help="Uncertainty plot",
                       action="store_true")
    group.add_argument("-s", "--state", help="State trajectory plot",
                       action="store_true")
    group.add_argument("-v", "--volume", help="Volume of estimate",
                       action="store_true")
    group.add_argument("-a", "--animation", help="Animation and video of the reconstruction",
                       action="store_true")
    args = parser.parse_args()

    if args.reconstruct:
        exploration_generate_plots(args.hdf5_file, args.img_path, magnification=args.magnification, show=args.show);
    elif args.uncertainty:
        plot_uncertainty(args.hdf5_file, img_path=args.img_path, show=args.show)
    elif args.state:
        plot_state_trajectory(args.hdf5_file)
    elif args.volume:
        plot_volume(args.hdf5_file, img_path=args.img_path, show=args.show)
    elif args.animation:
        save_animation(args.hdf5_file, output_path=args.img_path,
                       mesh_weight=args.mesh_weight)



