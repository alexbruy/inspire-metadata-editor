# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/metadadoSNIMar.py
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
from qgis.PyQt import QtGui as qgui, QtCore as qcore
import os
import platform
from qgis.utils import pluginDirectory
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QFont, QColor, QIcon
from qgis.PyQt.QtWidgets import QWidget, QListWidget, QPushButton, QGridLayout, QListWidgetItem, QStackedWidget
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
import EditorMetadadosMarswInforbiomares.CONSTANTS as cons
from EditorMetadadosMarswInforbiomares import snimarEditorController
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel


class MetadadoSNIMar(QWidget):
    def __init__(self, parent, scope=None, xml_doc=None, md=None):
        super(MetadadoSNIMar, self).__init__(parent)
        if scope is None:
            self.scope = SCOPES.get_code_representation(md.hierarchy)
        else:
            self.scope = scope

        self.current_index = 0
        self.widgetStalker = {}
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)

        self.sidelist = QListWidget(self)
        self.sidelist.setMinimumWidth(150)
        self.sidelist.setMaximumWidth(150)
        self.sidelist.setWordWrap(True)
        self.sidelist.setTextElideMode(Qt.ElideNone)
        self.sidelist.setIconSize(QSize(25, 25))
        self.sidelist.clicked.connect(self.list_clicked)
        index = 0
        if self.scope == SCOPES.SERVICES:
            tabs = cons.TABLIST_SERVICES
        else:
            tabs = cons.TABLIST_CDG_SERIES

        for tab_element in tabs:
            bufWidget = QListWidgetItem(qgui.QIcon(':/resourcesFolder/icons/' + tab_element[1]), tab_element[0])
            self.widgetStalker[tab_element[2]] = {"widget": bufWidget,
                                                  "missingFields": set(),
                                                  "incompleteEntries": set()}
            bufWidget.setSizeHint(QSize(150, 50))
            if platform.system() != "Linux":
                font = QFont()
                font.setFamily(u"Segoe UI Symbol")
                bufWidget.setFont(font)

            self.sidelist.insertItem(index, bufWidget)
            index += 1
        self.widgetstack = QStackedWidget(self)

        # Setup metadata stuff
        self.xml_doc = xml_doc
        self.is_new_file = True if xml_doc is None else False
        self.md = md
        self.codelist = self.parent().codelists
        self.helps = self.parent().helps
        self.orgs = self.parent().orgs
        f = open(os.path.join(pluginDirectory('EditorMetadadosMarswInforbiomares'), 'resourcesFolder/stylesheet.qtcss'))
        self.sytlesheet = f.read()
        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet(self.sytlesheet)
            btn.setFocusPolicy(Qt.NoFocus)
        self.reference_systems_list = self.parent().reference_systems
        tab_list = []

        # Setup snimarEditorController
        self.identification = snimarEditorController.IdentificationWidget(self, self.scope)
        tab_list.append(self.identification)
        if self.scope == SCOPES.SERVICES:
            self.operations = snimarEditorController.ServiceOperationsWidget(self)
            tab_list.append(self.operations)
        self.keywords = snimarEditorController.KeywordsWidget(self, self.scope)
        tab_list.append(self.keywords)
        self.geographicinfo = snimarEditorController.GeographicInfoWidget(self, self.scope)
        tab_list.append(self.geographicinfo)
        self.temporalinfo = snimarEditorController.TemporalInfoWidget(self, self.scope)
        tab_list.append(self.temporalinfo)
        self.quality = snimarEditorController.QualityWidget(self,self.scope)
        tab_list.append(self.quality)
        self.restrictions = snimarEditorController.RestrictionsWidget(self, self.scope)
        tab_list.append(self.restrictions)
        self.distribution = snimarEditorController.DistributionWidget(self, self.scope)
        tab_list.append(self.distribution)
        self.metadata = snimarEditorController.MetadataWidget(self)
        tab_list.append(self.metadata)

        self.setupUi()
        if not self.is_new_file:
            # Setup data
            self.identification.set_data(self.md)
            if self.scope == SCOPES.SERVICES:
                self.operations.set_data(md)
            self.temporalinfo.set_data(self.md)
            self.keywords.set_data(self.md)
            self.metadata.set_data(self.md)
            self.distribution.set_data(self.md)
            self.restrictions.set_data(self.md)
            self.quality.set_data(self.md)
            self.geographicinfo.set_data(self.md)

    def setupUi(self):
        self.widgetstack.addWidget(self.identification)
        if self.scope == SCOPES.SERVICES:
            self.widgetstack.addWidget(self.operations)
        self.widgetstack.addWidget(self.keywords)
        self.widgetstack.addWidget(self.geographicinfo)
        self.widgetstack.addWidget(self.temporalinfo)
        self.widgetstack.addWidget(self.quality)
        self.widgetstack.addWidget(self.restrictions)
        self.widgetstack.addWidget(self.distribution)
        self.widgetstack.addWidget(self.metadata)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.sidelist, 0, 0, 1, 1)
        self.grid.addWidget(self.widgetstack, 0, 1, 1, 1)
        self.setLayout(self.grid)
        self.widgetstack.setCurrentIndex(0)

    @qcore.pyqtSlot()
    def list_clicked(self):
        index = self.sidelist.currentRow()
        if index != self.current_index:
            self.widgetstack.setCurrentIndex(index)
            self.current_index = index

    def get_tab_data(self, md):
        if self.scope != SCOPES.SERVICES:
            md.identification = snimarProfileModel.MD_DataIdentification()
        else:
            md.serviceidentification = snimarProfileModel.SV_ServiceIdentification()

        self.identification.get_data(md)
        if self.scope == SCOPES.SERVICES:
            self.operations.get_data(md)
        self.keywords.get_data(md)
        self.geographicinfo.get_data(md)
        self.temporalinfo.get_data(md)
        self.quality.get_data(md)
        self.restrictions.get_data(md)
        self.distribution.get_data(md)
        self.metadata.get_data(md)

    # ------------------------------------------------------------------------
    #                    Validation STUFF
    # ------------------------------------------------------------------------

    def is_doc_Snimar_Valid(self):
        for x in list(self.widgetStalker.values()):
            if len(x["missingFields"]) > 0 or len(x["incompleteEntries"]) > 0:
                return False

        return True

    def register_mandatory_missingfield(self, widgetName, fieldName):
        self.widgetStalker[widgetName]["missingFields"].add(fieldName.replace(u'\u26a0', '').strip())
        self.widgetStalker[widgetName]["widget"].setToolTip(self.genToolTip(widgetName))
        self.widgetStalker[widgetName]["widget"].setForeground(QColor(cons.ERROR_COLOR))

        self.widgetStalker[widgetName]["widget"].setText(
            self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', '') + u'\u26a0')

    def unregister_mandatory_missingfield(self, widgetName, fieldName):
        self.widgetStalker[widgetName]["missingFields"].discard(fieldName)
        if len(self.widgetStalker[widgetName]["incompleteEntries"]) != 0 or len(self.widgetStalker[widgetName]["missingFields"]) != 0:
            self.widgetStalker[widgetName]["widget"].setText(
                self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', '') + u'\u26a0')
        else:
            self.widgetStalker[widgetName]["widget"].setForeground(QColor("black"))
            self.widgetStalker[widgetName]["widget"].setText(self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', ''))

        self.widgetStalker[widgetName]["widget"].setToolTip(self.genToolTip(widgetName))

    def register_incomplete_entries(self, widgetName, fieldName):
        self.widgetStalker[widgetName]["incompleteEntries"].add(fieldName.replace(u'\u26a0', '').strip())
        self.widgetStalker[widgetName]["widget"].setToolTip(self.genToolTip(widgetName))
        self.widgetStalker[widgetName]["widget"].setForeground(QColor(cons.ERROR_COLOR))
        self.widgetStalker[widgetName]["widget"].setText(self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', '') + u'\u26a0')

    def unregister_incomplete_entries(self, widgetName, fieldName):
        self.widgetStalker[widgetName]["incompleteEntries"].discard(fieldName)
        if len(self.widgetStalker[widgetName]["incompleteEntries"]) != 0 or len(self.widgetStalker[widgetName]["missingFields"]) != 0:
            self.widgetStalker[widgetName]["widget"].setText(
                self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', '') + u'\u26a0')
        else:
            self.widgetStalker[widgetName]["widget"].setForeground(QColor("black"))
            self.widgetStalker[widgetName]["widget"].setText(self.widgetStalker[widgetName]["widget"].text().replace(u'\u26a0', ''))
        self.widgetStalker[widgetName]["widget"].setToolTip(self.genToolTip(widgetName))

    def genToolTip(self, widgetName):
        tooltip = ""
        if len(self.widgetStalker[widgetName]["missingFields"]) > 0:
            tooltip += u"Campos Obrigatórios\nem falta:\n-" + "\n-".join(self.widgetStalker[widgetName]["missingFields"])
        if len(self.widgetStalker[widgetName]["missingFields"]) > 0 and len(self.widgetStalker[widgetName]["incompleteEntries"]) > 0:
            tooltip += u"\n---------------------\n"
        if len(self.widgetStalker[widgetName]["incompleteEntries"]) > 0:
            tooltip += u"Campos Incompletos\Incorrectos:\n-" + "\n-".join(self.widgetStalker[widgetName]["incompleteEntries"])
        tooltip += u"\n---------------------\n"
        return tooltip + u"\nA Conformidade diz respeito\n" \
                         u"as obrigações de formato " \
                         u"\ne completude do documento.\n" \
                         u"A validade do conteúdo é da\n" \
                         u"inteira responsabilidade\n" \
                         u"do utilizador. "


def vality_msg(validity):
    if validity:
        return u"Conforme Perfil SNIMar"
    else:
        return u"Não Conforme Perfil SNIMar"
