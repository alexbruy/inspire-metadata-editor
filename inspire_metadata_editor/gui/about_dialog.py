# -*- coding: utf-8 -*-

"""
***************************************************************************
    about_dialog.py
    ---------------------
    Date                 : March 2023
    Copyright            : (C) 2023 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'March 2023'
__copyright__ = '(C) 2023, Alexander Bruy'


import os
import configparser

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QTextDocument, QPixmap, QDesktopServices
from qgis.PyQt.QtCore import QUrl

from inspire_metadata_editor.constants import PLUGIN_ROOT


WIDGET, BASE = uic.loadUiType(os.path.join(PLUGIN_ROOT, "ui", "about_dialog.ui"))


class AboutDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(PLUGIN_ROOT, 'metadata.txt'))
        name = cfg['general']['name']
        about = cfg['general']['about']
        version = cfg['general']['version']
        icon = cfg['general']['icon']
        author = cfg['general']['author']
        self.home_page = cfg['general']['homepage']
        bug_tracker = cfg['general']['tracker']

        self.setWindowTitle(self.tr('About {}'.format(name)))
        self.lblName.setText('<h1>{}</h1>'.format(name))

        self.lblLogo.setPixmap(QPixmap(os.path.join(PLUGIN_ROOT, *icon.split('/'))))
        self.lblVersion.setText(self.tr(f'Version: {version}'))

        doc = QTextDocument()
        doc.setHtml(self.aboutText(about, author, self.home_page, bug_tracker))
        self.textBrowser.setDocument(doc)
        self.textBrowser.setOpenExternalLinks(True)

        self.buttonBox.helpRequested.connect(self.openHelp)

    def openHelp(self):
        QDesktopServices.openUrl(QUrl(self.home_page))

    def aboutText(self, about, author, home_page, bug_tracker):
        return self.tr(
            f'<p>{about}</p>'
            f'<p><strong>Developers</strong>: {author}</p>'
            f'<p><strong>Homepage</strong>: <a href="{home_page}">{home_page}</a></p>'
            f'<p>Please report bugs at <a href="{bug_tracker}">bugtracker</a>.</p>')
