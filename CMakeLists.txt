cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BackgroundNoiseSupression)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/BackgroundNoiseSupression")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Sam Brenny (CMRR), Henry Braun (CMRR)")
set(EXTENSION_DESCRIPTION "provides background noise filtering for MP2RAGE acquisition")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/BackgroundNoiseSupression.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/BackgroundNoiseSupression/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BackgroundNoiseSupression)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
