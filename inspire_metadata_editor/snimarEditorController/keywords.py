# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/keywords.py
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

# Qt and Qgis imports
from builtins import range
import copy
import datetime
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
import uuid
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAbstractItemView, QToolTip, QDateTimeEdit, QWidget, QLineEdit, QHeaderView, QDateEdit, QPushButton, QComboBox, QMessageBox
from qgis.PyQt.QtGui import QIcon, QCursor, QStandardItem, QStandardItemModel
from qgis._gui import QgsFilterLineEdit

# Snimar Constants
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES

# Snimar Qt ui generated files
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import keywordsPanel

# Dialogs
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.freekeywords_dialog import FreeKeyWordsDialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.snimarKeywordsDialog import SNIMARKeywordsDialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.wormsKeywordsDialog import WormsKeywordsDialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.crossrefKeywordsDialog import CrossrefKeywordsDialog

# Snimar Controller and Model imports
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import tablesRowsValidation as tval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import listRowsValidation as lval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import TableModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import unsetLabelRed, setLabelRed


class KeywordsWidget(QWidget, keywordsPanel.Ui_keywords):
    def __init__(self, parent, scope):
        super(KeywordsWidget, self).__init__(parent)
        self.setupUi(self)

        self.superParent = self.parent()

        self.combo_items_inspire = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["INSPIRE"])
        self.combo_items_serviceClassification = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["ServiceClassification"])
        self.combo_items_topiccategory = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_TopicCategoryCode"])
        self.combo_items_datetype = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["CI_DateTypeCode"])
        self.combo_items_md_keywordtypecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_KeywordTypeCode"])
        self.combo_items_md_keywordtypecode_snimar = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_KeywordTypeCodeSNIMar"])
        self.validatorList = lval.Keywords(list(self.combo_items_inspire.values()), list(self.combo_items_topiccategory.values()))
        self.validatorTables = tval.Keywords(list(self.combo_items_md_keywordtypecode.values()),
                                             list(self.combo_items_datetype.values()))

        sn_model = TableModel(self, [u"Tipo", u"Palavra-Chave", u"Versão Thesaurus"],
                              [customCombo.CustomComboBox, QLineEdit, QLineEdit],
                              self.snimarkeywords,
                              validationfunction=self.validatorTables.snimarkeywords)
        self.snimarkeywords.setModel(sn_model)
        self.snimarkeywords.resizeColumnsToContents()

        self.snimarkeywords.verticalHeader().setVisible(False)
        self.snimarkeywords.resizeRowsToContents()
        self.snimarkeywords.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.snimarkeywords.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.snimarkeywords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.btn_open_snimarkeywords.clicked.connect(self.snimar_dialog)
        self.btn_del_snimarkeywords.clicked.connect(lambda: tla.removeSelectedFromList(self.snimarkeywords))

        self.wormskeywords.setColumnHidden(1, True)
        worms_model = TableModel(self, ['Palavra-chave', 'date'], [QLineEdit, QLineEdit], self.wormskeywords)
        self.wormskeywords.setModel(worms_model)
        self.wormskeywords.setColumnHidden(1, True)
        self.wormskeywords.resizeColumnsToContents()
        self.wormskeywords.verticalHeader().setVisible(False)
        self.wormskeywords.resizeRowsToContents()
        self.wormskeywords.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.wormskeywords.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.wormskeywords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.btn_open_wormskeywords.clicked.connect(self.worms_dialog)
        self.btn_del_wormskeyword.clicked.connect(lambda: tla.removeSelectedFromList(self.wormskeywords))

        #crossref_model = TableModel(self, ['Autor', 'Titulo'], [QLineEdit, QLineEdit], self.crossrefkeywords)
        self.crossrefkeywords.setColumnHidden(1, True)
        self.crossrefkeywords.setColumnHidden(2, True)
        crossref_model = TableModel(self, ['Palavra-chave', 'doi', 'date'], [QLineEdit, QLineEdit, QLineEdit], self.crossrefkeywords)
        self.crossrefkeywords.setModel(crossref_model)
        self.crossrefkeywords.setColumnHidden(1, True)
        self.crossrefkeywords.setColumnHidden(2, True)
        self.crossrefkeywords.resizeColumnsToContents()
        self.crossrefkeywords.verticalHeader().setVisible(False)
        self.crossrefkeywords.resizeRowsToContents()
        self.crossrefkeywords.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.crossrefkeywords.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.crossrefkeywords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.btn_open_crossrefkeywords.clicked.connect(self.crossref_dialog)
        self.btn_del_crossrefkeyword.clicked.connect(lambda: tla.removeSelectedFromList(self.crossrefkeywords))

        tla.setupTableView(self, self.freekeywords,
                           [u"Palavra-Chave", u"Tipo", u"Thesaurus", u"Data", u"Tipo de Data"],
                           [QgsFilterLineEdit, customCombo.CustomComboBox, QgsFilterLineEdit, QDateEdit,
                            customCombo.CustomComboBox],
                           FreeKeyWordsDialog,
                           comboList=[self.combo_items_md_keywordtypecode, self.combo_items_datetype],
                           validationfunction=self.validatorTables.freekeywords)
        self.freekeywords.doubleClicked.connect(self.handleDoubleClick)
        self.freekeywords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for btn in self.findChildren(QPushButton, qcore.QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
        for info in self.findChildren(QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)
        self.btn_update_snimar.clicked.connect(self.launchupdatesnimar)
        self.snimarkeywords.model().rowsInserted.connect(self.snimar_keywords_special_validation)
        self.snimarkeywords.model().rowsRemoved.connect(self.snimar_keywords_special_validation)
        self.eater = tla.EatWheel()
        for x in self.findChildren(QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        self.dialog = SNIMARKeywordsDialog(self, self.snimarkeywords.model(),
                                           self.combo_items_md_keywordtypecode_snimar)
        self.dialog.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))


        self.wormsDialog = WormsKeywordsDialog(self)
        self.wormsDialog.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))

        self.crossrefDialog = CrossrefKeywordsDialog(self)
        self.crossrefDialog.setWindowIcon(QIcon(":/resourcesFolder/icons/main_icon.png"))


        self.validatorTables.set_thesaurus(self.dialog.thesaurus_model)

        self.snimar_keywords_special_validation()
        self.scope = scope
        if self.scope == SCOPES.SERVICES:
            self.widget_topic.setHidden(True)
            self.topiccategory.setHidden(True)
            self.combo_topiccategory.setHidden(True)
            self.btn_add_topiccategory.setHidden(True)
            self.btn_del_topiccategory.setHidden(True)
            self.widget_inspire.setHidden(True)
            self.inspire.setHidden(True)
            self.btn_add_inspire.setHidden(True)
            self.btn_del_inspire.setHidden(True)
            self.combo_inspire.setHidden(True)
            tla.setupListView(self.serviceClassification, customCombo.CustomComboBox, self,
                              comboList=list(self.combo_items_serviceClassification.values()))
            tla.setupMandatoryField(self, self.serviceClassification, self.label_serviceClassification,
                                    u"Obrigatório conter pelo menos uma entrada")

        else:
            self.widget_serviceClassification.setHidden(True)
            self.serviceClassification.setHidden(True)
            self.btn_add_serviceClassification.setHidden(True)
            self.btn_del_serviceClassification.setHidden(True)
            self.combo_serviceClassification.setHidden(True)
            tla.setupListView(self.topiccategory, customCombo.CustomComboBox, self,
                              comboList=list(self.combo_items_topiccategory.values()),
                              validationfunction=self.validatorList.topiccategory)
            tla.setupMandatoryField(self, self.topiccategory, self.label_topiccategory,
                                    u"Obrigatório conter pelo menos uma "
                                    u"entrada")
            tla.setupListView(self.inspire, customCombo.CustomComboBox, self,
                              comboList=list(self.combo_items_inspire.values()),
                              validationfunction=self.validatorList.inspire)

            tla.setupMandatoryField(self, self.inspire, self.label_inspire,
                                    u"Obrigatório conter pelo menos uma entrada")

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.helps['keywordsPanel'][self.sender().objectName()]), None)

    def snimar_keywords_special_validation(self):
        positives = 0

        for sn_type in cons.SNIMAR_KEYWORDS_MANDATORY_TYPES:
            if self.snimarkeywords.model().contains_at_column(self.combo_items_md_keywordtypecode_snimar.get(sn_type),
                                                              0):
                positives += 1
            else:
                break
        if positives == len(cons.SNIMAR_KEYWORDS_MANDATORY_TYPES) and self.label_snimarkeywords.toolTip() != u'':
            label_text = unsetLabelRed(self.label_snimarkeywords.text().replace(u'\u26a0', '')).strip()
            self.label_snimarkeywords.setText(label_text)
            self.label_snimarkeywords.setToolTip(u'')
            self.superParent.unregister_mandatory_missingfield(self.objectName(),
                                                               unsetLabelRed(self.label_snimarkeywords.text()))
        elif positives != len(cons.SNIMAR_KEYWORDS_MANDATORY_TYPES) and self.label_snimarkeywords.toolTip() == u'':
            label_text = setLabelRed(self.label_snimarkeywords.text() + u' ' + u'\u26a0')
            self.label_snimarkeywords.setText(label_text)
            self.label_snimarkeywords.setToolTip(
                tla.formatTooltip(
                    u"O Metadado tem que conter pelo menos uma palavra chave SNIMar dos seguintes tipos: " +
                    ', '.join(cons.SNIMAR_KEYWORDS_MANDATORY_TYPES) + u'.'))
            self.superParent.register_mandatory_missingfield(self.objectName(),
                                                             unsetLabelRed(self.label_snimarkeywords.text()))

    def snimar_dialog(self):
        try:
            self.dialog.exec_()
        except RuntimeError:
            try:
                self.dialog.exec_()
            except RuntimeError:
                pass

    def worms_dialog(self):
        try:
            self.wormsDialog.exec_()
        except RuntimeError:
            try:
                self.wormsDialog.exec_()
            except RuntimeError:
                pass

    def crossref_dialog(self):
        try:
            self.crossrefDialog.exec_()
        except RuntimeError:
            try:
                self.crossrefDialog.exec_()
            except RuntimeError:
                pass

    def set_data(self, md):
        if md is None:
            return False
        if self.scope != SCOPES.SERVICES:
            if md.identification is None:
                return
            for topic in md.identification.topiccategory:
                if self.combo_items_topiccategory.get(topic) is not None:
                    self.topiccategory.model().addNewRow(self.combo_items_topiccategory[topic])
                elif customCombo.reverse_en_to_pt_keys(self.combo_items_topiccategory).get(topic) is not None:
                    self.topiccategory.model().addNewRow(
                        customCombo.reverse_en_to_pt_keys(self.combo_items_topiccategory)[topic])
                else:
                    self.topiccategory.model().addNewRow(customCombo.CodeListItem(topic, topic, topic))
            common = md.identification
        else:
            common = md.serviceidentification

        if common is None:
            return
        for keyword in common.keywords:
            for word in keyword.keywords:
                if keyword.is_inspire() and self.scope != SCOPES.SERVICES:
                    if self.combo_items_inspire.get(word, None) is not None:
                        self.inspire.model().addNewRow(self.combo_items_inspire[word])
                    elif customCombo.reverse_en_to_pt_keys(self.combo_items_inspire).get(word, None) is not None:
                        self.inspire.model().addNewRow(
                            customCombo.reverse_en_to_pt_keys(self.combo_items_inspire)[word])
                    else:
                        self.inspire.model().addNewRow(customCombo.CodeListItem(word, word, word))
                elif keyword.is_serviceClassification() and self.scope == SCOPES.SERVICES:
                    if self.combo_items_serviceClassification.get(word, None) is not None:
                        self.serviceClassification.model().addNewRow(self.combo_items_serviceClassification[word])
                    elif customCombo.reverse_en_to_pt_keys(self.combo_items_serviceClassification).get(word,
                                                                                                       None) is not \
                            None:
                        self.serviceClassification.model().addNewRow(
                            customCombo.reverse_en_to_pt_keys(self.combo_items_serviceClassification)[word])
                    else:
                        self.serviceClassification.model().addNewRow(customCombo.CodeListItem(word, word, word))
                elif keyword.is_snimar():
                    if customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode_snimar).get(
                            keyword.type) is None:
                        type_ = customCombo.CodeListItem(keyword.type, keyword.type, keyword.type)
                    else:
                        type_ = customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode_snimar).get(
                            keyword.type)
                    thesaurus = {
                        'title': keyword.thesaurus["title"],
                        'version': u"v" + keyword.thesaurus["title"].split('v')[1],
                        'date': keyword.thesaurus['date'],
                        'datetype': customCombo.CodeListItem(u"publication", u"Publicação")
                    }

                    self.snimarkeywords.model().addNewRow(
                        [type_, word, thesaurus['version'], thesaurus, keyword.cc_uuid])
                    self.snimar_keywords_special_validation()

                elif keyword.is_worms():
                    self.wormskeywords.model().addNewRow(
                        [word, keyword.thesaurus['date']]
                    )

                elif keyword.is_crossref():
                    self.crossrefkeywords.model().addNewRow(
                        [word, keyword.thesaurus['title'].split('doi:')[-1], keyword.thesaurus['date']]
                    )

                else:
                    if customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode).get(keyword.type) is None:
                        if keyword.type is None:
                            type_ = None
                        else:
                            type_ = customCombo.CodeListItem(keyword.type, keyword.type, keyword.type)
                    else:
                        type_ = customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode).get(keyword.type)
                    row = [word] + [type_]
                    if keyword.thesaurus is not None:
                        row.append(keyword.thesaurus['title'])
                        date = qcore.QDate.fromString(keyword.thesaurus['date'], cons.DATE_FORMAT)
                        row.append(date)
                        if self.combo_items_datetype.get(keyword.thesaurus['datetype']) is None:
                            kw_type = None
                        else:
                            kw_type = self.combo_items_datetype[keyword.thesaurus['datetype']]
                        row.append(kw_type)
                    else:
                        row += [None] * 3
                    self.freekeywords.model().addNewRow(row)

    def get_data(self, md):
        if self.scope != SCOPES.SERVICES:
            md.identification.topiccategory = self.topiccategory.model().get_all_items()
            # Write the INSPIRE keywords
            inspire_keywords = snimarProfileModel.MD_Keywords()
            inspire_keywords.keywords = [x.term_pt for x in self.inspire.model().get_all_items()]
            inspire_keywords.type = self.combo_items_md_keywordtypecode['Tema']
            inspire_keywords.thesaurus = {
                'title': 'GEMET - INSPIRE themes, version 1.0',
                'date': '2008-06-01',
                'datetype': self.combo_items_datetype['publication'],
            }
            md.identification.keywords.append(inspire_keywords)
            common = md.identification
        else:
            common = md.serviceidentification
            service_keywords = snimarProfileModel.MD_Keywords()
            service_keywords.keywords = [x.term for x in self.serviceClassification.model().get_all_items()]
            service_keywords.type = self.combo_items_md_keywordtypecode['Tema']
            service_keywords.thesaurus = {
                'title': 'ISO - 19119 geographic services taxonomy',
                'date': '2010-01-19',
                'datetype': self.combo_items_datetype['publication'],
            }
            md.serviceidentification.keywords.append(service_keywords)

        for row in self.freekeywords.model().matrix:
            keyword = snimarProfileModel.MD_Keywords()
            keyword.keywords.append(row[0])
            keyword.type = row[1]

            if row[2] is not None and len(row[2]) > 0:
                if row[4] is None:
                    datety = None
                else:
                    datety = self.combo_items_datetype[row[4].term]
                keyword.thesaurus = {
                    'title': row[2],
                    'date': row[3].toString(cons.DATE_FORMAT),
                    'datetype': datety
                }
            common.keywords.append(keyword)

        for row in self.snimarkeywords.model().matrix:
            keyword = snimarProfileModel.MD_Keywords()
            keyword.keywords.append(row[1])
            keyword.type = row[0]
            keyword.cc_uid = row[4]
            keyword.thesaurus = row[3]
            keyword.kwdtype_codeList = 'http://collab-keywords.snimar.pt/codelists/gmxCodelists.xml' \
                                       '#MD_KeywordTypeCode_snimar'
            common.keywords.append(keyword)

        for row in self.wormskeywords.model().matrix:
            keyword = snimarProfileModel.MD_Keywords()
            keyword.keywords.append(row[0])
            keyword.thesaurus = {
                'title': 'https://www.marinespecies.org/rest/',
                'date': row[1],
                'datetype': self.combo_items_datetype['revision'],
            }
            common.keywords.append(keyword)

        for row in self.crossrefkeywords.model().matrix:
            keyword = snimarProfileModel.MD_Keywords()
            keyword.keywords.append(row[0])
            keyword.thesaurus = {
                'title': 'https://api.crossref.org/works?filter=doi:{}'.format(row[1]),
                'date': row[2],
                'datetype': self.combo_items_datetype['revision'],
            }
            common.keywords.append(keyword)

    @qcore.pyqtSlot(qcore.QModelIndex)
    def handleDoubleClick(self, index):
        if self.sender() == self.freekeywords:
            tla.callDialogAndEdit(self.sender(), FreeKeyWordsDialog, index,
                                  combos=[self.combo_items_md_keywordtypecode, self.combo_items_datetype])

    def revalidate_snimar_keywords(self):
        """Revalidate that goddamn snimar keywords table."""
        self.validatorTables.set_thesaurus(self.dialog.thesaurus_model)
        matrix_copy = copy.deepcopy(self.snimarkeywords.model().matrix)

        for index in range(self.snimarkeywords.model().rowCount()):
            self.snimarkeywords.model().removeSpecificRow(0)

        for row in matrix_copy:
            self.snimarkeywords.model().addNewRow(row)

    def launchupdatesnimar(self):
        title = "Atulizar Palavra-chave SNIMar"
        i = 0

        for line in self.snimarkeywords.model().matrix:
            val = self.validatorTables.snimarkeywords(line)
            i += 1
            if val[2] is None:
                continue
            if val[3] == 'word':
                texto = u'Palavra Não atualizada:'  u'\n' + line[1] + u'\n' + \
                        u'Palavra Atualizada:'  u'\n' + val[2] + u'\n' + u'\n' + \
                        u'Deseja Atualizar?'

                dialog = QMessageBox(QMessageBox.Question, title, texto,
                                          (QMessageBox.Ok | QMessageBox.Cancel))

                dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
                result = dialog.exec_()
                if result == QMessageBox.Ok:
                    index = self.snimarkeywords.model().index(i - 1, 1)
                    lineI = line[:]
                    lineI[1] = val[2]
                    self.snimarkeywords.model().setDataRow(index, lineI)
                    val = self.validatorTables.snimarkeywords(lineI)
            if val[2] is not None and val[3] == 'type':
                new_type = customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode_snimar)[val[2]]
                texto = u'Tipo Não Atualizado:'  u'\n' + line[0].term_pt + u'\n' + \
                        u'Tipo Atualizado:'  u'\n' + new_type.term_pt + u'\n' + u'\n' + \
                        u'Deseja Atualizar?'
                dialog = QMessageBox(QMessageBox.Question, title, texto,
                                          (QMessageBox.Ok | QMessageBox.Cancel))

                dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
                result = dialog.exec_()
                if result == QMessageBox.Ok:
                    index = self.snimarkeywords.model().index(i - 1, 1)
                    lineI = line[:]
                    lineI[0] = customCombo.reverse_pt_to_en_keys(self.combo_items_md_keywordtypecode_snimar)[val[2]]
                    self.snimarkeywords.model().setDataRow(index, lineI)

