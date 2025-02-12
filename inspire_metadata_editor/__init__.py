# -*- coding: utf-8 -*-

##############################################################################
#
#  Title:   __init__.py
#  Authors: Pedro Dias, Eduardo Castanho, Joana Teixeira
#  Date:    2015-08-11T16:14:20
#
# ---------------------------------------------------------------------------
#
#  XML metadata editor plugin for QGIS developed for the SNIMar Project.
#  Copyright (C) 2015  Eduardo Castanho, Pedro Dias, Joana Teixeira
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import json

from inspire_metadata_editor.plugin import InspireMetadataEditorPlugin

def classFactory(iface):
    return InspireMetadataEditorPlugin(iface)


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'version.json'), "r") as data_file:
        version = json.load(data_file)
    return ".".join([str(version["major"]), str(version["minor"]), str(version["revision"])])


__version__ = get_version()
