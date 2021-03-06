"""Visualize using VTK or Mayavi for fancy 3D graphics and things

Use VTK/Mayavi to make fancy plots

Author
------
Shankar Kulumani		GWU		skulumani@gwu.edu
"""
import logging
import pdb

import vtk
from vtk.util import numpy_support
from mayavi import mlab
import numpy as np

from point_cloud import wavefront

def draw_polyhedron_vtk(vertices, faces):
    r"""Plot a polyhedron using VTK

    mesh = draw_polyhedron_vtk(v, f)

    Parameters
    ----------
    vertices : (v, 3) numpy array
        Array holding all the vertices of the mesh
    faces : (f, 3) numpy array
        Array holding all of the faces of the mesh

    Returns
    -------
    none

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    # create a polydata object
    polyData = meshtopolydata(vertices, faces)

    # render and view
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polyData)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # now render
    camera = vtk.vtkCamera()
    camera.SetPosition(1, 1, 1)
    camera.SetFocalPoint(0, 0, 0)

    renderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)

    iren = vtk.vtkXRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    renderer.AddActor(actor)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.SetBackground(0, 0, 0)

    renWin.SetSize(800,800)

    renWin.Render()
    iren.Start()

def draw_polyhedron_mayavi(vertices, faces, fig):
    r"""Plot a polyhedron using Mayavi

    mesh = draw_polyhedron_mayavi(v, f, fig)

    Parameters
    ----------
    vertices : (v, 3) numpy array
        Array holding all the vertices of the mesh
    faces : (f, 3) numpy array
        Array holding all of the faces of the mesh
    fig : mlab.figure()
        Figure to plot the mesh into

    Returns
    -------
    mesh : mlab.triangular_mesh
        Mesh object from mayavi

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    x = vertices[:, 0]
    y = vertices[:, 1]
    z = vertices[:, 2]
    scalars = np.tile(0.5, x.shape)
    mesh = mlab.triangular_mesh(x, y, z, faces, color=(0.5, 0.5, 0.5), figure=fig,
                                representation='surface')
    
    # draw the body axes of the asteroid
    xaxis = mayavi_addLine(fig, np.array([0, 0, 0]), np.array([2, 0, 0]), color=(1, 0, 0)) 
    yaxis = mayavi_addLine(fig, np.array([0, 0, 0]), np.array([0, 2, 0]), color=(0, 1, 0)) 
    zaxis = mayavi_addLine(fig, np.array([0, 0, 0]), np.array([0, 0, 2]), color=(0, 0, 1)) 
    
    body_axes = (xaxis, yaxis, zaxis)

    return mesh, body_axes

def draw_dumbbell_mayavi(state, dum, fig):
    """Draw the dumbbell rigid body model and body axes

    """
    logger = logging.getLogger(__name__)
    pos = state[0:3]
    R = state[6:15]

    com = mlab.points3d(pos[0], pos[1], pos[2], color=(0, 0, 0), 
                        scale_factor=0.1)
    
    # draw the body axes of the asteroid
    xaxis = mayavi_addLine(fig, pos, pos+[1, 0, 0], color=(1, 0, 0)) 
    yaxis = mayavi_addLine(fig, pos, pos+[0, 1, 0], color=(0, 1, 0)) 
    zaxis = mayavi_addLine(fig, pos, pos+[0, 0, 1], color=(0, 0, 1)) 
    
    body_axes = (xaxis, yaxis, zaxis)

    return com, body_axes

