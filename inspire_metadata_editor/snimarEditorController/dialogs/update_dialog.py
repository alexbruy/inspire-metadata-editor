# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/update_dialog.py
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
import json
import datetime

from qgis.PyQt import QtGui as qgui
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import update_progress_bar
from EditorMetadadosMarswInforbiomares.snimarProfileModel import service
from EditorMetadadosMarswInforbiomares import CONSTANTS


class SNIMarThesaurusUpdateDialog(QDialog, update_progress_bar.Ui_update_dialog):
    def __init__(self, parent):
        super(SNIMarThesaurusUpdateDialog, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.update_progressbar.setMaximum(100)
        self.update_progressbar.setMinimum(0)
        self.update_progressbar.setValue(0)

        self.thesaurus = None

    def update_thesaurus(self):
        self.thesaurus = service.ThesaurusServiceManager(self.update_progressbar)
        self.thesaurus.retrieve_all()
        self.finish_update()
        pass

    def finish_update(self):
        self.update_progressbar.setValue(100)

        filename = ''.join(['snimarThesaurus', self.thesaurus.latest_stable_version, '.json'])
        with open(os.path.join(CONSTANTS.SNIMAR_THESAURUS_DIR, filename), 'w') as fp:
            json.dump(self.thesaurus.stable_data, fp)

        filename = ''.join(['snimarThesaurus', '.json'])
        with open(os.path.join(CONSTANTS.SNIMAR_THESAURUS_DIR, filename), 'w') as fp:
            json.dump(self.thesaurus.unstable_data, fp)

        filename = ''.join(['snimarThesaurus_meta', '.json'])
        with open(CONSTANTS.SNIMAR_THESAURUS_META, 'w') as fp:

            meta = {
                'last_download': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M'),
                'last_update': self.thesaurus.latest_unstable_version_date,
                'current_version': self.thesaurus.latest_stable_version,
            }
            json.dump(meta, fp)
