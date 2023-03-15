# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/snimarKeywordsDialog.py
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
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
import platform
from qgis.PyQt.QtCore import Qt, QModelIndex
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel, QFont
from qgis.PyQt.QtWidgets import QAbstractItemView, QSizePolicy, QLabel, QDialog

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import addSnimarKeyWordsDialog
from EditorMetadadosMarswInforbiomares.snimarProfileModel.snimarThesaurusBuilder import SnimarThesurusModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo


class SNIMARKeywordsDialog(QDialog, addSnimarKeyWordsDialog.Ui_Dialog):
    def __init__(self, parent, model_to_insert, snimar_keyword_types_list):
        super(SNIMARKeywordsDialog, self).__init__(parent)
        self.model_to_insert = model_to_insert
        self.combo_items_md_keywordtypecode = snimar_keyword_types_list
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)
        self.setModal(True)

        self.thesaurus_model = SnimarThesurusModel().get_Model()

        self.to_add_keywords = {}  # id : QStandartItem

        self.list_view_thesaurus.setModel(self.thesaurus_model)
        # TODO fix this
        self.thesaurus_model.itemChanged.connect(self.register_item)

        self.list_view_thesaurus.setAlternatingRowColors(True)
        self.list_view_thesaurus.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.list_view_thesaurus.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_view_thesaurus.setTextElideMode(Qt.ElideNone)
        self.list_view_thesaurus.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_view_thesaurus.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_view_thesaurus.setResizeGripsVisible(False)
        self.list_view_thesaurus.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.list_view_thesaurus.setColumnWidths([300, 300, 300, 0, 0, 0, 0, 0])
        self.list_view_thesaurus.setAutoScroll(True)
        label = QLabel('')
        label.setMaximumSize(0, 0)
        self.list_view_thesaurus.setPreviewWidget(label)
        label.hide()
        self.bt_add_selected.clicked.connect(self.add_keywords)
        self.btn_exit.clicked.connect(lambda: self.done(0))
        self.setSizeGripEnabled(True)
        self.resize(self.maximumSize())
        self.adjustSize()

    #@qcore.pyqtSlot(QStandardItem)
    def register_item(self, item):
        """
        :type item: QStandardItem
        """
        if item.checkState() == Qt.Checked:
            self.to_add_keywords[item.cc_uuid] = item
        else:
            self.to_add_keywords.pop(item.cc_uuid)

    def add_keywords(self):

        for x in list(self.to_add_keywords.values()):
            self.model_to_insert.addNewRow(
                [self.combo_items_md_keywordtypecode[x.kw_type], x.term, x.thesaurus_info['version'], x.thesaurus_info, x.cc_uuid],check_dup_on=[1,4])
            x.setCheckState(Qt.Unchecked)

    def update_thesaurus_model(self, stable=False):
        self.to_add_keywords.clear()
        self.thesaurus_model = SnimarThesurusModel(stable=stable).get_Model()
        self.list_view_thesaurus.setModel(self.thesaurus_model)
        self.thesaurus_model.itemChanged.connect(self.register_item)
