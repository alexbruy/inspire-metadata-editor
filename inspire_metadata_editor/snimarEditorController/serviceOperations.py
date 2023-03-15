# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/serviceOperations.py
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
from qgis.PyQt.QtCore import Qt, QRegExp
from qgis.PyQt.QtWidgets import QWidget, QLabel, QPushButton, QToolTip
from qgis.PyQt.QtGui import QIcon, QCursor
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import serviceOperationsPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.service_operation_inline import InlineServiceOperation
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import unsetLabelRed


class ServiceOperationsWidget(QWidget, serviceOperationsPanel.Ui_operations):
    def __init__(self, parent):
        super(ServiceOperationsWidget, self).__init__(parent)
        self.setupUi(self)
        self.op_box.setAlignment(Qt.AlignTop)
        self.superParent = self.parent()
        self.operationList = []
        self.btn_add_operations.clicked.connect(self.add_operation)
        self.check_mandatory_operations()
        for btn in self.findChildren(QPushButton, QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                #  btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
        for info in self.findChildren(QPushButton, QRegExp('info_*')):
            info.setIcon(QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['serviceOperationsPanel'][self.sender().objectName()]),
                          None)

    def add_operation(self):
        to_add = InlineServiceOperation(self)
        self.op_box.insertWidget(0, to_add)
        self.op_box.setAlignment(Qt.AlignTop)
        self.operationList.append(to_add)
        self.check_mandatory_operations()
        self.check_operations_completness()

    def remove_operation(self, operation):
        self.op_box.removeWidget(operation)
        self.operationList.remove(operation)
        operation.close()
        self.check_mandatory_operations()
        self.check_operations_completness()

    def check_mandatory_operations(self):
        if self.op_box.count() == 1:# op_box contains the button
            label_text = tla.setLabelRed(self.label_operation.text() + u' ' + u'\u26a0')
            self.label_operation.setText(label_text)
            self.label_operation.setToolTip(u"Deve ser definida pelo menos uma Operação.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_operation.text()))
        else:
            label_text = tla.unsetLabelRed(self.label_operation.text().replace(u'\u26a0', '')).strip()
            self.label_operation.setText(label_text)
            self.label_operation.setToolTip(u"")
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_operation.text()))

    def check_operations_completness(self):
        for x in self.operationList:
            if not x.isComplete():
                self.superParent.register_incomplete_entries(self.objectName(), u"Operações")
                return
        self.superParent.unregister_incomplete_entries(self.objectName(), u"Operações")

    def set_data(self, md):
        if md.serviceidentification is None:
            return
        for op in md.serviceidentification.operations:
            con = []
            for c in op['connectpoint']:
                con.append(c.url)
            to_add = InlineServiceOperation(self)
            to_add.set_data(op['name'], op['dcplist'], con)
            self.op_box.insertWidget(0, to_add)
            self.op_box.setAlignment(Qt.AlignTop)
            self.operationList.append(to_add)
            self.check_mandatory_operations()
            self.check_operations_completness()

    def get_data(self, md):
        ret = []
        for op in self.operationList:
            ret.append(op.get_data())
        md.serviceidentification.operations = ret
        return md
