# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

set(air_modes_sources
    preamble_impl.cc
    slicer_impl.cc
    modes_crc.cc
)

set(air_modes_sources "${air_modes_sources}" PARENT_SCOPE)

add_library(gnuradio-air_modes SHARED
    ${air_modes_sources}
)
target_link_libraries(gnuradio-air_modes gnuradio::gnuradio-runtime)
target_include_directories(gnuradio-air_modes
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
    PUBLIC $<INSTALL_INTERFACE:include>
  )

set_target_properties(gnuradio-air_modes PROPERTIES DEFINE_SYMBOL "AIR_MODES_EXPORTS")
set_target_properties(gnuradio-air_modes PROPERTIES SOVERSION "${VERSION_MAJOR}")
set_target_properties(gnuradio-air_modes PROPERTIES VERSION "${VERSION_MAJOR}.${VERSION_MINOR}")

if(APPLE)
    set_target_properties(gnuradio-air_modes PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-air_modes)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")
