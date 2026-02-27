#include <iostream>
#include <vector>
#include <cmath>

#include <omp.h>


namespace part7{


    double sum(const std::vector<double>& values){

        double sum_result = 0.0;
        const auto N = values.size();
        #pragma omp parallel for reduction(+:sum_result) shared(values)
            for (int i=0; i<N; ++i){
                sum_result += values[i];
            }
        

        return sum_result;
    }

    double mean(const std::vector<double>& values){
        auto sum_vals = sum(values);
        return sum_vals / values.size();
    }

    double variance(const std::vector<double>& values){
       
        
        const auto N = values.size();

        auto mean_val = mean(values);

        double sum_result = 0.0;
        #pragma omp parallel for reduction(+:sum_result) shared(values, mean_val)
            for (auto i=0; i<N; ++i){
                auto diff = values[i] - mean_val;
                sum_result += diff * diff;
            }
        

        return sum_result / values.size();
    }

}


int main(){

    omp_set_num_threads(4);
    using namespace part7;
    std::vector<double> data(10000, 1.0);

    auto mu = mean(data);
    auto var = variance(data);
    std::cout<<"mean: "<<mu<<" variance: "<<var<<std::endl;

    return 0;
}