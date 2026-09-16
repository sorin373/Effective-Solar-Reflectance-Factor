#include "solver.hpp"

#include <vector>
#include <fstream>
#include <random>

namespace sim
{
    std::vector<OpticalPoint> load_optical_curve(const char *filename)
    {
        std::ifstream file(filename);

        if (!file.is_open())
            throw std::runtime_error("Could not open optical data file!\n");

        std::vector<OpticalPoint> curve;
        
        char line[256] = {'\0'};

        file.getline(line, 256);

        while (file.getline(line, 256))
        {
            char *token = strtok(line, ",");
            double wavelength_um = static_cast<double>(std::atof(token));

            token = strtok(NULL, ",");
            double n = static_cast<double>(std::atof(token));

            token = strtok(NULL, ",");
            double kappa = static_cast<double>(std::atof(token));

            curve.push_back({wavelength_um * 1000.0, n, kappa});
        }

        if (curve.empty())
            throw std::runtime_error("No optical data loaded!\n");

        return curve;
    }

    std::vector<SolarPoint> load_solar_spectrum(const char *filename, double lambda_min_nm, double lambda_max_nm)
    {
        std::ifstream file(filename);

        if (!file.is_open())
            throw std::runtime_error("Could not open solar spectrum file!\n");

        std::vector<SolarPoint> spectrum;

        char line[256] = {'\0'};

        file.getline(line, 256);

        while (file.getline(line, 256))
        {   
            char *token = strtok(line, ",");
            double wavelength_nm = static_cast<double>(std::atof(token));

            token = strtok(NULL, ",");
            double irradiance = static_cast<double>(std::atof(token));

            if (wavelength_nm < lambda_min_nm || wavelength_nm > lambda_max_nm)
                continue;

            spectrum.push_back({wavelength_nm, irradiance});
        }

        if (spectrum.size() < 2)
            throw std::runtime_error("Not enough solar spectrum points loaded.");

        return spectrum;
    }

    double dot(const Vec3 &a, const Vec3 &b)
    { return a.x * b.x + a.y * b.y + a.z * b.z; }

    Complex get_cos_beta(double alpha, double n_I, Complex n_T)
    {
        Complex sin_beta = (n_I / n_T) * std::sin(alpha);
        Complex cos_beta = std::sqrt(Complex{1.0, 0.0} - sin_beta * sin_beta);
        Complex q = n_T * cos_beta;

        if (q.imag() < 0.0 || (q.imag() == 0.0 && q.real() < 0.0))
            cos_beta = -cos_beta;

        return cos_beta;
    }

    Complex get_r_perp(double n_I, Complex n_T, double alpha, Complex cos_beta)
    { return (n_I * std::cos(alpha) - n_T * cos_beta) / (n_I * std::cos(alpha) + n_T * cos_beta); }

    Complex get_r_parallel(double n_I, Complex n_T, double alpha, Complex cos_beta)
    { return (n_T * std::cos(alpha) - n_I * cos_beta) / (n_T * std::cos(alpha) + n_I * cos_beta); }

    const Material& Solver::get_material(unsigned int material_ID) const
    {
        for (const Material& material : _materials)
            if (material.ID == material_ID)
                return material;

        throw std::runtime_error("Material ID not found: " + std::to_string(material_ID));
    }

    void Solver::prepare_solar_spectrum(const std::vector<SolarPoint>& solar_spectrum)
    {
        _prepared_materials.clear();
        _prepared_materials.reserve(_materials.size());

        for (const Material& material : _materials)
        {
            PreparedMaterial prepared;

            prepared.ID = material.ID;
            prepared.refractive_indices.reserve(solar_spectrum.size());

            for (const SolarPoint& point : solar_spectrum)
                prepared.refractive_indices.push_back(get_refractive_index(material, point.wavelength_nm));

            _prepared_materials.push_back(std::move(prepared));
        }
    }

