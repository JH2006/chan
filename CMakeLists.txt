cmake_minimum_required(VERSION 3.22)

project(Engine)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAkE_CXX_FLAGS "$ENV{CXXFLAGS} -rdynamic -g -std=c++11")

set(LIB_SRC ./src/log.cpp)
# add_library(log STATIC ${LIB_SRC})

# include_directories(./leetcode)
# include_directories(./include)
include_directories(./tests) 

# link_directories(./lib/gtest)

aux_source_directory(./src SRC)
aux_source_directory(./src/utility UTL) 

add_executable(test ./tests/test.cpp ./tests/tcpserv01.cpp ./tests/tcpserv02.cpp)
# add_dependencies(test log)
# target_link_libraries(test log)

SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
SET(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib) 