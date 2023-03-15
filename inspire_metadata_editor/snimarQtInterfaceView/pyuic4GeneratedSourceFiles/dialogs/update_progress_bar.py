# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditorMetadadosMarswInforbiomares/snimarQtInterfaceView/templates/dialogs//update_progress_bar.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_update_dialog(object):
    def setupUi(self, update_dialog):
        update_dialog.setObjectName("update_dialog")
        update_dialog.resize(360, 70)
        update_dialog.setMinimumSize(QtCore.QSize(360, 70))
        update_dialog.setMaximumSize(QtCore.QSize(360, 70))
        update_dialog.setAutoFillBackground(False)
        update_dialog.setModal(True)
        self.formLayout = QtWidgets.QFormLayout(update_dialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(update_dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.update_progressbar = QtWidgets.QProgressBar(update_dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.update_progressbar.setFont(font)
        self.update_progressbar.setProperty("value", 90)
        self.update_progressbar.setInvertedAppearance(False)
        self.update_progressbar.setObjectName("update_progressbar")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.update_progressbar)

        self.retranslateUi(update_dialog)
        QtCore.QMetaObject.connectSlotsByName(update_dialog)

    def retranslateUi(self, update_dialog):
        _translate = QtCore.QCoreApplication.translate
        update_dialog.setWindowTitle(_translate("update_dialog", "Thesaurus SNIMar"))
        self.label.setText(_translate("update_dialog", "A atualizar a lista de palavras do thesaurus SNIMar"))
