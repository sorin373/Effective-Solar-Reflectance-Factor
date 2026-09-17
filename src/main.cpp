#include <iostream>
#include <algorithm>
#include <random>

#include "../include/solver.hpp"

#define SOLAR_SPECTRUM_DATA          "data/E490_AM0.csv"
#define AlUMINIUM_OPTICAL_CURVE_DATA "data/Rakic_Al.csv"

using namespace sim;

Vec3 random_dir(std::mt19937& gen)
{
    std::uniform_real_distribution<double> dist_u(-1.0, 1.0);
    std::uniform_real_distribution<double> dist_phi(0.0, 2.0 * PI);

    double u = dist_u(gen), phi = dist_phi(gen),
        r = std::sqrt(1.0 - u * u);

    return {r * std::cos(phi), r * std::sin(phi), u};
}

double projected_area(const std::vector<Surface>& surfaces, const Vec3& k)
{
    double A = 0.0;

    for (const Surface& surface : surfaces)
    {
        double c = -dot(k, surface.normal);

        if (c > 0.0)
            A += surface.area * c;
    }

    return A;
}

struct Result
{
    double mean;
    double std_dev;

    double p05;
    double median;
    double p95;

    double standard_error;
};

std::ofstream convergents("results/convergence.csv");

Result run_monte_carlo(Solver &solver, const std::vector<SolarPoint> &solar_spectrum, unsigned int N, unsigned int seed)
{
    std::ofstream csv("results/final_samples.csv");
    csv << "sample,kx,ky,kz,q,A_proj,force_factor\n";

    std::mt19937 gen(seed);

    std::vector<double> values;
    values.reserve(N);

    double sum = 0.0, sum2 = 0.0;

    for (unsigned int i = 0; i < N; ++i)
    {
        Vec3 k_i = random_dir(gen);

        solver.set_direction(k_i);

        double R_eff = solver.get_effective_solar_R(solar_spectrum);
        double A_proj = projected_area(solver.get_surfaces(), k_i);
        double force_factor = A_proj * (1.0 + R_eff);

        values.push_back(R_eff);
        
        sum += R_eff;
        sum2 += R_eff * R_eff;

        csv << i << ',' << k_i.x << ',' << k_i.y << ',' << k_i.z << ',' << R_eff << ',' << A_proj << ',' << force_factor << '\n';
    }

    csv.close();

    std::sort(values.begin(), values.end());

    double mean = sum / static_cast<double>(N);
    double variance = (sum2 - static_cast<double>(N) * mean * mean) / static_cast<double>(N - 1);
    double std_dev = std::sqrt(variance);
    double std_error = std_dev / std::sqrt(static_cast<double>(N));

    unsigned int i05 = static_cast<unsigned int>(0.05 * (N - 1));
    unsigned int i50 = static_cast<unsigned int>(0.50 * (N - 1));
    unsigned int i95 = static_cast<unsigned int>(0.95 * (N - 1));

    convergents << N << "," << mean << "," << std_dev << "," << values[i05] << "," << values[i50] << "," << values[i95] << '\n';

    return {mean, std_dev, values[i05], values[i50], values[i95], std_error};
}

int main()
{
    std::vector<OpticalPoint> aluminum_curve = load_optical_curve(AlUMINIUM_OPTICAL_CURVE_DATA);
    std::vector<SolarPoint>   solar_spectrum = load_solar_spectrum(SOLAR_SPECTRUM_DATA, 250.0, 2500.0);

    const std::vector<Material> materials = {
        {1, "Al-5005-H14", aluminum_curve},
        {2, "Al-6082-T651", aluminum_curve},
        {3, "Al-6061-T6", aluminum_curve},
        {
            4,
            "CMG-100-Glass-Cover",
            {
                {250.0,  1.516, 0.0},
                {500.0,  1.516, 0.0},
                {1000.0, 1.516, 0.0},
                {1500.0, 1.516, 0.0},
                {2000.0, 1.516, 0.0},
                {2500.0, 1.516, 0.0}
            }
        },
        {5, "Al-7075-T6", aluminum_curve}
    };

    const std::vector<Surface> surfaces = {
        {"Main Back Plate", 3, 18472.4801 - 7380.0363 - 6361.2203, dir::PY},

        {"Back Plate (COM)", 1, 7380.0363, dir::PY},
        {"Shield (COM)", 2, 6361.2203, dir::PY},
        {"Side Rail", 5, 2538.75 * 2, dir::PY},
        {"OAB", 3, 1977.1523, dir::PY},

        {"Side Rail", 5, 2538.75 * 2, dir::PX},
        {"OAB", 3, 1977.1523, dir::PX},
        {"Fixed Solar Cells (FSC)", 4, 3017.75 * 7, dir::PX},
        {"Deployable Solar Cells (DSC)", 4, 3017.75 * 12, dir::PX},
        {"Back Plate (FSC)", 1, 25060.1199 - 3017.75 * 7, dir::PX},
        {"Back Plate (DSC)", 2, 2 * 23210.7363 - 3017.75 * 12, dir::PX},

        {"Side Rail", 5, 2538.75 * 2, dir::NY},
        {"OAB", 3, 1977.1523, dir::NY},
        {"Back Plate", 2, 23004.8134, dir::NY},

        {"Side Rail", 5, 2538.75 * 2, dir::NX},
        {"OAB", 3, 1977.1523, dir::NX},
        {"FSC", 4, 3017.75 * 7, dir::NX},
        {"Back Plate (FSC)", 1, 25060.1199 - 3017.75 * 7, dir::NX},
        {"Back Plate (DSC)", 2, 23004.8134 * 2, dir::NX},

        {"Chorus Shield", 2, 8478.2977, dir::PZ},

        {"Top Frame + Camera housing", 3, 1975.8099 + 6653.7694, dir::NZ}
    };

    Solver solver(surfaces, materials);
    solver.prepare_solar_spectrum(solar_spectrum);

    const unsigned int seed = 12345;

    convergents << "N,mean,std,p05,median,p95\n";

    for (const unsigned int N : {10, 100, 1000, 10000, 100000})
    {
        Result result = run_monte_carlo(solver, solar_spectrum, N, seed);
    
        std::cout << "N = " << N << '\n';
        std::cout << "Mean R = " << result.mean << '\n';
        std::cout << "Std dev = " << result.std_dev << '\n';
        std::cout << "P05 = " << result.p05 << '\n';
        std::cout << "Median = " << result.median << '\n';
        std::cout << "P95 = " << result.p95 << '\n';
        std::cout << "Standard error of mean = " << result.standard_error << '\n';
        std::cout << "===========================================================\n\n";
    }

    std::vector<std::pair<std::string, Vec3>> test_dirs = {
        {"+X face illuminated", {-1.0,  0.0,  0.0}},
        {"-X face illuminated", { 1.0,  0.0,  0.0}},
        {"+Y face illuminated", { 0.0, -1.0,  0.0}},
        {"-Y face illuminated", { 0.0,  1.0,  0.0}},
        {"+Z face illuminated", { 0.0,  0.0, -1.0}},
        {"-Z face illuminated", { 0.0,  0.0,  1.0}}
    };

    std::cout << "\n===== PRINCIPAL DIRECTIONS =====\n";

    for (const std::pair<std::string, Vec3>& item : test_dirs)
    {
        const std::string& name = item.first;
        const Vec3& k = item.second;

        solver.set_direction(k);

        double R_eff = solver.get_effective_solar_R(solar_spectrum);

        std::cout << name << " : q = " << R_eff << '\n';
    }

    convergents.close();

    return 0;
}