    const PreparedMaterial& Solver::get_prepared_material(unsigned int material_ID) const
    {
        for (const PreparedMaterial& material : _prepared_materials)
            if (material.ID == material_ID)
                return material;

        throw std::runtime_error("Prepared material not found: " + std::to_string(material_ID));
    }

    Complex Solver::get_refractive_index(const Material& material, double wavelength_nm)
    {
        const std::vector<OpticalPoint>& curve = material.optical_curve;

        if (curve.empty())
            throw std::runtime_error("Empty optical curve.");

        if (wavelength_nm < curve.front().wavelength_nm || wavelength_nm > curve.back().wavelength_nm)
            throw std::runtime_error("Requested wavelength outside optical curve range.");

        for (std::size_t i = 0, N = curve.size(); i + 1 < N; ++i)
        {
            const OpticalPoint& a = curve[i], b = curve[i + 1];
            
            if (wavelength_nm >= a.wavelength_nm && wavelength_nm <= b.wavelength_nm)
            {
                double t = (wavelength_nm - a.wavelength_nm) / (b.wavelength_nm - a.wavelength_nm);
                double n = a.n + t * (b.n - a.n);
                double kappa = a.kappa + t * (b.kappa - a.kappa);

                return Complex{n, kappa};
            }
        }

        throw std::runtime_error("Interpolation failed.");
    }

    double Solver::get_surface_R(const Surface& surface, std::size_t spectral_index)
    {
        double cos_alpha_i = -dot(this->_k_i, surface.normal);

        if (cos_alpha_i <= 0.0)
            return 0;

        const PreparedMaterial& material = get_prepared_material(surface.Material_ID);

        double alpha = std::acos(cos_alpha_i);

        Complex n_T = material.refractive_indices[spectral_index];

        const double n_I = 1.0;

        Complex cos_beta = get_cos_beta(alpha, n_I, n_T),
                  r_perp = get_r_perp(n_I, n_T, alpha, cos_beta),
              r_parallel = get_r_parallel(n_I, n_T, alpha, cos_beta);

        return 0.5 * (std::norm(r_perp) + std::norm(r_parallel));
    }

    double Solver::get_surface_solar_R(const Surface& surface, const std::vector<SolarPoint>& solar_spectrum)
    {
        if (solar_spectrum.size() < 2)
            throw std::runtime_error("Solar spectrum needs at least 2 points.");

        double numerator = 0.0, denominator = 0.0;
        double R_a = get_surface_R(surface, 0);

        for (std::size_t i = 0, N = solar_spectrum.size(); i + 1 < N; ++i)
        {
            const SolarPoint& a = solar_spectrum[i], b = solar_spectrum[i + 1];

            double dlambda = b.wavelength_nm - a.wavelength_nm;

            if (dlambda <= 0.0)
                throw std::runtime_error("Solar spectrum wavelengths must be increasing.");

            double R_b = get_surface_R(surface, i + 1);
            double numerator_a = a.irradiance * R_a, numerator_b = b.irradiance * R_b;

            // trapezoidal integration
            numerator += 0.5 * (numerator_a + numerator_b) * dlambda;
            denominator += 0.5 * (a.irradiance + b.irradiance) * dlambda;

            R_a = R_b;
        }

        if (denominator == 0.0)
            throw std::runtime_error("Solar spectrum integral is zero.");

        return numerator / denominator;
    }

    double Solver::get_effective_solar_R(const std::vector<SolarPoint>& solar_spectrum)
    {
        double numerator = 0.0, denominator = 0.0;

        for (const Surface& surface : _surfaces)
        {
            double cos_alpha = -dot(_k_i, surface.normal);

            if (cos_alpha <= 0.0)
                continue;

            double R_solar = get_surface_solar_R(surface, solar_spectrum);

            numerator += R_solar * surface.area * cos_alpha;
            denominator += surface.area * cos_alpha;
        }

        if (denominator == 0.0)
            return 0.0;

        return numerator / denominator;
    }
}
