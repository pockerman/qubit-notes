#include <iostream>
#include <vector>
#include <cmath>

#include <omp.h>


namespace part7{


    double sum(const std::vector<double>& values){

        double sum_result = 0.0;
        const auto N = values.size();
        #pragma omp parallel for simd reduction(+:sum_result) shared(values)
            for (int i=0; i<N; ++i){
                sum_result += values[i];
            }
        

        return sum_result;
    }

    double mean(const std::vector<double>& values){
        auto sum_vals = sum(values);
        return sum_vals / values.size();
    }

}


int main(){

    omp_set_num_threads(4);
    using namespace part7;
    std::vector<double> data(10000, 1.0);

    auto mu = mean(data);
    std::cout<<"mean: "<<mu<<std::endl;

    return 0;
}