def vtk_addPoint(renderer, p, radius=0.1, color=[0.0, 0.0, 1]):
    r"""Add a point to a VTK render

    vtk_addPoint(renderer, point, radius=0.1, color=[R, G, B])

    Parameters
    ----------
    renderer : vtk.vtkRenderer()
        Renderer object in vtk
    p : (3,) array/tuple
        Point to plot in VTK
    radius : float
        Size of the point ( graphing units)
    color : (3,) array
        RGB color of point

    Returns
    -------
    none

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    res = 100

    point = vtk.vtkSphereSource()
    point.SetCenter(p)
    point.SetRadius(radius)
    point.SetPhiResolution(res)
    point.SetThetaResolution(res)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(point.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)

    renderer.AddActor(actor)
    
    return 0

def vtk_addLine(renderer, p1, p2, color=[0.0, 0.0, 1.0]):
    r"""Add a line to a VTK render

    vtk_addLine(renderer, p1, p2, radius=0.1, color=[R, G, B])

    Parameters
    ----------
    renderer : vtk.vtkRenderer()
        Renderer object in vtk
    p1 : (3,) array/tuple
        Start Point to plot in VTK
    p2 : (3,) array/tuple
        End Point to plot in VTK
    radius : float
        Size of the point ( graphing units)
    color : (3,) array
        RGB color of point

    Returns
    -------
    none

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    line = vtk.vtkLineSource()
    line.SetPoint1(p1)
    line.SetPoint2(p2)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)

    renderer.AddActor(actor)
    
    return 0

def vtk_addPoly(renderer, polydata, color=[0.0, 0.0, 1.0]):
    r"""Add a polyhedron to a VTK render

    vtk_addPoly(renderer, polydata, color=[R, G, B])

    Parameters
    ----------
    renderer : vtk.vtkRenderer()
        Renderer object in vtk
    polydata : vtk.vtkPolyData
        Polyhedron object ( can convert numpy arrays to mesh from wavefront)
    color : (3,) array
        RGB color of point

    Returns
    -------
    none

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    # now viusalize
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarRange(0, 7)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer.AddActor(actor)

    return 0

def vtk_show(renderer, width=800, height=600):
    r"""Start a vtk renderer window and interact

    vtk_show(renderer, width, height)

    Parameters
    ----------
    renderer : vtk.vtkRenderer()
        Renderer object in vtk
    width, height : int
        Width and height in pixels of resulting window

    Returns
    -------
    none

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    # now render
    camera = vtk.vtkCamera()
    camera.SetPosition(2, 2, 2)
    camera.SetFocalPoint(0, 0, 0)

    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.SetBackground(0, 0, 0)

    renderWindow = vtk.vtkRenderWindow()
    # renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(width, height)
    
    iren = vtk.vtkXRenderWindowInteractor()
    iren.SetRenderWindow(renderWindow)

    renderWindow.Render()
    iren.Start()

def vtk_renderer():
    """Just creates a renderer so you don't have to import VTK everywhere
    """
    return vtk.vtkRenderer()

def mayavi_figure(size=(800, 600), bg=(1, 1, 1),offscreen=False, **kwargs):
    """Just define a figure for mayavi to plot into
    """
    mlab.options.offscreen = offscreen
    return mlab.figure(bgcolor=bg, size=size, **kwargs)

def mayavi_addPoly(fig, polydata, color=(0.5, 0.5, 0.5)):
    r"""Draw a VKT polydata object to a mayavi figure

    mesh = mayavi_addPoly(fig, polydata)

    Convert the polydata to V,F then plot inside mayavi

    Parameters
    ----------
    fig : mlab.figure()
        Mayavi figure to draw into
    polydata : vtk.vtkPolyData object
        Polyhedron object from VTK

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """
    vertices, faces = wavefront.polydatatomesh(polydata)

    scalars = np.tile(0.5, vertices.shape[0])
    mesh = mlab.triangular_mesh(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                                faces, color=color, figure=fig,
                                representation='surface')

    return mesh

