# -*- coding=utf-8 -*-
#############################################################################################################
#                     _______  _______   __  .___________.  ______   .______                                #
#                    |   ____||       \ |  | |           | /  __  \  |   _  \                               #
#                    |  |__   |  .--.  ||  | `---|  |----`|  |  |  | |  |_)  |                              #
#                    |   __|  |  |  |  ||  |     |  |     |  |  |  | |      /                               #
#                    |  |____ |  '--'  ||  |     |  |     |  `--'  | |  |\  \----.                          #
#                    |_______||_______/ |__|     |__|      \______/  | _| `._____|                          #
#                                                                                                           #
#  .___  ___.  _______ .___________.    ___       _______       ___       _______   ______        _______.  #
#  |   \/   | |   ____||           |   /   \     |       \     /   \     |       \ /  __  \      /       |  #
#  |  \  /  | |  |__   `---|  |----`  /  ^  \    |  .--.  |   /  ^  \    |  .--.  |  |  |  |    |   (----`  #
#  |  |\/|  | |   __|      |  |      /  /_\  \   |  |  |  |  /  /_\  \   |  |  |  |  |  |  |     \   \      #
#  |  |  |  | |  |____     |  |     /  _____  \  |  '--'  | /  _____  \  |  '--'  |  `--'  | .----)   |     #
#  |__|  |__| |_______|    |__|    /__/     \__\ |_______/ /__/     \__\ |_______/ \______/  |_______/      #
#                                                                                                           #
#                     _______..__   __.  __  .___  ___.      ___      .______                               #
#                    /       ||  \ |  | |  | |   \/   |     /   \     |   _  \                              #
#                   |   (----`|   \|  | |  | |  \  /  |    /  ^  \    |  |_)  |                             #
#                    \   \    |  . `  | |  | |  |\/|  |   /  /_\  \   |      /                              #
#                .----)   |   |  |\   | |  | |  |  |  |  /  _____  \  |  |\  \----.                         #
#                |_______/    |__| \__| |__| |__|  |__| /__/     \__\ | _| `._____|                         #
#                                                                                                           #
#                                                                                                           #
#############################################################################################################

##############################################################################
#
#  Title:   snimarMetadataEditorPluginEntryPoint.py
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
from __future__ import absolute_import
from builtins import object
import os.path
import platform
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QSplashScreen, QApplication, QAction, QMessageBox

from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt.QtCore import  Qt
import time

from . import editorMetadadosMarswInforbiomares

from . import resources


class EditorMetadadosPluginEntryPoint(object):
    """Main entrypoint for the QGIS EditorMetadadosMarswInforbiomares plugin."""

    def __init__(self, iface):
        self._name = 'Editor de Metadados Marsw Inforbiomares'
        self._iface = iface
        self.dialog = None


    def initGui(self):
        """Initialize the GUI machine"""
        self.action = QAction(QIcon(":/resourcesFolder/icons/main_icon.png"), self._name, self._iface.mainWindow())
        self.action.setObjectName('initialAction')
        self.action.setWhatsThis('Editor de Metadados Marsw Inforbiomares')
        self.action.setStatusTip('Editor de Metadados Marsw Inforbiomares')
        #qcore.QObject.connect(self.action, qcore.SIGNAL('triggered()'), self.run)
        self.action.triggered.connect(self.run)
        self._iface.addPluginToMenu('Editor de Metadados Marsw Inforbiomares', self.action)
        self._iface.addToolBarIcon(self.action)

    def unload(self):
        """Unload the plugin"""
        self._iface.removePluginMenu('Editor de Metadados Marsw Inforbiomares', self.action)
        self._iface.removeToolBarIcon(self.action)
        try:
            os.remove(os.path.join(os.path.dirname(__file__), "userFiles/.meLock"))
        except OSError:
            pass

    def run(self):
        """Plugin initial run"""

        if platform.system() == 'Linux':
            try:
                from lxml import etree
            except ImportError:
                message = QMessageBox()
                message.setModal(True)
                message.setWindowTitle(u'Módulo LXML Não Instalado')
                message.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))
                message.setIcon(QMessageBox.Critical)
                message.setInformativeText(u"<a href=\"http://lxml.de/installation.html\">Como instalar</a>")
                message.setText(u"O plugin necessita do módulo Lxml instalado.")
                message.addButton(u'Sair', QMessageBox.RejectRole)
                message.exec_()
                return

        if os.path.exists(os.path.join(os.path.dirname(__file__), "userFiles/.meLock")):
            message = QMessageBox()
            message.setModal(True)
            message.setWindowTitle(u'O Editor já se encontra a correr?')
            message.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))
            message.setIcon(QMessageBox.Warning)
            message.setText(u"Verifique,\npor favor, se já existe outra instância do Editor de Metadados aberta.\n"
                            u"Só é permitida uma instância para evitar conflitos.")
            message.setInformativeText(u"Deseja continuar?")
            message.addButton(u'Continuar', QMessageBox.AcceptRole)
            message.addButton(u'Sair', QMessageBox.RejectRole)
            ret = message.exec_()
            if ret != QMessageBox.AcceptRole:
                return

        # Create and display the splash screen
        splash_pix = QPixmap(":/resourcesFolder/splash.png")
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        #splash.showMessage("A Carregar...", alignment=Qt.AlignBottom | Qt.AlignHCenter, color=Qt.white)
        splash.setWindowFlags(splash.windowFlags() | Qt.WindowStaysOnTopHint)
        splash.show()

        QApplication.processEvents()

        start = time.time()
        while time.time() < start + 2:
            QApplication.processEvents()
        splash.close()

        f = open(os.path.join(os.path.dirname(__file__), "userFiles/.meLock"), "w")
        f.close()
        self.dialog = editorMetadadosMarswInforbiomares.EditorMetadadosMarswInforbiomares(self._iface, self)
        self.dialog.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))
        self.dialog.show()

