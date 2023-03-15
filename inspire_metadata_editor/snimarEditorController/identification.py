# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/identification.py
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
from builtins import zip
from builtins import str
import uuid
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QWidget, QHeaderView, QPushButton, QComboBox, QDoubleSpinBox, QSpinBox
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis._gui import QgsFilterLineEdit

from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
from EditorMetadadosMarswInforbiomares.snimarEditorController import contactWidget
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import listRowsValidation as lval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import tablesRowsValidation as tval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import unsetLabelRed, \
    setLabelRed
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import \
    identificationPanel


class IdentificationWidget(QWidget, identificationPanel.Ui_identification):
    """

        :type superParent :   editorMetadadosSNIMar.EditorMetadadosMarswInforbiomares
        """

    def __init__(self, parent, scope):

        super(IdentificationWidget, self).__init__(parent)
        self.setupUi(self)
        self.superParent = self.parent()
        self.contacts_list = []
        self.scope = scope
        # CODELISTS LOAD
        self.combo_items_md_maintenancefrequencycode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_MaintenanceFrequencyCode"])
        self.combo_items_languagecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["LanguageCode"])
        self.combo_items_md_spatialrepresentationtypecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_SpatialRepresentationTypeCode"])
        self.combo_items_md_charactersetCode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_CharacterSetCode"])
        self.combo_items_md_scopecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_ScopeCode"])
        self.combo_items_md_progressCode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_ProgressCode"])
        self.combo_item_service_type = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["ServiceType"])
        self.combo_items_couplingType = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["CouplingType"])
        self.combo_items_distance_units = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["DistanceUnits"])

        # Lists
        self.validator = lval.Identification(list(self.combo_items_md_maintenancefrequencycode.values()),
                                             list(self.combo_items_languagecode.values()),
                                             list(self.combo_items_md_spatialrepresentationtypecode.values()),
                                             list(self.combo_items_md_progressCode.values()))
        self.tablevalidator = tval.Identification()
        tla.setupListView(self.credits, QgsFilterLineEdit, self)
        # ---------

        tla.setupListView(self.resourcemaintenance, customCombo.CustomComboBox, self,
                          comboList=list(self.combo_items_md_maintenancefrequencycode.values()),
                          validationfunction=self.validator.resourcemaintenance)
        # ---------

        tla.setupListView(self.language, customCombo.CustomComboBox, self,
                          comboList=list(self.combo_items_languagecode.values()),
                          validationfunction=self.validator.language)

        # ----------------------------
        tla.setupListView(self.resourcestatus, customCombo.CustomComboBox, self,
                          comboList=list(self.combo_items_md_progressCode.values()),
                          validationfunction=self.validator.resourcestatus)

        self.combo_language.setCurrentIndex(
            self.combo_language.findText(cons.PREDEF_LANG_RESOURCES))
        # ---------

        # tables
        tla.setupTableView(self, self.identifiers,
                           [u'Identificador', u'Espaço de Nomes'],
                           [QgsFilterLineEdit, QgsFilterLineEdit],
                           [self.line_identifier, self.line_namespace],
                           validationfunction=self.tablevalidator.identifiers,
                           mandatorysources=[0])
        self.identifiers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        tla.setupMandatoryField(self, self.hierarchylevel, self.label_hierarchylevel,
                                u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.title, self.label_title,
                                u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.abstract_, self.label_abstract,
                                u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.titleEN, self.label_titleEN,
                                u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.abstractEN, self.label_abstractEN,
                                u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.resourcemaintenance, self.label_resourcemaintenance,
                                u"Obrigatório conter pelo menos uma entrada")
        tla.setupMandatoryField(self, self.identifiers, self.label_identifiers,
                                u"Obrigatório conter pelo menos uma entrada")
        tla.setupMandatoryField(self, self.characterset, self.label_characterset,
                                u"Elemento obrigatório em falta")



        # ComboBoxes Initialization(Not the ones associated with List/Table Views!!!!)

        self.characterset.setModel(
            customCombo.CustomComboBoxModel(self, [None] + sorted(
                list(self.combo_items_md_charactersetCode.values()), key=lambda x: x.term_pt)))
        self.characterset.setCurrentIndex(self.characterset.findText(cons.PREDEF_CHARSET))
        self.hierarchylevel.setModel(
            customCombo.CustomComboBoxModel(self,
                                            [None] + sorted(list(self.combo_items_md_scopecode.values()),
                                                            key=lambda x: x.term_pt)))
        # ----------------------------------------------------------------------#
        self.btn_adi_contact.clicked.connect(self.addContact)
        self.check_mandatory_contacts()
        # Buttons Icons initialization

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
        self.btn_adi_contact.setIcon(QIcon(':/resourcesFolder/icons/plus_icon.svg'))
        self.btn_gen_uuid_identifiers.clicked.connect(
            lambda: self.identifiers.model().addNewRow([str(uuid.uuid4()), None]))

        self.eater = tla.EatWheel()
        for x in self.findChildren(QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

        self.hierarchylevel.setCurrentIndex(
            self.hierarchylevel.findText(self.combo_items_md_scopecode[
                                             SCOPES.get_string_representation(self.scope)].term_pt))
        self.hierarchylevel.setDisabled(True)

        if scope == SCOPES.CDG or scope == SCOPES.SERIES:

            tla.setupTableView(self, self.distance, ["Valor", "Unidade"],
                               [QDoubleSpinBox, customCombo.CustomComboBox],
                               [self.spin_distance, self.combo_distance],
                               comboList=[self.combo_items_distance_units],
                               mandatorysources=[0, 1])
            self.distance.verticalHeader().setMinimumSectionSize(20)
            self.distance.verticalHeader().setDefaultSectionSize(100)
            self.distance.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.combo_distance.setModel(
                customCombo.CustomComboBoxModel(self,
                                                sorted(list(self.combo_items_distance_units.values()),
                                                       key=lambda x: x.term_pt)))
            self.combo_distance.setCurrentIndex(self.combo_distance.findText('Metros'))

            tla.setupListView(self.equivalentscale, QSpinBox, self, fraction_flag=True,
                              validationfunction=self.validator.equivalentscale)
            tla.setupListView(self.geographicrepresentation, customCombo.CustomComboBox, self,
                              comboList=list(self.combo_items_md_spatialrepresentationtypecode.values()),
                              validationfunction=self.validator.geographicrepresentation)

            self.equivalentscale.model().rowsInserted.connect(self.check_mandatory_resolution)
            self.equivalentscale.model().rowsRemoved.connect(self.check_mandatory_resolution)
            self.distance.model().rowsInserted.connect(self.check_mandatory_resolution)
            self.distance.model().rowsRemoved.connect(self.check_mandatory_resolution)
            self.widget_service.setHidden(True)
            self.serviceType.setHidden(True)
            self.widget_coupling.setHidden(True)
            self.couplingType.setHidden(True)
            self.widget_operatesOn.setHidden(True)
            self.operatesOn.setHidden(True)
            self.btn_add_operatesOn.setHidden(True)
            self.btn_del_operatesOn.setHidden(True)
            self.line_operatesOn.setHidden(True)
            self.check_mandatory_resolution()
            tla.setupMandatoryField(self, self.geographicrepresentation,
                                    self.label_geographicrepresentation,
                                    u"Obrigatório conter pelo menos uma entrada")
            tla.setupMandatoryField(self, self.language, self.label_language,
                                    u"Obrigatório conter pelo menos uma entrada")

            self.spatiaResolutionUnknown.stateChanged.connect(self.check_mandatory_resolution)
        elif scope == SCOPES.SERVICES:
            tla.setupListView(self.operatesOn, QgsFilterLineEdit, self)
            self.serviceType.setModel(
                customCombo.CustomComboBoxModel(self, [None] + sorted(
                    list(self.combo_item_service_type.values()), key=lambda x: x.term_pt)))
            self.couplingType.setModel(
                customCombo.CustomComboBoxModel(self, [None] + sorted(
                    list(self.combo_items_couplingType.values()), key=lambda x: x.term_pt)))
            # spatialRespresentationType AND language
            self.box_language_geoReprType.setHidden(True)
            # spatialRepresentation
            self.box_spatial_resolution.setHidden(True)
            # charset
            self.widget_charset.setHidden(True)
            self.characterset.setHidden(True)
            tla.setupMandatoryField(self, self.couplingType, self.label_couplingType,
                                    u"Campo Obrigatório.")
            tla.setupMandatoryField(self, self.serviceType, self.label_serviceType,
                                    u"Campo Obrigatório.")

    def set_data(self, md):

        if md is not None:

            self.hierarchylevel.setCurrentIndex(
                self.hierarchylevel.findText(self.combo_items_md_scopecode[md.hierarchy].term_pt))
            self.hierarchylevel.setDisabled(True)

            if self.scope == SCOPES.SERVICES:
                if md.serviceidentification is None:
                    return
                if self.combo_item_service_type.get(md.serviceidentification.type) is not None:
                    self.serviceType.setCurrentIndex(
                        self.serviceType.findText(
                            self.combo_item_service_type[md.serviceidentification.type].term_pt))
                if self.combo_items_couplingType.get(
                        md.serviceidentification.couplingtype) is not None:
                    self.couplingType.setCurrentIndex(
                        self.couplingType.findText(self.combo_items_couplingType[
                                                       md.serviceidentification.couplingtype].term_pt))

                for opOn in md.serviceidentification.operateson:
                    if opOn.get('href'):
                        self.operatesOn.model().addNewRow(opOn['href'])

                common = md.serviceidentification
            else:
                if md.identification is None:
                    return
                for lang in md.identification.language:
                    if self.combo_items_languagecode.get(lang) is None:
                        self.language.model().addNewRow(customCombo.CodeListItem(lang, lang, lang))
                    else:
                        self.language.model().addNewRow(self.combo_items_languagecode[lang])

                if self.combo_items_md_charactersetCode.get(md.identification.charset) is None:
                    self.characterset.setCurrentIndex(
                        self.characterset.findText(cons.PREDEF_CHARSET))
                else:
                    self.characterset.setCurrentIndex(
                        self.characterset.findText(self.combo_items_md_charactersetCode.get(
                            md.identification.charset).term_pt))
                for geo in md.identification.spatialrepresentation:
                    if self.combo_items_md_spatialrepresentationtypecode.get(geo) is None:
                        self.geographicrepresentation.model().addNewRow(
                            customCombo.CodeListItem(geo, geo, geo))
                    else:
                        self.geographicrepresentation.model().addNewRow(
                            self.combo_items_md_spatialrepresentationtypecode[geo])
                not_unk = True
                if len(md.identification.denominators) > 0:
                    for val in md.identification.denominators:
                        if int(val) == -1:
                            self.spatiaResolutionUnknown.setChecked(True)
                            self.equivalentscale.model().deleteAll()
                            not_unk = False
                            break
                        else:
                            try:
                                self.equivalentscale.model().addNewRow(int(val))
                            except ValueError:
                                pass  # discard value

                if len(md.identification.distance) > 0 and not_unk:
                    for val, uom in zip(md.identification.distance, md.identification.uom):
                        uom=unit_decoder(uom)
                        try:
                            ums = self.combo_items_distance_units.get(uom,
                                                                      self.combo_items_distance_units.get(
                                                                          'm'))
                            self.distance.model().addNewRow((float(val.replace(',', '.')), ums))
                        except ValueError:
                            pass  # discard value
                self.check_mandatory_resolution()

                common = md.identification

                ############################################33

            for cred in common.credits:
                if cred is not None and cred.strip() != "":
                    self.credits.model().addNewRow(cred)

            for res in common.resourcemaintenance:
                if self.combo_items_md_maintenancefrequencycode.get(res) is not None:
                    self.resourcemaintenance.model().addNewRow(
                        self.combo_items_md_maintenancefrequencycode[res])
                else:
                    self.resourcemaintenance.model().addNewRow(
                        customCombo.CodeListItem(res, res, res))

            self.graphicoverview.setText(common.graphicoverview)
            self.title.setText(common.title)
            self.titleEN.setText(common.titleEN)
            self.abstract_.setPlainText(common.abstract)
            self.abstractEN.setPlainText(common.abstractEN)
            self.alternatetitle.setText(common.alternatetitle)

            for status in common.status:
                if self.combo_items_md_progressCode.get(status) is not None:
                    self.resourcestatus.model().addNewRow(self.combo_items_md_progressCode[status])
                else:
                    self.resourcestatus.model().addNewRow(
                        customCombo.CodeListItem(status, status, status))

            self.purpose.setPlainText(common.purpose)

            for index, item in enumerate(common.uricode):
                self.identifiers.model().addNewRow([item, common.uricodespace[index]])

            # Set contacts
            contact_index = 0
            for contact in common.contact:
                self.addContact()
                contact_object = self.contacts_list[contact_index]
                contact_object.set_data(contact)
                contact_index += 1
            self.check_mandatory_contacts()

    def get_data(self, md):
        md.hierarchy = self.hierarchylevel.itemData(self.hierarchylevel.currentIndex())
        md.scope = SCOPES.get_string_representation(self.scope)
        if self.scope == SCOPES.SERVICES:
            md.serviceidentification.type = self.serviceType.itemData(
                self.serviceType.currentIndex())
            md.serviceidentification.couplingtype = self.couplingType.itemData(
                self.couplingType.currentIndex())
            md.serviceidentification.operateson = self.operatesOn.model().get_all_items()
            common = md.serviceidentification
        else:
            md.identification.charset = self.characterset.itemData(self.characterset.currentIndex())
            md.identification.spatialrepresentation = self.geographicrepresentation.model(
            ).get_all_items()
            md.identification.language = self.language.model().get_all_items()
            if not self.spatiaResolutionUnknown.isChecked():

                for val in self.distance.model().matrix:
                    if val[0] != 0.:
                        md.identification.distance.append([val[0], val[1].term])
                for val in self.equivalentscale.model().get_all_items():
                    if val != 0:
                        md.identification.denominators.append(val)
            else:
                md.identification.denominators.append(
                    -1)  # -1 is the default value if spatial resolution is unknown
            common = md.identification

        common.title = self.title.text()
        common.titleEN = self.titleEN.text()
        common.abstract = self.abstract_.toPlainText()
        common.abstractEN = self.abstractEN.toPlainText()
        common.alternatetitle = self.alternatetitle.text()
        common.purpose = self.purpose.toPlainText()
        common.status = self.resourcestatus.model().get_all_items()

        common.credits = self.credits.model().listElements
        common.resourcemaintenance = self.resourcemaintenance.model().get_all_items()

        for row in self.identifiers.model().matrix:
            common.uricode.append(row[0])
            if row[1] is not None and isinstance(row[1], str) and row[1].strip() != "":
                common.uricodespace.append(row[1].strip())
            else:
                common.uricodespace.append(None)

        common.graphicoverview = self.graphicoverview.text()
        for contact in self.contacts_list:
            temp = contact.get_data()
            if temp.role == "pointOfContact":
                common.contact.insert(0, temp)
            else:
                common.contact.append(temp)
        return md

    def addContact(self):
        contact = contactWidget.InlineContactWidget(self, self.superParent.orgs)
        self.Contacts.insertWidget(-1, contact)
        self.Contacts.setAlignment(Qt.AlignTop)
        self.contacts_list.append(contact)
        self.check_mandatory_contacts()
        self.check_contacts_completness()

    def deleteContact(self, contact):
        self.Contacts.removeWidget(contact)
        self.contacts_list.remove(contact)
        contact.close()
        self.check_mandatory_contacts()
        self.check_contacts_completness()

    def check_mandatory_contacts(self):
        if self.Contacts.count() == 0:
            label_text = tla.setLabelRed(
                self.label_contacts.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"É necessario pelo menos um contacto.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_contacts.text()))
        else:
            label_text = tla.unsetLabelRed(
                self.label_contacts.text().replace(u'\u26a0', '')).strip()
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"")
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_contacts.text()))

    def check_contacts_completness(self):
        self.check_role()
        for x in self.contacts_list:
            if not x.isComplete():
                self.superParent.register_incomplete_entries(self.objectName(), "Contactos")
                return
        self.superParent.unregister_incomplete_entries(self.objectName(), "Contactos")

    def check_role(self):
        have_poc = False
        for cont in self.contacts_list:
            if cont.get_role() == 'pointOfContact':
                have_poc = True
                break
        if not have_poc:
            label_text = tla.setLabelRed(
                self.label_contacts.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(
                u"É necessario pelo menos um contacto com a função 'Contacto'.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_contacts.text()))
        else:
            label_text = tla.unsetLabelRed(
                self.label_contacts.text().replace(u'\u26a0', '')).strip()
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"")
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_contacts.text()))

    def check_mandatory_resolution(self):
        if self.spatiaResolutionUnknown.isChecked():
            self.box_spatial_res_tables.setDisabled(True)
        else:
            self.box_spatial_res_tables.setDisabled(False)

        if self.spatiaResolutionUnknown.isChecked() and self.label_spatialResolution.toolTip() != \
                u"":
            label_text = unsetLabelRed(
                self.label_spatialResolution.text().replace(u'\u26a0', '')).strip()
            self.label_spatialResolution.setText(label_text)
            self.label_spatialResolution.setToolTip(u'')
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_spatialResolution.text()))
            return

        if self.distance.model().rowCount() <= 0 and self.equivalentscale.model().rowCount() <= 0 and \
                        self.label_spatialResolution.toolTip() == u"":
            label_text = setLabelRed(
                self.label_spatialResolution.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_spatialResolution.setText(label_text)
            self.label_spatialResolution.setToolTip(
                tla.formatTooltip(u"Pelo menos um dos seguintes listas tem que conter um valor."))
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_spatialResolution.text()))

        elif (self.distance.model().rowCount() > 0 or self.equivalentscale.model().rowCount() > 0) \
                and self.label_spatialResolution.toolTip() != u"":
            label_text = unsetLabelRed(
                self.label_spatialResolution.text().replace(u'\u26a0', '')).strip()
            self.label_spatialResolution.setText(label_text)
            self.label_spatialResolution.setToolTip(u'')
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(
                self.label_spatialResolution.text()))

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(
            self.superParent.helps['identificationPanel'][self.sender().objectName()]), None)


def unit_decoder(unit):
    radian = ['rad', 'radian']
    degree = ['deg', 'degree']

    unit = unit.split('#')[-1]

    if unit.lower() in radian:
        return 'rad'
    elif unit.lower() in degree:
        return 'deg'
    else:  # even if the unit isn't recognized ,should be defaulted to the most common used unit, metre
        return 'm'
