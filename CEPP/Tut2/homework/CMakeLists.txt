cmake_minimum_required(VERSION 3.5)
project(geant4_example)

find_package(Geant4 REQUIRED ui_all vis_all)
include( ${Geant4_USE_FILE} )

add_executable(myApp main.cc)
target_link_libraries(myApp ${Geant4_LIBRARIES})
