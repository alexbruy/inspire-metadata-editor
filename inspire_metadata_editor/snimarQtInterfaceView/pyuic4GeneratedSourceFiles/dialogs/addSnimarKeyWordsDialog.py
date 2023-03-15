# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditorMetadadosMarswInforbiomares/snimarQtInterfaceView/templates/dialogs//addSnimarKeyWordsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 550)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(800, 550))
        Dialog.setMaximumSize(QtCore.QSize(1040, 600))
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.list_view_thesaurus = QtWidgets.QColumnView(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_view_thesaurus.sizePolicy().hasHeightForWidth())
        self.list_view_thesaurus.setSizePolicy(sizePolicy)
        self.list_view_thesaurus.setMinimumSize(QtCore.QSize(780, 481))
        self.list_view_thesaurus.setMaximumSize(QtCore.QSize(1020, 481))
        self.list_view_thesaurus.setFocusPolicy(QtCore.Qt.NoFocus)
        self.list_view_thesaurus.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.list_view_thesaurus.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.list_view_thesaurus.setLineWidth(6)
        self.list_view_thesaurus.setMidLineWidth(6)
        self.list_view_thesaurus.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_view_thesaurus.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_view_thesaurus.setAutoScroll(True)
        self.list_view_thesaurus.setAutoScrollMargin(0)
        self.list_view_thesaurus.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_view_thesaurus.setAlternatingRowColors(True)
        self.list_view_thesaurus.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_view_thesaurus.setTextElideMode(QtCore.Qt.ElideNone)
        self.list_view_thesaurus.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_view_thesaurus.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_view_thesaurus.setResizeGripsVisible(False)
        self.list_view_thesaurus.setObjectName("list_view_thesaurus")
        self.gridLayout.addWidget(self.list_view_thesaurus, 0, 0, 1, 2)
        self.btn_exit = QtWidgets.QPushButton(Dialog)
        self.btn_exit.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_exit.setObjectName("btn_exit")
        self.gridLayout.addWidget(self.btn_exit, 1, 0, 1, 1)
        self.bt_add_selected = QtWidgets.QPushButton(Dialog)
        self.bt_add_selected.setMinimumSize(QtCore.QSize(0, 30))
        self.bt_add_selected.setAutoDefault(False)
        self.bt_add_selected.setObjectName("bt_add_selected")
        self.gridLayout.addWidget(self.bt_add_selected, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Escolher palavras chave SNIMar"))
        self.btn_exit.setText(_translate("Dialog", "Sair"))
        self.bt_add_selected.setText(_translate("Dialog", "Adicionar Selecionadas"))