def mayavi_addMesh(fig, vertices, faces, color=(0.5, 0.5, 0.5), 
                   representation='surface', **kwargs):
    r"""Draw a mesh to a mayavi figure

    mesh = mayavi_addPoly(fig, v, f, color)

    Draw mesh defined by vertices and faces to a mayavi figure

    Parameters
    ----------
    fig : mlab.figure()
        Mayavi figure to draw into
    vertices : (v, 3) numpy array
        Array holding all the vertices of the mesh
    faces : (f, 3) numpy array
        Array holding all of the faces of the mesh

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """

    scalars = np.tile(0.5, vertices.shape[0])
    mesh = mlab.triangular_mesh(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                                faces, color=color, figure=fig,
                                representation=representation, **kwargs)
    return mesh

def mayavi_addLine(fig, p1, p2, color=( 0, 0, 1 )):
    r"""Add a line to a mayavi figure

    mayavi_addLine(fig, p1, p2, radius=0.1, color=[R, G, B])

    Parameters
    ----------
    fig : mlab.figure()
        Figure to plot into
    p1 : (3,) array/tuple
        Start Point to plot 
    p2 : (3,) array/tuple
        End Point to plot
    radius : float
        Size of the line( graphing units)
    color : (3,) array
        RGB color of line

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    if p1.size == 3:
        line = mlab.plot3d([p1[0], p2[0]], 
                           [p1[1], p2[1]],
                           [p1[2], p2[2]],
                           color=color,
                           figure=fig,
                           tube_radius=None)
    elif p1.size > 3:
        line = [mlab.plot3d([p1[ii, 0], p2[ii, 0]],
                            [p1[ii, 1], p2[ii, 1]],
                            [p1[ii, 2], p2[ii, 2]],
                            color=color, figure=fig, tube_radius=None) 
                for ii in range(p1.shape[0])]

    return line

def mayavi_addPoint(fig, p, radius=0.1, color=( 0, 0, 1 ), **kwargs):
    r"""Add a point to a mayavi figure

    mayavi_addPoint(fig, p, radius=0.1, color=[R, G, B])

    Parameters
    ----------
    fig : mlab.figure()
        Figure to plot into
    p : (3,) array/tuple
        Start Point to plot 
    radius : float
        Size of the line( graphing units)
    color : (3,) array
        RGB color of line

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    logger = logging.getLogger(__name__)
    if p.size == 0:
        logger.info('No points to plot')
        return None
    elif p.size > 3:
        # check if an array
        # TODO Plot all points at once and return a single handle for all of them
        points = []
        for pt in p:
            points.append( mlab.points3d(pt[0], pt[1], pt[2],scale_factor=radius, color=color, figure=fig,
                                         **kwargs))

        return points
    else:
        p = np.squeeze(p)
        point = mlab.points3d(p[0], p[1], p[2],scale_factor=radius, color=color, figure=fig,
                              **kwargs)
        return point

def mayavi_plot_trajectory(fig, pos, color=(1, 0, 0), **kwargs):
    r"""Draw trajectory onto mayavi figure

    traj = mayavi_plot_trajectory(fig, pos, color)    

    Parameters
    ----------
    fig : mlab.figure()
        Figure to plot into
    pos : (n, 3) array/tuple
        Points of trajectory to plot into figure
    color: (3,) array
        RGB color of line

    Returns
    -------
    traj: mlab.plot3d()
        Plot3d handle to the trajectory

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """ 
    logger = logging.getLogger(__name__)
    
    if len(pos) == 3: # only a single position
        l = mlab.points3d(pos[0], pos[1], pos[2], color=color, **kwargs)
    elif len(pos) > 3:
        l = mlab.points3d(pos[:, 0], pos[:, 1], pos[:, 2], color=color, **kwargs) 
    

    return l

def mayavi_points3d(figure, points, scale_factor=0.1, color=(0, 0, 1), **kwargs):
    r"""Scatter plot of points in mayavi

    p = mayavi_points3d(points, figure, scale, color)

    Parameters
    ----------
    figure : mayavi figure
        Figure to draw the points
    points : numpy array (n, 3)
        Array of point locations, each row is a single point
    scale : float
        Scale for the points
    color : tuple
        RGB color

    Returns
    -------
    p : mayavi object
        Points3d object defining all the points

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """
    if points.size == 3:
        p = mlab.points3d(points[0], points[1], points[2],
                          scale_factor=scale_factor,
                          color=color, figure=figure, **kwargs)
    elif points.size > 3:
        p = mlab.points3d(points[:, 0], points[:, 1], points[:, 2],
                        scale_factor=scale_factor, color=color, figure=figure, 
                        **kwargs)
    
    return p

