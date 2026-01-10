#include <iostream>
#include <omp.h>

// TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
int main()
{
  // TIP Press <shortcut actionId="RenameElement"/> when your caret is at the <b>lang</b> variable name to see how CLion can help you rename it.
  auto lang = "C++";
  std::cout << "Hello and welcome to " << lang << "!\n";
  auto n_threads = omp_get_num_threads();
  auto thread_id = omp_get_thread_num();

  std::cout << "Number of threads: " << n_threads << std::endl;
  std::cout << "Thread ID: " << thread_id << std::endl;
  return 0;
}