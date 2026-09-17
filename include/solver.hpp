#pragma once

#include <cmath>
#include <complex>
#include <cstring>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace sim
{
    using Complex = std::complex<double>;

    constexpr double PI = 3.14159265358979323846;

    struct Vec3
    {
        double x = 0.0, y = 0.0, z = 0.0;
    };

    namespace dir
    {
        constexpr Vec3 PX{ 1.0,  0.0,  0.0};
        constexpr Vec3 NX{-1.0,  0.0,  0.0};

        constexpr Vec3 PY{ 0.0,  1.0,  0.0};
        constexpr Vec3 NY{ 0.0, -1.0,  0.0};

        constexpr Vec3 PZ{ 0.0,  0.0,  1.0};
        constexpr Vec3 NZ{ 0.0,  0.0, -1.0};
    }

    double dot(const Vec3 &a, const Vec3 &b);

    struct OpticalPoint
    {
        double wavelength_nm;
        double n;
        double kappa;
    };

    std::vector<OpticalPoint> load_optical_curve(const char *filename);

    struct SolarPoint
    {
        double wavelength_nm;
        double irradiance;
    };

    std::vector<SolarPoint> load_solar_spectrum(const char *filename, double lambda_min_nm, double lambda_max_nm);

    struct Material
    {
        unsigned int ID;
        std::string name;
        std::vector<OpticalPoint> optical_curve;
    };

    struct PreparedMaterial
    {
        unsigned int ID;
        std::vector<Complex> refractive_indices;
    };

    struct Surface
    {
        std::string name;
        unsigned int Material_ID;
        double area; // mm^2
        Vec3 normal;
    };

    Complex get_cos_beta(double alpha, double n_I, Complex n_T);
    Complex get_r_perp(double n_I, Complex n_T, double alpha, Complex cos_beta);
    Complex get_r_parallel(double n_I, Complex n_T, double alpha, Complex cos_beta);

    class Solver
    {
    public:
        Solver(const std::vector<Surface>& surfaces, const std::vector<Material>& materials)
            : _materials(materials), _surfaces(surfaces) { }

        Solver(const std::vector<Surface>& surfaces, Vec3& k_i, const std::vector<Material>& materials)
            : _materials(materials), _surfaces(surfaces), _k_i(k_i) { }

        const Material& get_material(unsigned int material_ID) const;

        void prepare_solar_spectrum(const std::vector<SolarPoint>& solar_spectrum);

        const PreparedMaterial& get_prepared_material(unsigned int material_ID) const;

        Complex get_refractive_index(const Material& material, double wavelength_nm);

        double get_surface_R(const Surface& surface, std::size_t spectral_index);

        double get_surface_solar_R(const Surface& surface, const std::vector<SolarPoint>& solar_spectrum);
        
        double get_effective_solar_R(const std::vector<SolarPoint>& solar_spectrum);

        Vec3 k_i() const noexcept 
        { return this->_k_i; }

        const std::vector<Surface>& get_surfaces() const noexcept 
        { return this->_surfaces; }

        const std::vector<Material>& get_materials() const noexcept
        { return this->_materials; }

        void set_direction(const Vec3& direction)
        { this->_k_i = direction; }

    private:
        std::vector<Material> _materials;
        std::vector<Surface>  _surfaces;
        Vec3 _k_i;

        std::vector<PreparedMaterial> _prepared_materials;
    };
}