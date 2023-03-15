# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/geo_localization_dialog.py
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
from builtins import str
import platform
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtWidgets import QDialog, QToolTip
from qgis.PyQt.QtGui import QCursor, QFont
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import chooseExtentGeographicInformationDialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import geographicinformationPanel


class GeoLocalizationDialog(QDialog, chooseExtentGeographicInformationDialog.Ui_Dialog):
    def __init__(self, parent, coord=None):

        if not coord:
            coord = [0, 0, 0, 0, True]
        super(GeoLocalizationDialog, self).__init__(parent)
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)

        self.check_haveresources.setChecked(coord[4])
        self.setModal(True)
        self.btn_cancel.clicked.connect(lambda: self.done(QDialog.Rejected))
        self.btn_add.clicked.connect(lambda: self.done(QDialog.Accepted))
        self.spin_west_limit.setValue(float(str(coord[0]).replace(",", ".")))
        self.spin_east_limit.setValue(float(str(coord[1]).replace(",", ".")))
        self.spin_north_limit.setValue(float(str(coord[2]).replace(",", ".")))
        self.spin_south_south.setValue(float(str(coord[3]).replace(",", ".")))
        self.spin_west_limit.setDecimals(5)
        self.spin_east_limit.setDecimals(5)
        self.spin_north_limit.setDecimals(5)
        self.spin_south_south.setDecimals(5)
        self.superParent = None
        temp = self.parent()
        while self.superParent is None:
            if issubclass(type(temp), geographicinformationPanel.Ui_geographicinfo):
                self.superParent = temp
            else:
                temp = temp.parent()
        for info in self.findChildren(qwidgets.QPushButton, QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

    def get_data_list(self):
        return [self.spin_west_limit.text().strip(),
                self.spin_east_limit.text().strip(),
                self.spin_north_limit.text().strip(),
                self.spin_south_south.text().strip(),
                self.check_haveresources.isChecked()]

    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.superParent.helps['chooseExtentGeographicInformationDialog'][self.sender().objectName()]),
                          None)
