#include "eigen_hdf5.hpp"

#include <gtest/gtest.h>

#include <iostream>

TEST(TestHDF5Wrapper, CreateFile) {
    HDF5::File hf_file("/tmp/test.hdf5", 1); 
}