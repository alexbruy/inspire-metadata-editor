# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/temporalInfo.py
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
from builtins import str
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets

# UI generated python module
from qgis.PyQt.QtCore import QDate, Qt
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QDateEdit, QWidget
from qgis.PyQt.QtGui import QCursor
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import temporalInformationPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import unsetLabelRed
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.null_QDateEdit import NullQDateEditWrapper, NullQDateTimeEditWrapper
from EditorMetadadosMarswInforbiomares.snimarProfileModel.snimarProfileModel import EX_TemporalExtent


class TemporalInfoWidget(QWidget, temporalInformationPanel.Ui_temporal):
    def __init__(self, parent, scope):
        super(TemporalInfoWidget, self).__init__(parent)

        self.setupUi(self)
        self.creationdate = NullQDateEditWrapper(self.creationdate)
        self.revisiondate = NullQDateEditWrapper(self.revisiondate)
        self.superParent = self.parent()
        self.scope = scope
        self.combo_items_ci_datetypecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["CI_DateTypeCode"])
        tla.setupListView(self.publicationdate, QDateEdit, self, date_format=cons.DATE_FORMAT)

        # timeextension stuff (headers and types and such
        self.creationdate.clear()
        self.revisiondate.clear()
        self.date_publicationdate.clear()

        self.begindate = NullQDateTimeEditWrapper(self.begindate)
        self.enddate = NullQDateTimeEditWrapper(self.enddate)
        self.begindate.clear()
        self.enddate.clear()

        self.date_publicationdate.setDate(QDate.currentDate())
        self.publicationdate.model().rowsInserted.connect(self.reftemocheck)
        self.publicationdate.model().rowsRemoved.connect(self.reftemocheck)
        self.creationdate.get_original().editingFinished.connect(self.reftemocheck)
        self.revisiondate.get_original().editingFinished.connect(self.reftemocheck)
        self.creationdate.get_original().dateTimeChanged.connect(self.reftemocheck)
        self.revisiondate.get_original().dateTimeChanged.connect(self.reftemocheck)

        self.begindate.get_original().editingFinished.connect(self.time_ext_check)
        self.enddate.get_original().editingFinished.connect(self.time_ext_check)
        self.begindate.get_original().dateTimeChanged.connect(self.time_ext_check)
        self.enddate.get_original().dateTimeChanged.connect(self.time_ext_check)
        self.reftemocheck()
        self.time_ext_check()

        for btn in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
            elif '_clear_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_field.svg'))
        for info in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)
        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

        self.btn_clear_creationdate.pressed.connect(lambda: self.creationdate.clear())
        self.btn_clear_revisiondate.pressed.connect(lambda: self.revisiondate.clear())
        self.btn_clear_begindate.pressed.connect(lambda: self.begindate.clear())
        self.btn_clear_enddate.pressed.connect(lambda: self.enddate.clear())

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['temporalInformationPanel'][self.sender().objectName()]),
                          None)

    def set_data(self, md=None):
        if md is None:
            return None
        if self.scope != SCOPES.SERVICES:
            common = md.identification
        else:
            common = md.serviceidentification
        if common is None:
            return
        for date in common.date:
            if date.type == 'creation':
                self.creationdate.setDateTime(qcore.QDateTime.fromString(date.date, cons.DATE_FORMAT))
            elif date.type == 'revision':
                self.revisiondate.setDateTime(qcore.QDateTime.fromString(date.date, cons.DATE_FORMAT))
            elif date.type == 'publication':
                self.publicationdate.model().addNewRow(QDate.fromString(date.date, cons.DATE_FORMAT))

        for extent in common.extent:
            if hasattr(extent, 'beginposition') and extent.beginposition is not None:
                self.begindate.set_dateTime(
                    qcore.QDateTime.fromString(extent.beginposition.replace("T", " "), cons.DATE_TIME_FORMAT))
                self.enddate.set_dateTime(qcore.QDateTime.fromString(extent.endposition.replace("T", " "), cons.DATE_TIME_FORMAT))

    def get_data(self, md=None):
        if self.scope != SCOPES.SERVICES:
            common = md.identification
        else:
            common = md.serviceidentification
        if self.creationdate.get_date() is not None:
            creation_date = snimarProfileModel.iso.CI_Date()
            creation_date.date = self.creationdate.get_date().toString(cons.DATE_FORMAT)
            creation_date.type = self.combo_items_ci_datetypecode['creation']
            common.date.append(creation_date)
        if self.revisiondate.get_date() is not None:
            revision_date = snimarProfileModel.iso.CI_Date()
            revision_date.date = self.revisiondate.get_date().toString(cons.DATE_FORMAT)
            revision_date.type = self.combo_items_ci_datetypecode['revision']
            common.date.append(revision_date)

        for pub in self.publicationdate.model().listElements:
            pub_date = snimarProfileModel.iso.CI_Date()
            pub_date.date = pub.toString(cons.DATE_FORMAT)
            pub_date.type = self.combo_items_ci_datetypecode['publication']
            common.date.append(pub_date)

        bdate = self.begindate.get_dateTime()
        edate = self.enddate.get_dateTime()

        if bdate is None or edate is None:
            return

        bdate = self.begindate.get_dateTime().toString(cons.DATE_TIME_FORMAT).replace(" ", "T")
        edate = self.enddate.get_dateTime().toString(cons.DATE_TIME_FORMAT).replace(" ", "T")
        ids = "B" + bdate.replace(":", "").replace("-", "") + "E" + edate.replace(":", "").replace("-", "")
        common.extent.append(EX_TemporalExtent(id=ids, beginposition=bdate, endposition=edate))

    def reftemocheck(self):
        if self.creationdate.get_date() is None and self.revisiondate.get_date() is None and \
                        self.publicationdate.model().rowCount() == 0 and self.label_temporalREf.toolTip() == "":

            label_text = tla.setLabelRed(self.label_temporalREf.text() + u' ' + u'\u26a0')
            self.label_temporalREf.setText(label_text)
            self.label_temporalREf.setToolTip(u"Pelo menos um dos elementos tem que ser preenchido.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_temporalREf.text()))
        elif not (
                            self.creationdate.get_date() is None and self.revisiondate.get_date() is None and self.publicationdate.model().rowCount() == 0) and self.label_temporalREf.toolTip() != "":
            label_text = tla.unsetLabelRed(self.label_temporalREf.text().replace(u'\u26a0', '')).strip()
            self.label_temporalREf.setText(label_text)
            self.label_temporalREf.setToolTip(u'')
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_temporalREf.text()))

    def time_ext_check(self):
        self.set_diference()
        # clean state
        label_text = tla.unsetLabelRed(self.label_timeextension.text().replace(u'\u26a0', '')).strip()
        self.label_timeextension.setText(label_text)
        self.label_timeextension.setToolTip(u'')
        self.superParent.unregister_incomplete_entries(self.objectName(), unsetLabelRed(self.label_timeextension.text()))

        if self.enddate.is_null_date() and self.begindate.is_null_date():
            pass
        elif self.begindate.is_null_date():
            label_text = tla.setLabelRed(self.label_timeextension.text() + u' ' + u'\u26a0')
            self.label_timeextension.setText(label_text)
            self.label_timeextension.setToolTip(u"A data de início da extensão temporal não se encontra preenchida.")
            self.superParent.register_incomplete_entries(self.objectName(), unsetLabelRed(self.label_timeextension.text()))
        elif self.enddate.is_null_date():
            label_text = tla.setLabelRed(self.label_timeextension.text() + u' ' + u'\u26a0')
            self.label_timeextension.setText(label_text)
            self.label_timeextension.setToolTip(u"A data de fim da extensão temporal não se encontra preenchida.")
            self.superParent.register_incomplete_entries(self.objectName(), unsetLabelRed(self.label_timeextension.text()))
        elif self.begindate.get_dateTime() > self.enddate.get_dateTime():
            label_text = tla.setLabelRed(self.label_timeextension .text() + u' ' + u'\u26a0')
            self.label_timeextension.setText(label_text)
            self.label_timeextension.setToolTip(u"A duração da Extensão Temporal não se encontra correcta.")
            self.superParent.register_incomplete_entries(self.objectName(),  unsetLabelRed(self.label_timeextension.text()))

    def set_diference(self):
        if self.enddate.is_null_date() or self.begindate.is_null_date():
            self.label_duration.setText("-")
            return True
        else:
            delta = self.enddate.get_dateTime().toPyDateTime() - self.begindate.get_dateTime().toPyDateTime()
            hours = delta.seconds / 3600
            minutes = (delta.seconds % 3600) / 60
            segundos = ((delta.seconds % 3600) % 60)
            text = str(delta.days) + " Dias," + str(hours) + " Horas," + str(minutes) + " Minutos," + str(
                segundos) + " Segundos"
            if delta.days < 0 or delta.seconds < 0:
                self.label_duration.setText(tla.setLabelRed(text))
                return False
            else:
                self.label_duration.setText(text)
                return True
