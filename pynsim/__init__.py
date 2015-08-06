#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
level = 'INFO'

if os.name == "nt":
   logging.addLevelName( logging.INFO, logging.getLevelName(logging.INFO))
   logging.addLevelName( logging.DEBUG, logging.getLevelName(logging.DEBUG))
   logging.addLevelName( logging.WARNING, logging.getLevelName(logging.WARNING))
   logging.addLevelName( logging.ERROR, logging.getLevelName(logging.ERROR))
   logging.addLevelName( logging.CRITICAL, logging.getLevelName(logging.CRITICAL))
   logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=level)
else:
   logging.addLevelName( logging.INFO, "\033[0;m%s\033[0;m" % logging.getLevelName(logging.INFO))
   logging.addLevelName( logging.DEBUG, "\033[0;32m%s\033[0;32m" % logging.getLevelName(logging.DEBUG))
   logging.addLevelName( logging.WARNING, "\033[0;33m%s\033[0;33m" % logging.getLevelName(logging.WARNING))
   logging.addLevelName( logging.ERROR, "\033[0;31m%s\033[0;31m" % logging.getLevelName(logging.ERROR))
   logging.addLevelName( logging.CRITICAL, "\033[0;35m%s\033[0;35m" % logging.getLevelName(logging.CRITICAL))

   logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s\033[0m', level=level)



from components import Network, Node, Link, Institution
from engines import Engine
from simulators import Simulator
