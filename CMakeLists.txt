cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(UHFMRTools)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/harellab/SlicerUHFMRTools")
set(EXTENSION_CATEGORY "Filtering")
set(EXTENSION_CONTRIBUTORS "Sam Brenny (CMRR), Henry Braun (CMRR)")
set(EXTENSION_DESCRIPTION "This extension provides tools for working with ultra-high field (UHF) MRI images and is intended to provide post-acquisition processing.")
set(EXTENSION_ICONURL "https://github.com/harellab/SlicerUHFMRTools/blob/trunk/ExtensionIcon.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/harellab/SlicerUHFMRTools/blob/trunk/doc/AdditionalModulePaths.png, https://github.com/harellab/SlicerUHFMRTools/blob/trunk/doc/FavoriteModules.png, https://github.com/harellab/SlicerUHFMRTools/blob/trunk/doc/ModuleWorkflow.png, https://github.com/harellab/SlicerUHFMRTools/blob/trunk/doc/ModuleResult.png")
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
