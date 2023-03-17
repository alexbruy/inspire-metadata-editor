# -*- coding: utf-8 -*-

"""
***************************************************************************
    add_organization_dialog.py
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

from inspire_metadata_editor.constants import PLUGIN_ROOT


WIDGET, BASE = uic.loadUiType(os.path.join(PLUGIN_ROOT, "ui", "add_organization_dialog.ui"))


class AddOrganizationDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def short_name(self):
        return self.le_short_name.text()

    def full_name(self):
        return self.txt_full_name.toPlainText()
