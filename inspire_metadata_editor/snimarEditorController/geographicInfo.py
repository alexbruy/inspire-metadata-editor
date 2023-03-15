# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/geographicInfo.py
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

from qgis.PyQt.QtCore import QModelIndex, Qt
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QWidget

from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.extent_dialog import ExtentDialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CodeListItem, \
    CustomComboBox, Reference_System_Item

# UI generated python modules

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import \
    geographicinformationPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.geo_localization_dialog import \
    GeoLocalizationDialog
from qgis.gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import setLabelRed, \
    unsetLabelRed
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import listRowsValidation as lval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo

NO_VALUE = -999999999.0000


class GeographicInfoWidget(QWidget, geographicinformationPanel.Ui_geographicinfo):
    def __init__(self, parent, scope):
        super(GeographicInfoWidget, self).__init__(parent)
        self.setupUi(self)
        self.superParent = self.parent()
        self.scope = scope

        headers = [u'Limite Oeste', u"Limite Este", u"Limite Norte", u"Limite Sul",
                   u"Contém\nRecurso"]

        column_types = [qwidgets.QDoubleSpinBox, qwidgets.QDoubleSpinBox, qwidgets.QDoubleSpinBox,
                        qwidgets.QDoubleSpinBox, qwidgets.QCheckBox]
        tla.setupTableView(self, self.boundingbox, headers, column_types, GeoLocalizationDialog)
        self.boundingbox.horizontalHeader().setCascadingSectionResizes(True)
        self.boundingbox.horizontalHeader().setStretchLastSection(False)
        self.boundingbox.horizontalHeader().resizeSection(4, 60)
        self.boundingbox.horizontalHeader().setSectionResizeMode(4, qwidgets.QHeaderView.Fixed)
        self.boundingbox.horizontalHeader().setSectionResizeMode(3, qwidgets.QHeaderView.Stretch)
        self.boundingbox.horizontalHeader().setSectionResizeMode(2, qwidgets.QHeaderView.Stretch)
        self.boundingbox.horizontalHeader().setSectionResizeMode(1, qwidgets.QHeaderView.Stretch)
        self.boundingbox.horizontalHeader().setSectionResizeMode(0, qwidgets.QHeaderView.Stretch)

        headers = [u"Identificador", u"Contém\nRecurso"]
        column_types = [QgsFilterLineEdit, qwidgets.QCheckBox]
        sources = [self.line_identifier, self.check_haveResource]
        tla.setupTableView(self, self.geographicidentifier, headers, column_types, sources,
                           mandatorysources=[0])
        self.geographicidentifier.horizontalHeader().setCascadingSectionResizes(True)
        self.geographicidentifier.horizontalHeader().setStretchLastSection(False)
        self.geographicidentifier.horizontalHeader().resizeSection(1, 60)
        self.geographicidentifier.horizontalHeader().setSectionResizeMode(0, qwidgets.QHeaderView.Stretch)

        # Setup the reference system stuff
        self.combo_items = {}
        for element in self.superParent.reference_systems_list["horizontal_refs"]:
            self.combo_items[str(element['code']).strip()] = Reference_System_Item(
                code=element['code'], name=element['name'],
                codeSpace=element['codespace'])

        self.listValidation = lval.GeographicInfo(list(self.combo_items.values()))
        tla.setupListView(self.referencesystem, CustomComboBox, self,
                          comboList=list(self.combo_items.values()),
                          validationfunction=self.listValidation.referenceSystems)

        self.boundingbox.doubleClicked.connect(self.handleDoubleClick)

        self.combo_items_vert = {}
        for element in self.superParent.reference_systems_list["vertical_refs"]:
            self.combo_items_vert[str(element['code']).strip()] = Reference_System_Item(
                code=element['code'], name=element['name'],
                codeSpace='EPSG')
        self.referencesystemidentifier.setModel(
            customCombo.CustomComboBoxModel(self, [None] + sorted(list(self.combo_items_vert.values()),
                                                                  key=lambda x: x.name)))

        for btn in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
        for info in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        self.extent_btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/globe.svg'))
        self.extent_btn.setText('')
        self.minimumValue.valueChanged.connect(self.check_consistency_altimetric_extention)
        self.maximumValue.valueChanged.connect(self.check_consistency_altimetric_extention)
        self.referencesystemidentifier.currentIndexChanged.connect(
            self.check_consistency_altimetric_extention)
        self.minimumValue.setSpecialValueText(" ")
        self.maximumValue.setSpecialValueText(" ")
        self.clear_min_max()

        tla.setupMandatoryField(self, self.referencesystem, self.label_referencesystem,
                                u"Obrigatório conter pelo menos uma "
                                u"entrada")
        tla.setupMandatoryField(self, self.boundingbox, self.label_boundingbox,
                                u"A Especificação de uma caixa envolvente é obrigatoria.")
        # Button to open extent dialog
        self.extent_btn.clicked.connect(self.launch_extent_dialog)

        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        self.check_consistency_altimetric_extention()

        self.dialog = None
        self.check_haveResource.setChecked(True)
        self.btn_clear_all.pressed.connect(self.clear_min_max)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.helps['geographicinformationPanel'][
                                                self.sender().objectName()]), None)

    def check_consistency_altimetric_extention(self):
        if self.maximumValue.value() == NO_VALUE and self.minimumValue.value() == NO_VALUE and \
                (
                                self.referencesystemidentifier.currentText() is None or
                                self.referencesystemidentifier.currentText().strip() == ""):
            self.unsetWarn()
        elif self.maximumValue.value() - self.minimumValue.value() > 0 and \
                        self.maximumValue.value() != NO_VALUE and \
                        self.minimumValue.value() != NO_VALUE and \
                (self.referencesystemidentifier.currentText().strip() != ""):
            self.unsetWarn()
        else:
            if self.maximumValue.value() == NO_VALUE or \
                            self.minimumValue.value() == NO_VALUE or \
                            self.referencesystemidentifier.currentText().strip() == "":
                self.setWarn(u"Todos campos da Extensão Altimétrica têm que estar preenchidos.")
            else:
                self.setWarn(u"O valor maximo deve ser maior que o valor minimo.")

    def setWarn(self, text):
        if not unsetLabelRed(self.label_vertical_extent.text()).strip().endswith(u'\u26a0'):
            label_text = setLabelRed(self.label_vertical_extent.text() + u' ' + u'\u26a0')
            self.label_vertical_extent.setText(label_text)
        self.label_vertical_extent.setToolTip(tla.formatTooltip(text))
        self.superParent.register_incomplete_entries(self.objectName(), unsetLabelRed(
            self.label_vertical_extent.text()))

    def unsetWarn(self):
        label_text = unsetLabelRed(self.label_vertical_extent.text().replace(u'\u26a0', '')).strip()
        self.label_vertical_extent.setText(label_text)
        self.label_vertical_extent.setToolTip(u'')
        self.superParent.unregister_incomplete_entries(self.objectName(), unsetLabelRed(
            self.label_vertical_extent.text()))

    @qcore.pyqtSlot(QModelIndex)
    def handleDoubleClick(self, index):
        if self.sender() == self.boundingbox:
            tla.callDialogAndEdit(self.sender(), GeoLocalizationDialog, index)

    def set_data(self, md=None):
        if md is not None:
            if self.scope != SCOPES.SERVICES:
                common = md.identification
            else:
                common = md.serviceidentification
            if common is None:
                return
            for extent in common.extent:
                if hasattr(extent, 'boundingBox') and extent.boundingBox is not None:
                    bbox = extent.boundingBox
                    if extent.hasresource == 'true':
                        hasresource = True
                    else:
                        hasresource = False
                    boundingbox_row = [bbox.minx.replace('.', ','), bbox.maxx.replace('.', ','),
                                       bbox.maxy.replace('.', ','),
                                       bbox.miny.replace('.', ','), hasresource]
                    self.boundingbox.model().addNewRow(boundingbox_row)
                elif hasattr(extent, 'description_code') and extent.description_code is not None:
                    if extent.hasresource == 'true':
                        hasresource = True
                    else:
                        hasresource = False
                    self.geographicidentifier.model().addNewRow(
                        [extent.description_code, hasresource])
                elif hasattr(extent, 'min'):
                    if isFloat(extent.min):
                        self.minimumValue.setValue(float(extent.min))
                    if isFloat(extent.max):
                        self.maximumValue.setValue(float(extent.max))
                    if isinstance(extent.crs, str):
                        buf = extent.crs.replace("urn:ogc:def:crs:EPSG:", "")
                        if self.combo_items_vert.get(buf) is not None:
                            self.referencesystemidentifier.setCurrentIndex(
                                self.referencesystemidentifier.findText(
                                    self.combo_items_vert.get(buf).term_pt))

            for reference_system in md.referencesystem:
                if reference_system.code == "":
                    continue
                code = reference_system.code.split('/')[
                    -1] if reference_system.code is not None else None
                if self.combo_items.get(code) is None:
                    self.referencesystem.model().addNewRow(
                        Reference_System_Item(code=code, codeSpace=reference_system.codeSpace,
                                              name=""))
                else:
                    self.referencesystem.model().addNewRow(self.combo_items[code])
        self.check_consistency_altimetric_extention()

    def get_data(self, md):

        if self.scope != SCOPES.SERVICES:
            common = md.identification
        else:
            common = md.serviceidentification
        for row in self.boundingbox.model().matrix:
            bbox = snimarProfileModel.EX_Extent()
            bbox.hasresource = str(row[4])
            bbox.boundingBox = snimarProfileModel.iso.EX_GeographicBoundingBox()
            bbox.boundingBox.minx = row[1].replace(',', '.')
            bbox.boundingBox.maxx = row[0].replace(',', '.')
            bbox.boundingBox.miny = row[3].replace(',', '.')
            bbox.boundingBox.maxy = row[2].replace(',', '.')
            common.extent.append(bbox)

        for row in self.geographicidentifier.model().matrix:
            geographic_identifier = snimarProfileModel.EX_Extent()
            geographic_identifier.description_code = str(row[0])
            geographic_identifier.hasresource = str(row[1])
            common.extent.append(geographic_identifier)

        for row in self.referencesystem.model().listElements:
            reference_system = snimarProfileModel.iso.MD_ReferenceSystem(None)
            reference_system.code = row.code
            reference_system.codeSpace = row.codeSpace
            md.referencesystem += [reference_system]

        vertical_ext = snimarProfileModel.EX_VerticalExtent()
        have_vert = False
        if self.referencesystemidentifier.currentText() != '':
            vertical_ext.crs = u"urn:ogc:def:crs:EPSG:" + self.referencesystemidentifier.itemData(
                self.referencesystemidentifier.currentIndex()).code
            have_vert = True

        if self.maximumValue.value() != NO_VALUE:
            vertical_ext.max = self.maximumValue.value()
            have_vert = True

        if self.minimumValue.value() != NO_VALUE:
            vertical_ext.min = self.minimumValue.value()
            have_vert = True

        if have_vert:
            common.extent.append(vertical_ext)


    @qcore.pyqtSlot()
    def launch_extent_dialog(self):
        self.dialog = ExtentDialog(self, self.boundingbox)
        self.dialog.show()

    def clear_min_max(self):
        self.minimumValue.setValue(NO_VALUE)
        self.maximumValue.setValue(NO_VALUE)
        self.referencesystemidentifier.setCurrentIndex(-1)
        self.check_consistency_altimetric_extention()


def isFloat(str):
    try:
        float(str)
        return True
    except Exception:
        return False
