# -*- coding: utf-8 -*-

"""
***************************************************************************
    select_layer_dialog.py
    ---------------------
    Date                 : March 2023
    Copyright            : (C) 2023 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'March 2023'
__copyright__ = '(C) 2023, Alexander Bruy'


import os

from qgis.PyQt import uic

from qgis.core import QgsMapLayerProxyModel

from inspire_metadata_editor.constants import PLUGIN_ROOT


WIDGET, BASE = uic.loadUiType(os.path.join(PLUGIN_ROOT, "ui", "select_layer_dialog.ui"))


class SelectLayerDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.cmb_layer.setAllowEmptyLayer(True)
        #self.cmb_layer.setFilters(QgsMapLayerProxyModel.All)

    def layer(self):
        return self.cmb_layer.currentLayer()

