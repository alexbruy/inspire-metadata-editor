# -*- coding: utf-8 -*-

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

import os
import time
import platform

from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtWidgets import QSplashScreen, QApplication, QAction, QMessageBox

from qgis.core import QgsApplication

from inspire_metadata_editor.gui.editor_window import EditorWindow
from inspire_metadata_editor.gui.about_dialog import AboutDialog
from inspire_metadata_editor.constants import PLUGIN_ROOT


class InspireMetadataEditorPlugin:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action_run = QAction(self.tr("INSPIRE Metadata Editor"), self.iface.mainWindow())
        self.action_run.setIcon(QIcon(os.path.join(PLUGIN_ROOT, "icons", "plugin.svg")))
        self.action_run.setObjectName('actionOpenInspireEditor')
        self.action_run.triggered.connect(self.run)

        self.action_about = QAction(self.tr('About…'), self.iface.mainWindow())
        self.action_about.setIcon(QgsApplication.getThemeIcon('/mActionHelpContents.svg'))
        self.action_about.setObjectName('actionAboutInspireEditor')
        self.action_about.triggered.connect(self.about)

        self.iface.addPluginToMenu(self.tr('INSPIRE Metadata Editor'), self.action_run)
        self.iface.addPluginToMenu(self.tr('INSPIRE Metadata Editor'), self.action_about)

        self.iface.addToolBarIcon(self.action_run)

    def unload(self):
        self.iface.removePluginMenu(self.tr('INSPIRE Metadata Editor'), self.action_run)
        self.iface.removePluginMenu(self.tr('INSPIRE Metadata Editor'), self.action_about)

        self.iface.removeToolBarIcon(self.action_run)

        try:
            os.remove(os.path.join(PLUGIN_ROOT, "userFiles", ".meLock"))
        except OSError:
            pass

    def run(self):
        if platform.system() == 'Linux':
            try:
                from lxml import etree
            except ImportError:
                message = QMessageBox()
                message.setModal(True)
                message.setWindowTitle(self.tr('Módulo LXML Não Instalado'))
                message.setWindowIcon(QIcon(os.path.join(PLUGIN_ROOT, "icons", "plugin.svg")))
                message.setIcon(QMessageBox.Critical)
                message.setInformativeText(self.tr("<a href=\"http://lxml.de/installation.html\">Como instalar</a>"))
                message.setText(self.tr("O plugin necessita do módulo Lxml instalado."))
                message.addButton(self.tr('Sair'), QMessageBox.RejectRole)
                message.exec_()
                return

        if os.path.exists(os.path.join(PLUGIN_ROOT, "userFiles", ".meLock")):
            message = QMessageBox()
            message.setModal(True)
            message.setWindowTitle(self.tr('O Editor já se encontra a correr?'))
            message.setWindowIcon(QIcon(PLUGIN_ROOT, "resourcesFolder", "icons", "main_icon.png"))
            message.setIcon(QMessageBox.Warning)
            message.setText(self.tr("Verifique,\npor favor, se já existe outra instância do Editor de Metadados aberta.\n"
                            "Só é permitida uma instância para evitar conflitos."))
            message.setInformativeText(self.tr("Deseja continuar?"))
            message.addButton(self.tr('Continuar'), QMessageBox.AcceptRole)
            message.addButton(self.tr('Sair'), QMessageBox.RejectRole)
            ret = message.exec_()
            if ret != QMessageBox.AcceptRole:
                return

        # Create and display the splash screen
        splash_pix = QPixmap(os.path.join(PLUGIN_ROOT, "icons", "splash.png"))
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.setWindowFlags(splash.windowFlags() | Qt.WindowStaysOnTopHint)
        splash.show()

        QApplication.processEvents()

        start = time.time()
        while time.time() < start + 2:
            QApplication.processEvents()
        splash.close()

        f = open(os.path.join(PLUGIN_ROOT, "userFiles", ".meLock"), "w")
        f.close()
        dialog = EditorWindow()
        dialog.setWindowIcon(QIcon(os.path.join(PLUGIN_ROOT, "icons", "plugin.svg")))
        dialog.show()

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)
