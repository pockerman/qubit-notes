cmake_minimum_required(VERSION 3.29)
project(part_1)

SET(EXECUTABLE  main)
SET(SOURCE ${EXECUTABLE}.cpp)
SET(CMAKE_CXX_STANDARD 23)

ADD_EXECUTABLE(${EXECUTABLE} ${SOURCE})

target_link_options(${EXECUTABLE} PRIVATE -fopenmp)
