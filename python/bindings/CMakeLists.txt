# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT air_modes_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT air_modes_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND air_modes_python_files
    python_bindings.cc
    preamble_python.cc
    slicer_python.cc)

GR_PYBIND_MAKE_OOT(air_modes 
   ../..
   gr::air_modes
   "${air_modes_python_files}")

install(TARGETS air_modes_python DESTINATION ${GR_PYTHON_DIR}/air_modes COMPONENT pythonapi)
