#include "cgal.hpp"

// TODO Modify this to compute distance instead of doing raycasting
void distance_to_polyhedron(Eigen::Vector3d& pt, std::shared_ptr<MeshData> mesh) {
    AABB_Tree tree(faces(mesh->polyhedron).first, faces(mesh->polyhedron).second, mesh->polyhedron);
    
    // create a Point object
    Point a(pt(0), pt(1), pt(2));
    Point b(0, 0, 0);
    Segment segment_query(a, b);

    // tests intersections with segment query
    if(tree.do_intersect(segment_query)) {
        std::cout << "intersection(s)" << std::endl;
    } else {
        std::cout << "no intersection" << std::endl;
    }
    
    std::cout << tree.number_of_intersected_primitives(segment_query) << " intersection(s)" << std::endl;


    Segment_intersection intersection = tree.any_intersection(segment_query);
    if(intersection) {
        // get intersection object
        const Point* p = boost::get<Point>(&(intersection->first));
        if(p) {
            std::cout << "intersection object is a point " << *p << std::endl;
        }
    }
}

// Raycaster class
RayCaster::RayCaster(std::shared_ptr<MeshData> mesh_in) {
    // assign copy of pointer to object instance
    this->mesh = mesh_in;
    this->tree.insert(faces(this->mesh->polyhedron).first,
            faces(this->mesh->polyhedron).second,
            this->mesh->polyhedron);
}

void RayCaster::update_mesh(std::shared_ptr<MeshData> mesh_in) {
    this->mesh = mesh_in;
    this->tree.clear();
    this->tree.insert(faces(this->mesh->polyhedron).first,
            faces(this->mesh->polyhedron).second,
            this->mesh->polyhedron);
}

int RayCaster::castray(const Eigen::Ref<const Eigen::Vector3d>& psource, const Eigen::Ref<const Eigen::Vector3d>& ptarget, Eigen::Ref<Eigen::Vector3d> pint) {
    // TODO Also look at closest_point_and_primitive
    // create a Point object
    Point a(psource(0),psource(1),psource(2));
    Point b(ptarget(0), ptarget(1), ptarget(2));
    Ray ray_query(a, b);
    
    // May need to add a skip function here https://doc.cgal.org/latest/AABB_tree/AABB_tree_2AABB_ray_shooting_example_8cpp-example.html
    Ray_intersection intersection = this->tree.first_intersection(ray_query);
    if (intersection) {
        // get intersection object
        const Point* p = boost::get<Point>(&(intersection->first));
        if (p) {
            // output from function
            pint << CGAL::to_double(p->x()), CGAL::to_double(p->y()), CGAL::to_double(p->y());
        } else {
            return 1;
        }

    } else {
        return 1;
    }

    return 0;
}

// MeshDistance class
// Raycaster class
MeshDistance::MeshDistance(std::shared_ptr<MeshData> mesh_in) {
    // assign copy of pointer to object instance
    this->mesh = mesh_in;

    this->vppmap = get(CGAL::vertex_point, this->mesh->surface_mesh);

    // TODO Figure out how to save KD tree to the class
    
}

void MeshDistance::update_mesh(std::shared_ptr<MeshData> mesh_in) {
    this->mesh = mesh_in;
    this->vppmap = get(CGAL::vertex_point, this->mesh->surface_mesh);

}

int MeshDistance::k_nearest_neighbor(const Eigen::Ref<const Eigen::Vector3d>& pt, const int &K) {
    
    Vertex_point_pmap vppmap = get(CGAL::vertex_point, this->mesh->surface_mesh);

    // insert number of data points in the tree
    KD_Tree tree(vertices(this->mesh->surface_mesh).begin(),
            vertices(this->mesh->surface_mesh).end(),
            Splitter(),
            KD_Traits(vppmap));
    Point query(pt(0),  pt(1), pt(2));
    Distance tr_dist(vppmap);

    K_neighbor_search search(tree, query, K, 0, true, tr_dist);
    for (K_neighbor_search::iterator it = search.begin(); it != search.end(); it++) {
        std::cout << "Vertex " << it->first << " : " << vppmap[it->first] << " at distance " 
            << tr_dist.inverse_of_transformed_distance(it->second) << std::endl;
    }
    return 0;
}
