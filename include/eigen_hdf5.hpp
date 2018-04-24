/**
    Simple wrapper for Eigen to/from HDF5 datasets
    
    Updated/correctd from the work of Jim Garrison
    https://github.com/garrison/eigen3-hdf5

    @author Shankar Kulumani
    @version 23 April 2018
*/

#ifndef EIGEN_HDF5_H
#define EIGEN_HDF5_H
#include <Eigen/Dense>
#include "H5Cpp.h"

#include <stdexcept>

// TODO Use H5::H5Object isntead of H5Location it has attribute member functions
// TODO Turn on compression by default or maybe with a flag as well
class HDF5DataSet {
    // save data to the dataset (eigen arrays)
    // save attribute to dataset
};

class HDF5Group : public HDF5DataSet {
    // create a new dataset inside the group
    // create attribute in the group
};

class HDF5File : public HDF5Group {
    public: 
        HDF5File( void );

        // close the file
        virtual ~HDF5File( void );
        
        /** @fn Open the HDF5 file
                
            Open the file for reading (default to only opening new file)

            @param file_name File_name for the file

            @author Shankar Kulumani
            @version 23 April 2018
        */
        HDF5File(const std::string& file_name);
        
        /** @fn Open HDF5 file for reading/writing
                
            Can specify some options for the file

            @param file_name File name to open/create
            @param access_mode "r", "w"

            @author Shankar Kulumani
            @version 23 April 2018
        */
        HDF5File(const std::string& file_name, const std::string& access_mode);
        
        // create a group inside this file and return HDF5Group
        // create a dataset and return HDF5DataSet
        // create attribute
    private:
        H5::H5File hf;
};

template <typename T>
struct DatatypeSpecialization;

// floating-point types

template <>
struct DatatypeSpecialization<float> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_FLOAT;
    }
};

template <>
struct DatatypeSpecialization<double> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_DOUBLE;
    }
};

template <>
struct DatatypeSpecialization<long double> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_LDOUBLE;
    }
};

// integer types

template <>
struct DatatypeSpecialization<short> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_SHORT;
    }
};

template <>
struct DatatypeSpecialization<unsigned short> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_USHORT;
    }
};

template <>
struct DatatypeSpecialization<int> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_INT;
    }
};

template <>
struct DatatypeSpecialization<unsigned int> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_UINT;
    }
};

template <>
struct DatatypeSpecialization<long> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_LONG;
    }
};

template <>
struct DatatypeSpecialization<unsigned long> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_ULONG;
    }
};

template <>
struct DatatypeSpecialization<long long> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_LLONG;
    }
};

template <>
struct DatatypeSpecialization<unsigned long long> {
    static inline const H5::DataType * get (void) {
        return &H5::PredType::NATIVE_ULLONG;
    }
};
// string types, to be used mainly for attributes

template <>
struct DatatypeSpecialization<const char *> {
    static inline const H5::DataType * get (void) {
        static const H5::StrType strtype(0, H5T_VARIABLE);
        return &strtype;
    }
};

template <>
struct DatatypeSpecialization<char *> {
    static inline const H5::DataType * get (void){
        static const H5::StrType strtype(0, H5T_VARIABLE);
        return &strtype;
    }
};

// XXX: for some unknown reason the following two functions segfault if
// H5T_VARIABLE is used.  The passed strings should still be null-terminated,
// so this is a bit worrisome.

template <std::size_t N>
struct DatatypeSpecialization<const char [N]> {
    static inline const H5::DataType * get (void) {
        static const H5::StrType strtype(0, N);
        return &strtype;
    }
};

template <std::size_t N>
struct DatatypeSpecialization<char [N]> {
    static inline const H5::DataType * get (void) {
        static const H5::StrType strtype(0, N);
        return &strtype;
    }
};

template <typename Derived>
void load (const H5::H5Location &h5group, const std::string &name, const Eigen::DenseBase<Derived> &mat);

template <typename Derived>
void save (H5::H5Location &h5group, const std::string &name, 
        const Eigen::EigenBase<Derived> &mat,
        const H5::DSetCreatPropList &plist=H5::DSetCreatPropList::DEFAULT);


namespace internal
{
    template <typename Derived>
    H5::DataSpace create_dataspace (const Eigen::EigenBase<Derived> &mat);

    template <typename Derived>
    bool write_rowmat(const Eigen::EigenBase<Derived> &mat,
        const H5::DataType * const datatype,
        H5::DataSet *dataset,
        const H5::DataSpace* dspace);

    template <typename Derived>
    bool write_colmat(const Eigen::EigenBase<Derived> &mat,
        const H5::DataType * const datatype,
        H5::DataSet *dataset,
        const H5::DataSpace* dspace);

    // H5::Attribute and H5::DataSet both have similar API's, and although they
    // share a common base class, the relevant methods are not virtual.  Worst
    // of all, they take their arguments in different orders!

    template <typename Scalar>
    inline void read_data (const H5::DataSet &dataset, Scalar *data, const H5::DataType &datatype) {
        dataset.read(data, datatype);
    }

    template <typename Scalar>
    inline void read_data (const H5::Attribute &dataset, Scalar *data, const H5::DataType &datatype) {
        dataset.read(datatype, data);
    }

    // read a column major attribute; I do not know if there is an hdf routine to read an
    // attribute hyperslab, so I take the lazy way out: just read the conventional hdf
    // row major data and let eigen copy it into mat. 
    template <typename Derived>
    bool read_colmat(const Eigen::DenseBase<Derived> &mat,
        const H5::DataType * const datatype,
        const H5::Attribute &dataset);

    template <typename Derived>
    bool read_colmat(const Eigen::DenseBase<Derived> &mat,
        const H5::DataType * const datatype,
        const H5::DataSet &dataset);

    template <typename Derived, typename DataSet>
        void _load (const DataSet &dataset, const Eigen::DenseBase<Derived> &mat);
}
#endif