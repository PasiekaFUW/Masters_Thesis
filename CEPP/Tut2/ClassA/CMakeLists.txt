cmake_minimum_required(VERSION 3.10)
project(ClassA)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")

# Define the executable
add_executable(myApplication
    ClassA.cc
    main.cc
)

# Include directories
target_include_directories(myApplication PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
