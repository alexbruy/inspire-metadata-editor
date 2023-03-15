# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/service_operation_inline.py
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
import platform
from qgis.PyQt.QtCore import QRegExp, Qt
from qgis.PyQt.QtWidgets import QWidget, QPushButton, QToolTip, QComboBox, QMessageBox, QDateTimeEdit
from qgis.PyQt.QtGui import QCursor, QIcon, QPalette, QFont
from qgis._gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import operationInlinePanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBox
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo


class InlineServiceOperation(QWidget, operationInlinePanel.Ui_operations):
    def __init__(self, parent):
        super(InlineServiceOperation, self).__init__(parent)
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)

        self.parent = parent
        self.superParent = parent.superParent

        self.combo_items_dcp = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["DCPCodeList"])

        tla.setupListView(self.dcp, CustomComboBox, self, comboList=list(self.combo_items_dcp.values()), NoParent=True)
        tla.setupListView(self.connectionPoint, QgsFilterLineEdit, self, NoParent=True)
        tla.setupMandatoryField(None, self.operationName, self.label_operationName, u"Elemento Obrigatório.", )
        tla.setupMandatoryField(None, self.dcp, self.label_dcp, u"Obrigatório conter pelo menos uma entrada")
        tla.setupMandatoryField(None, self.connectionPoint, self.label_connectionPoint, u"Obrigatório conter pelo menos uma entrada")

        for btn in self.findChildren(QPushButton, QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
        for info in self.findChildren(QPushButton, QRegExp('info_*')):
                     info.setIcon(QIcon(':/resourcesFolder/icons/help_icon.svg'))
                     info.setText('')
                     info.pressed.connect(self.printHelp)
        self.operationName.editingFinished.connect(self.update_title)
        self.update_title()
        self.btn_del_operation.setToolTip(u"Agagar Operação.")
        self.eater = tla.EatWheel()
        for x in self.findChildren(QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        self.btn_del_operation.clicked.connect(self.deleteOperation)
        self.dcp.model().dataChanged.connect(self.update_title)
        self.connectionPoint.model().dataChanged.connect(self.update_title)
        self.combo_dcp.setCurrentIndex(self.combo_dcp.findText("WebServices"))

    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['operationInlinePanel'][self.sender().objectName()]), None)

    def update_title(self):
        if self.operationName.text().strip() == '':
            palette = QPalette()
            palette.setColor(QPalette.Text, Qt.red)
            self.operation_gbox.setPalette(palette)
            self.operation_gbox.setTitle(u"O Nome da Operação não está definido.")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Text, Qt.black)
            self.operation_gbox.setPalette(palette)
            self.operation_gbox.setTitle(self.operationName.text())
        self.parent.check_operations_completness()

    def deleteOperation(self):
        message = QMessageBox()
        message.setModal(True)
        message.setWindowTitle(u'Remover operação?')
        message.setIcon(QMessageBox.Warning)
        message.setText(u"Tem a certeza que pretende remover a operação?")
        message.addButton(u'Remover', QMessageBox.AcceptRole)
        message.addButton(u'Cancelar', QMessageBox.RejectRole)
        ret = message.exec_()
        if ret == QMessageBox.AcceptRole:
            self.parent.remove_operation(self)
        else:
            return

    def isComplete(self):
        if self.operationName.text().strip() != '' and self.dcp.model().rowCount() > 0 and self.connectionPoint.model().rowCount() > 0:
            return True
        else:
            return False

    def get_data(self):
        return [self.operationName.text(), self.dcp.model().get_all_items(), self.connectionPoint.model().get_all_items()]

    def set_data(self, name, dcpList, connectionPointList):
        self.operationName.setText(name)
        for dcp in dcpList:
            if self.combo_items_dcp.get(dcp) is not None:
                self.dcp.model().addNewRow(self.combo_items_dcp.get(dcp))
            else:
                self.dcp.model().addNewRow(customCombo.CodeListItem(dcp, dcp, dcp))

        for c in connectionPointList:
            self.connectionPoint.model().addNewRow(c)
