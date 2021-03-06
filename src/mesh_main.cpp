#include "loader.hpp"
#include "mesh.hpp"
#include "cgal.hpp"
#include "polyhedron.hpp"
#include "stats.hpp"

#include "input_parser.hpp"

#include <igl/readOBJ.h>

#include <CGAL/Polygon_mesh_processing/refine.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>

#include <memory>
#include <iostream>
#include <fstream>
#include <chrono>

// try to write a function to  find distance from mesh to point using AABB
//
int main(int argc, char* argv[]) {
    InputParser input(argc, argv);
    if (input.option_exists("-h")) {
        std::cout << "Usage mesh -i input_file.obj" << std::endl;
    }

    const std::string input_file = input.get_command_option("-i");
    std::shared_ptr<MeshData> mesh;

    // create a mesh object
    if (input_file.empty()) {
        std::cout << "No input file!!! mesh -h" << std::endl;
        return 1;
    }

    /* mesh = Loader::load(input_file); */
    Eigen::MatrixXd V;
    Eigen::MatrixXi F;
    
    igl::readOBJ(input_file, V, F);
    
    mesh = std::make_shared<MeshData>(V, F);

    // lets try and build a surface mesh now
    Eigen::MatrixXd v_eigen = mesh->get_verts();
    Eigen::MatrixXi f_eigen = mesh->get_faces();

    // update the mesh with new data
    mesh->update_mesh(v_eigen, f_eigen);

    Stats::surface_mesh_stats(mesh);

    /* print_surface_mesh_vertices(mesh); */

    Eigen::Vector3d psource, ptarget;
    psource << 2, 0, 0;
    ptarget << 0, 0, 0;

    // instantiate the raycaster object
    RayCaster caster(mesh);
    Eigen::Vector3d intersection;
    intersection = caster.castray(psource, ptarget);
    std::cout << "Intersection point: " << intersection << std::endl;
    // compute minimum distance to mesh
    double min_dist = caster.minimum_distance(psource);
    std::cout << "Minimum distance: " << min_dist << std::endl;

    // Distance to mesh object
    MeshDistance mesh_dist(mesh);

    mesh_dist.k_nearest_neighbor(psource, 5);

    // compute the volume of the mesh
    double vol;
    vol = PolyVolume::volume(mesh->get_verts(), mesh->get_faces());
    std::cout << "Volume: " << vol << std::endl;
    
    /* std::cout << "Vertices: \n" << mesh->vertices << std::endl; */
    /* std::cout << "Faces: \n" << mesh->faces << std::endl; */

    /* print_polyhedron_vertices(mesh); */
    
    // test the mesh constructor
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    MeshData mesh_test(V, F);
    std::chrono::steady_clock::time_point end= std::chrono::steady_clock::now();

    std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count() << " microsecond" << std::endl;
    std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::nanoseconds> (end - begin).count() << " nanosecond " << std::endl;
    return 0;
}
