# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/quality.py
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
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
from qgis.PyQt.QtCore import Qt, QDate, QDateTime
from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QDateEdit, QWidget
from qgis.PyQt.QtGui import QCursor
from qgis._gui import QgsFilterLineEdit
import re

from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel

# UI generated python modules

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import qualityPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import tablesRowsValidation as tval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.null_QDateEdit import NullQDateEditWrapper
from EditorMetadadosMarswInforbiomares import CONSTANTS as CONS

regex_pt = re.compile('^ *dados? *hist.ricos? *(?:marinhos?)? *(?:recuperados?)? *\.? *\n?',
                      re.IGNORECASE)
regex_en = re.compile('^ *historical? *(?:marine)? *registers? *(?:recovered) *\.? *\n?',
                      re.IGNORECASE)
expr_pt = u'Dado histórico marinho recuperado.\n'
expr_en = u'Historical marine register recovered.\n'


class QualityWidget(QWidget, qualityPanel.Ui_quality):
    def __init__(self, parent, scope):
        super(QualityWidget, self).__init__(parent)
        self.setupUi(self)
        self.conformancedate = NullQDateEditWrapper(self.conformancedate)
        self.superParent = self.parent()
        self.scope = scope
        self.combo_items_ci_datetypecode = customCombo.dic_to_CustomComboBox_dic(
                self.superParent.codelist["CI_DateTypeCode"])
        self.conformancedatetype.setModel(
                customCombo.CustomComboBoxModel(self, [None] + sorted(
                        list(self.combo_items_ci_datetypecode.values()),
                        key=lambda x: x.term_pt)))
        if scope == CONS.Scopes.CDG or scope == CONS.Scopes.SERIES:

            tla.setupTableView(self, self.processsteps,
                               [u"Descrição", u"Data", u"Justificação"],
                               [QgsFilterLineEdit, QDateTimeEdit, QgsFilterLineEdit],
                               [self.line_description, self.date_processdate, self.line_rationale],
                               mandatorysources=[0], validationfunction=tval.Quality().processsteps,
                               date_format=cons.DATE_TIME_FORMAT)
            self.processsteps.horizontalHeader().setCascadingSectionResizes(False)
            self.processsteps.horizontalHeader().setStretchLastSection(False)
            self.processsteps.horizontalHeader().resizeSection(1, 260)
            self.processsteps.horizontalHeader().setDefaultSectionSize(260)
            self.processsteps.horizontalHeader().setMinimumSectionSize(260)
            self.processsteps.horizontalHeader().setSectionResizeMode(1, qwidgets.QHeaderView.Fixed)
            self.processsteps.horizontalHeader().setSectionResizeMode(2, qwidgets.QHeaderView.Stretch)
            self.processsteps.horizontalHeader().setSectionResizeMode(0, qwidgets.QHeaderView.Stretch)
            self.date_processdate.setDate(QDate.currentDate())

            tla.setupListView(self.source, QgsFilterLineEdit, self)
            tla.setupMandatoryField(self, self.statement, self.label_statement,
                                    u"Elemento obrigatório.")
        else:
            self.panel_hist.hide()

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

        tla.setupMandatoryField(self, self.conformancetitle, self.label_conformancetitle,
                                u"Elemento obrigatório.")
        tla.setupMandatoryField(self, self.conformancedate, self.label_conformancedate,
                                u"Elemento obrigatório.")
        tla.setupMandatoryField(self, self.conformancedatetype, self.label_conformancedatetype,
                                u"Elemento obrigatório.")
        tla.setupMandatoryField(self, self.conformanceexplanation,
                                self.label_conformanceexplanation,
                                u"Elemento obrigatório.")

        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        self.btn_clear_conformancedate.pressed.connect(lambda: self.conformancedate.clear())

        self.btn_INSPIRE.pressed.connect(self.set_default_dataquality_report)
        self.statement.textChanged.connect(self.checkHistText)
        self.hist_data.stateChanged.connect(self.setHist)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.helps['qualityPanel'][
                                                self.sender().objectName()]), None)

    def get_data(self, md):

        dq = snimarProfileModel.DQ_DataQuality()
        if self.conformancedate.get_date() is not None:
            dq.conformancedate.append(self.conformancedate.get_date().toString('yyyy-MM-dd'))

        dq.conformancedatetype.append(
                self.conformancedatetype.itemData(self.conformancedatetype.currentIndex()))
        dq.conformancetitle.append(self.conformancetitle.text())
        dq.conformanceexplanation = self.conformanceexplanation.text()
        dq.conformancedegree.append(self.conformancedegree.isChecked())

        if self.scope == CONS.Scopes.CDG or self.scope == CONS.Scopes.SERIES:
            dq.lineage = self.statement.toPlainText()
            dq.lineageEN = self.statementEN.toPlainText()
            dq.sources = self.source.model().listElements
            temp = []
            for row in self.processsteps.model().matrix:
                temp.append([row[0], row[1].replace(" ", "T"), row[2]])
            dq.process_steps = temp

        md.dataquality = dq
        return md

    def set_data(self, md=None):
        if md is not None and md.dataquality is not None:
            report = snimarProfileModel.get_domainconsistency_report(md)
            self.conformancetitle.setText(report['specification'])
            if report['date'] is not None:
                self.conformancedate.setDate(
                        qcore.QDate.fromString(report['date'], cons.DATE_FORMAT))
            if report['datetype'] is not None and report['datetype'].strip() != "":
                self.conformancedatetype.setCurrentIndex(
                        self.conformancedatetype.findText(
                                self.combo_items_ci_datetypecode[report['datetype']].term_pt))
            self.conformanceexplanation.setText(report['explanation'])
            self.conformancedegree.setChecked(True if report['pass'] == 'true' else False)

            if self.scope == CONS.Scopes.CDG or self.scope == CONS.Scopes.SERIES:
                self.statement.setPlainText(md.dataquality.lineage)
                self.statementEN.setPlainText(md.dataquality.lineageEN)

                for source in md.dataquality.sources:
                    self.source.model().addNewRow(source)

                # Process Steps (aka etapas do processo)
                for row in md.dataquality.process_steps:
                    if type(row[1]) == str:
                        if re.match('^\d\d\d\d-\d\d-\d\d$', row[1]):
                            dt = row[1].strip() + "T00:00:00"
                        else:
                            dt = row[1]
                        dt = QDateTime.fromString(dt.replace("T", " "),
                                                  cons.DATE_TIME_FORMAT).toString(
                                cons.DATE_TIME_FORMAT)
                    else:
                        dt = ""
                    self.processsteps.model().addNewRow([row[0], dt, row[2]])
                self.date_processdate.setDate(QDate.currentDate())

    def set_default_dataquality_report(self):
        """
        Sets the report title, date and datetype to the required values specified
        by the INSPIRE Metadata profile.
        """
        if self.scope == CONS.Scopes.SERVICES:
            self.conformancetitle.setText(CONS.INSPIRE_TEXT_SERVICE)
            self.conformancedate.set_date(
                    qcore.QDate.fromString(CONS.INSPIRE_DATE_SERVICE, cons.DATE_FORMAT))
        else:
            self.conformancetitle.setText(CONS.INSPIRE_TEXT_DATASET)
            self.conformancedate.set_date(
                    qcore.QDate.fromString(CONS.INSPIRE_DATE_DATASET, cons.DATE_FORMAT))
        self.conformancedatetype.setCurrentIndex(self.conformancedatetype.findText(u'Publicação'))
        self.conformanceexplanation.setText(u'Ver a especificação citada.')
        self.setWindowModified(True)

    def checkHistText(self):
        if regex_pt.search(self.statement.toPlainText()) is not None:
            self.hist_data.setChecked(True)
        else:
            self.hist_data.setChecked(False)

    def setHist(self):
        stat_pt = regex_pt.sub('', self.statement.toPlainText())
        stat_en = regex_en.sub('', self.statementEN.toPlainText())
        if self.hist_data.checkState():
            self.statement.setPlainText(expr_pt + stat_pt)
            self.statementEN.setPlainText(expr_en + stat_en)
        else:
            self.statement.setPlainText(stat_pt)
            self.statementEN.setPlainText(stat_en)
        self.statement.moveCursor(QTextCursor.End)
