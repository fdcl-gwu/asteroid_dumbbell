#ifndef STATS_H
#define STATS_H

#include "mesh.hpp"

#include <memory>

void print_polyhedron_vertices(std::shared_ptr<MeshData> mesh);

void print_polyhedron_faces(std::shared_ptr<MeshData> mesh);

void print_polyhedron_stats(std::shared_ptr<MeshData> mesh);
#endif
