cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BackgroundNoiseSuppression)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/harellab/SlicerMp2rageBackgroundSuppression")
set(EXTENSION_CATEGORY "Filtering")
set(EXTENSION_CONTRIBUTORS "Sam Brenny (CMRR), Henry Braun (CMRR)")
set(EXTENSION_DESCRIPTION "provides background noise filtering for MP2RAGE acquisition")
set(EXTENSION_ICONURL "https://github.com/harellab/SlicerMp2rageBackgroundSuppression/blob/trunk/BackgroundNoiseSuppression.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/harellab/SlicerMp2rageBackgroundSuppression/blob/trunk/Screenshot1.png, https://github.com/harellab/SlicerMp2rageBackgroundSuppression/blob/trunk/Screenshot2.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BackgroundNoiseSuppression)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