def mayavi_addTitle(fig, string, **kwargs):
    r"""Add a title to mayavi figure

    t = mayavi_addTitle(fig, string, **kwargs)

    Parameters
    ----------
    fig : mayavi figure
        Figure to add the title
    string : str
        Title string
    **kwargs : keyword list matching documentation
        Height, color, size are useful

    Returns
    -------
    t : mayavi object
        Title object

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """
    t = mlab.title(string, figure=fig, **kwargs)
    return t

def mayavi_view(fig, azimuth=None, elevation=None, distance='auto', 
                focalpoint='auto', **kwargs):
    r"""Change the view of the mayavi figure

    mayavi_view(fig, azimuth, elevation, **kwargs)

    Parameters
    ----------
    fig : mayavi figure
        Figure to add the title
    azimuth : float
        Angle (0-360) angle from the x axis (longitude)
    elevation : float
        Angle (0-180) from the vertical z axis (latitude)
    distance : float or 'auto'
        Distance to the focal point. Auto will best fit all objects
    focalpoint : array_lik (3) or 'float'
        Focal point of the camera. Auto will be the center of all objects
    **kwargs : keyword list 
        
    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu
    """
    mlab.view(azimuth=azimuth, elevation=elevation,
              distance=distance, focalpoint=focalpoint, figure=fig, **kwargs)
    return 0

def mayavi_axes(fig, extent, tube_radius=None, line_width=2, **kwargs):
    r"""Add axes to figure

    mayavi_axes(fig, extent, line_width=2.0, **kwargs)

    Parameters
    ----------
    fig : mayavi figure
        Figure to add the axes
    extent : array_like (6, )
        [xmin, xmax, ymin, ymax, zmin, zmax]
    line_width: float
        Width of lines

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    """
    mlab.plot3d([extent[0], extent[1]], [0, 0], [0, 0], color=(1, 0, 0), tube_radius=tube_radius, line_width=line_width)
    mlab.plot3d([0, 0], [extent[2], extent[3]], [0, 0], color=(0, 1, 0), tube_radius=tube_radius, line_width=line_width)
    mlab.plot3d([0, 0], [0, 0], [extent[4], extent[5]], color=(0, 0, 1), tube_radius=tube_radius, line_width=line_width)
    return 0

def mayavi_savefig(fig, filename, magnification=4, **kwargs):
    r"""Save mayavi figure

    mayavi_savefig(fig, filename, magnification=4, **kwargs)

    Parameters
    ----------

    fig : mayavi figure
        Figure to save
    filename : filename to save
    magnification : float
        Scale for the image

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    """
    mlab.savefig(filename, figure=fig, magnification=magnification, **kwargs)
    return 0

def point_cloud_asteroid_frame(point_cloud, bg=(0,0,0)):
    """Input the point cloud data and plot all in the asteroid fixed frame
    """
    # rotate each  one by the state of the asteroid
    rot_ast2int = point_cloud['ast_state'] # rotation from asteroid to inertial frame
    intersections = point_cloud['ast_ints'] # ints in the inertial frame
    ast_pts = []

    mfig = mayavi_figure(bg=bg)

    for pcs in intersections:
        for pt in pcs:
            if not np.isnan(pt).any():
                ast_pts.append(pt)
   
    ast_pts = np.asarray(ast_pts)
    mlab.points3d(ast_pts[:, 0], ast_pts[:, 1], ast_pts[:, 2],scale_factor=0.005, 
                  color=(0, 0, 1), figure=mfig)
    # plot everything in the asteroid frame

