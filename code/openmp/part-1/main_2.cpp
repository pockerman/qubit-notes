#include <iostream>
#include <omp.h>


int main()
{

  // set number of threads
   omp_set_num_threads(4);

  #pragma omp parallel
  {
    auto n_threads = omp_get_num_threads();
     auto thread_id = omp_get_thread_num();

     std::cout << "Number of threads: " << n_threads << std::endl;
     std::cout << "Thread ID: " << thread_id << std::endl;
  }
 return 0;
}
