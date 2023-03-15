# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditorMetadadosMarswInforbiomares/snimarQtInterfaceView/templates/dialogs//chooseGeographicExtentFromLayer.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(400, 129)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.mMapLayerComboBox = gui.QgsMapLayerComboBox(Dialog)
        self.mMapLayerComboBox.setObjectName("mMapLayerComboBox")
        self.gridLayout.addWidget(self.mMapLayerComboBox, 1, 0, 1, 1)
        self.selectionCheckBox = QtWidgets.QCheckBox(Dialog)
        self.selectionCheckBox.setObjectName("selectionCheckBox")
        self.gridLayout.addWidget(self.selectionCheckBox, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Obter extensão da camada"))
        self.selectionCheckBox.setText(_translate("Dialog", "Usar apenas elementos seleccionados"))
        self.label.setText(_translate("Dialog", "Selecione camada"))
from qgis import gui
