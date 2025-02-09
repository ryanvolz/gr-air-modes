#
# Copyright 2008,2009 Free Software Foundation, Inc.
# 
# This application is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio gr-air-modes package. It provides a library and
application for receiving Mode S / ADS-B signals from aircraft. Use
modes_rx as the main application for receiving signals. cpr.py
provides an implementation of Compact Position Reporting. altitude.py
implements Gray-coded altitude decoding. Various plugins exist for SQL,
KML, and PlanePlotter-compliant SBS-1 emulation output. mlat.py provides
an experimental implementation of a multilateration solver.
'''

from .air_modes_python import *

# import any pure python here
#

try:
    import zmq
except ImportError:
    raise RuntimeError("PyZMQ not found! Please install libzmq and PyZMQ to run gr-air-modes")

from .rx_path import rx_path
from .zmq_socket import zmq_pubsub_iface
from .parse import *
from .msprint import output_print
from .sql import output_sql
from .sbs1 import output_sbs1
from .kml import output_kml, output_jsonp
from .raw_server import raw_server
from .radio import modes_radio
from .exceptions import *
from .modes_types import *
from .altitude import *
from .cpr import cpr_decoder
from .html_template import html_template
from .msgq_runner import msgq_runner

#this is try/excepted in case the user doesn't have numpy installed
try:
    from .flightgear import output_flightgear
    from .Quaternion import *
except ImportError:
    print("gr-air-modes warning: numpy+scipy not installed, FlightGear interface not supported")
    pass
