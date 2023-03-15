# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   editorMetadadosSNIMar.py
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
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import filter
from builtins import str
from builtins import range
import os
from qgis.utils import pluginDirectory
import sys
import json
import platform
import traceback
import urllib.request, urllib.error, urllib.parse

from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtWidgets import QPushButton, QHeaderView, QMenu, QAction, QProgressDialog, QProgressBar, QMessageBox, QAbstractItemView, QMainWindow, QWidget, QLineEdit, QTabBar
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QFont
import datetime

from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.about import About
from .snimarEditorController.metadadoSNIMar import MetadadoSNIMar, vality_msg
from .snimarEditorController import filemanager
from .snimarProfileModel import snimarProfileModel, validation
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tableaux
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs.update_dialog import SNIMarThesaurusUpdateDialog
from .snimarQtInterfaceView.pyuic4GeneratedSourceFiles import snimarEditorMainWindow
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
from EditorMetadadosMarswInforbiomares import CONSTANTS
from EditorMetadadosMarswInforbiomares.snimarProfileModel import service

from .snimarEditorController.dialogs import contacts_dialog
from .snimarEditorController.models.delegates import ButtonDelegate

# FLAGS
SAVE_FLAG = 0
SAVEAS_FLAG = 1


class EditorMetadadosMarswInforbiomares(QMainWindow, snimarEditorMainWindow.Ui_mainwindow):
    """SNIMar Editor main window class"""

    def __init__(self, iface, parent):
        super(EditorMetadadosMarswInforbiomares, self).__init__()

        # Setup the directory that will contain the filelist and the list of contacts
        self.setup_editor_dir()
        self.exitB = False
        self.iface = iface
        self.xml_files = []
        self.tmp_files = {}
        self.tab_files = []
        self.tmp_file_index = 0
        self.codelists = None
        self.load_codelists()
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)

        self.tracked_list = filemanager.FileManager(to_save=True, editordir=self.editor_dirname())
        self.tmp_list = filemanager.FileManager(to_save=False, editordir=self.editor_dirname())
        self.open_list = filemanager.FileManager(to_save=False, editordir=self.editor_dirname())
        self.last_open_dir = os.path.expanduser('~')

        self.setupUi(self)
        f = open(os.path.join(pluginDirectory('EditorMetadadosMarswInforbiomares'), 'resourcesFolder/stylesheet.qtcss'))
        self.sytlesheet = f.read()
        for btn in self.findChildren(QWidget):
            btn.setStyleSheet(self.sytlesheet)
            btn.setFocusPolicy(Qt.NoFocus)
        self.showMaximized()
        self.setWindowTitle(u'Editor de Metadados Marsw Inforbiomares')

        # Shortcuts
        shortcut_open = qgui.QKeySequence(qcore.Qt.CTRL + qcore.Qt.Key_O)
        shortcut_save = qgui.QKeySequence(qcore.Qt.CTRL + qcore.Qt.Key_S)



        # All the connects for the Dialog widget
        self.tabWidget.tabCloseRequested.connect(self.tab_close)
        self.new_dataset.triggered.connect(lambda: self.new_metadata_xml_tab(SCOPES.CDG))
        self.new_serie.triggered.connect(lambda: self.new_metadata_xml_tab(SCOPES.SERIES))
        self.new_service.triggered.connect(lambda: self.new_metadata_xml_tab(SCOPES.SERVICES))
        self.menu_open.triggered.connect(self.open_metadata_xml_file)
        self.menu_open.setShortcut(shortcut_open)
        self.menu_save.triggered.connect(lambda: self.save_metadata_xml_file(SAVE_FLAG))
        self.menu_save.setShortcut(shortcut_save)
        self.menu_saveas.triggered.connect(lambda: self.save_metadata_xml_file(SAVEAS_FLAG))
        self.menu_save_all.triggered.connect(self.save_all_open)
        self.menu_add_dir.triggered.connect(self.start_dir_track)
        self.menu_close.triggered.connect(self.close_editor)
        self.menu_codelists.triggered.connect(self.refresh_codelist)
        self.menu_resave.triggered.connect(self.resave_all_in_list)

        contact_list = self.menubar.addAction("Lista de Contactos")
        contact_list.triggered.connect(self.open_list_contacts)
        about = self.menubar.addAction("Sobre")
        about.triggered.connect(self.open_about)
        self.menubar.setNativeMenuBar(False)

        # Load the list of tracked files and load the filetable view
        self.tracked_list.load()
        filetable_data = []
        for key, value in list(self.tracked_list.items()):
            filetable_data.append([value['doc_type'], value['title'], value['path'], value['id'], None, None])
        type_mapping = [QLineEdit, QLineEdit, QLineEdit, QLineEdit, QLineEdit, QPushButton]
        self.filetable.setWordWrap(True)
        self.filetable.setTextElideMode(Qt.ElideNone)
        tableaux.setupTableView(self, self.filetable,
                                [u'Tipo', u'Título', u'Localização', u'Identificador Único Do Ficheiro',
                                 u'Conformidade*', u''],
                                type_mapping, None, model_data=filetable_data)
        self.filetable.horizontalHeader().setMinimumSectionSize(29)
        self.filetable.horizontalHeader().setCascadingSectionResizes(False)
        self.filetable.horizontalHeader().setStretchLastSection(False)
        self.filetable.horizontalHeader().resizeSection(5, 29)
        self.filetable.horizontalHeader().resizeSection(4, 200)
        self.filetable.horizontalHeader().resizeSection(3, 300)
        self.filetable.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.filetable.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.filetable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.filetable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.filetable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.filetable.verticalHeader().setMinimumSectionSize(60)
        self.filetable.verticalHeader().setDefaultSectionSize(60)
        self.filetable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.filetable.resizeRowsToContents()
        self.filetable.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.tabWidget.tabBar().setElideMode(Qt.ElideMiddle)
        self.filetable.setItemDelegateForColumn(5, ButtonDelegate(self.filetable, self))
        self.tabWidget.tabBar().tabButton(0, QTabBar.RightSide).resize(0, 0)

        self.filetable.doubleClicked.connect(lambda: self.open_metadata_xml_file(self.selected_file_row()))

        self.filetable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.filetable.customContextMenuRequested.connect(self.menu_context)
        self.filetable.model().sort(1, Qt.AscendingOrder)
        self.filetable.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)

        # CKW Thesaurus stuff
        # If the snimarThesaurus_meta file does not exist we force an update
        if not os.path.exists(CONSTANTS.SNIMAR_THESAURUS_META):
            self.launch_update()
        else:
            # If the file exists we check the last download date and if more than
            # 24 hours as passed we ask if it wants to update
            with open(CONSTANTS.SNIMAR_THESAURUS_META) as fp:
                meta = json.load(fp)
                last_download = datetime.datetime.strptime(meta['last_download'], '%Y-%m-%dT%H:%M')
                # See if the last_update or the version changed
                thesaurus = service.ThesaurusServiceManager(None)
                try:
                    thesaurus.set_version_params()
                except Exception as e:
                    QMessageBox().critical(self,
                                                u'Erro ao atualizar o Thesaurus SNIMar',
                                                u'Ocorreu um erro ao atualizar o Thesaurus SNIMar. Por favor '
                                                u'verifique o estado da sua ligação à rede.\nEntretanto, '
                                                u'poderá continuar ' + \
                                                u'a utilizar o editor com uma versão anterior do Thesaurus.' + \
                                                u'\nSe o problema persistir, por favor envie um email para '
                                                u'suporte.snimar@ipma.pt e inclua o seguinte texto:\n\n{}'.format(
                                                    e.message),
                                                u'OK')
                else:
                    if datetime.datetime.now() - last_download > datetime.timedelta(hours=24):
                        if thesaurus.latest_stable_version != meta[
                            'current_version'] or thesaurus.latest_unstable_version_date != meta[
                            'last_update']:
                            update_question_dialog = QMessageBox()
                            reply = update_question_dialog.question(self, u'Actualização do Thesaurus SNIMar',
                                                                    u'Existe uma nova versão do Thesaurus SNIMar. '
                                                                    u'Pretende actualizar agora?',
                                                                    QMessageBox.Yes | QMessageBox.No)
                            if reply == QMessageBox.Yes:
                                self.launch_update()

        self.thesaurus_update.clicked.connect(self.launch_update)
        #self.thesaurus_unstable_checkbox.stateChanged.connect(self.use_unstable)

        self.btn_delete_all.pressed.connect(self.erase_all)
        self.btn_conform_all.pressed.connect(self.check_conformity_all)


        # Table Actions
        self.visualize_action = QAction(u"Visualizar Metadado Externamente", self)
        self.visualize_action.triggered.connect(self.visualize_file)
        self.remove_action = QAction(u"Remover Metadado(s) da Lista", self)
        self.remove_action.triggered.connect(lambda: self.tab_close(None, remove=True))
        self.edit_action = QAction(u"Editar Metadado(s)", self)
        self.edit_action.triggered.connect(self.edit_meta)
        # table contextMenus
        self.menu_single = QMenu()
        self.menu_single.addAction(self.edit_action)
        self.menu_single.addAction(self.remove_action)
        self.menu_single.addAction(self.visualize_action)
        self.mouse_point = None  # dont use this not updated frequentaly only when menucontext is call

    # -------------------------------
    # EditorMetadadosMarswInforbiomares Slots
    # -------------------------------

    @qcore.pyqtSlot(QPoint)
    def menu_context(self, point):
        self.mouse_point = point
        self.menu_single.exec_(self.filetable.viewport().mapToGlobal(point))

    @qcore.pyqtSlot(int)
    def tab_close(self, index, remove=False):
        """Slot to handle the closing of a tab."""
        if not remove:
            curr_name = self.tabWidget.widget(index).objectName()
            if index > 0:
                self.tabWidget.removeTab(index)
                self.open_list.pop(curr_name)
        else:
            if len(self.filetable.selectionModel().selectedRows()) <= 0:
                return
            for x in sorted(self.filetable.selectionModel().selectedRows(), key=lambda row: row.row(), reverse=True):
                if self.filetable.model().matrix[x.row()][2] in self.open_list:
                    meta = self.findChild(MetadadoSNIMar, self.filetable.model().matrix[x.row()][2])
                    self.tabWidget.removeTab(self.tabWidget.indexOf(meta))
                self.tracked_list.pop(self.filetable.model().matrix[x.row()][2], None)
                self.filetable.model().removeSpecificRow(x.row())

    @qcore.pyqtSlot()
    def new_metadata_xml_tab(self, scope):
        """Slot to create a new tab without loading any XML file."""
        widget = MetadadoSNIMar(self, scope)
        new_tmp_name = u'Novo Ficheiro'
        if self.tmp_file_index > 0:
            new_tmp_name += '(' + str(self.tmp_file_index) + ')'

        widget.setObjectName(new_tmp_name)
        self.tabWidget.addTab(widget, new_tmp_name)
        self.tabWidget.setCurrentWidget(widget)
        filedict = {
            'path': new_tmp_name,
            'name': new_tmp_name,
            'title': None,
            'id': None,
            'doc_type': SCOPES.get_rich_text_translation(SCOPES.get_string_representation(scope))
        }
        print('new_metadata_xml_tab')
        self.open_list.track_new_file(**filedict)
        self.tab_files.append(filedict)
        self.tmp_file_index += 1

    @qcore.pyqtSlot()
    def open_metadata_xml_file(self, name=None):
        """Slot to create a new tab using the data retrieved from a XML file."""
        # Get the filename
        if name is None:
            name = [None, None]
        if name[0] is None:
            file_dialog = qwidgets.QFileDialog(self)
            #file_dialog.setFilter(u"XML files (*.xml);;All Files (*.*)")
            filters = "XML files (*.xml);;All Files (*.*)"
            doc_names = file_dialog.getOpenFileName(self, u'Abrir ficheiro XML', self.last_open_dir, filters)
            doc_names = [doc_names[0]]
        else:
            doc_names = [name[0]]
        for doc_ in doc_names:
            doc = str(doc_)
            # Check that the string doc is not empty
            if len(doc) < 1:
                continue

            # Verify that the file is not open already
            if doc in self.open_list:
                meta = self.findChild(MetadadoSNIMar, doc)
                self.tabWidget.setCurrentWidget(meta)
            else:
                # Update the last open dir variable
                if name[0] is None:
                    self.last_open_dir = os.path.dirname(doc)

                # Open the file
                index = self.tabWidget.count()
                try:
                    open(doc, "r")
                except IOError as e:
                    message = QMessageBox(self)
                    message.setWindowTitle(u'Erro ao abrir o ficheiro')
                    message.setIcon(QMessageBox.Critical)
                    message.setText(
                        u'Ocorreu um erro ao abrir )o ficheiro %s.\nEste não é um ficheiro XML válido ou ja não '
                        u'existe.\n Por favor seleccione '
                        u'um '
                        u'ficheiro '
                        u'XML.' % doc)
                    message.show()
                    self.tracked_list.pop(doc, None)
                    self.filetable.model().removeSpecificRow(name[1])
                    return

                md = validation.validate(doc)

                if md is None:
                    message = QMessageBox(self)
                    message.setWindowTitle(u'Erro ao abrir o ficheiro')
                    message.setIcon(QMessageBox.Critical)
                    message.setText(
                        u'Ocorreu um erro ao abrir o ficheiro %s.\nEste não é um ficheiro XML válido. Por favor '
                        u'seleccione um ficheiro XML.' % doc)
                    message.show()
                    return
                else:
                    meta = MetadadoSNIMar(self, xml_doc=doc, md=md)
                    meta.setObjectName(doc)

                    if SCOPES.get_code_representation(md.hierarchy) != SCOPES.SERVICES:
                        common = md.identification
                    else:
                        common = md.serviceidentification

                    if common is None:
                        message = QMessageBox(self)
                        message.setWindowTitle(u'Erro ao abrir o ficheiro')
                        message.setIcon(QMessageBox.Critical)
                        message.setText(
                            u'Ocorreu um erro ao abrir o ficheiro %s.\nO metadado está corrupto. Por favor verifique '
                            u'o conteúdo do ficheiro XML.' % doc)
                        message.show()
                        return

                    filelist = {
                        'path': doc, 'name': doc, 'object': meta, 'title': common.title,
                        'doc_type': SCOPES.get_rich_text_translation(md.hierarchy),
                        'id': md.identifier
                    }
                    print('open_metadata_xml_file')
                    self.open_list.track_new_file(**filelist)
                    self.tabWidget.setCurrentIndex(self.tabWidget.addTab(meta, os.path.basename(doc)))

                # Update tracking info
                if name[0] is None and doc not in self.tracked_list:
                    validity = meta.is_doc_Snimar_Valid()
                    self.filetable.model().addNewRow(
                        [SCOPES.get_rich_text_translation(md.hierarchy), common.title, doc, md.identifier,
                         vality_msg(validity), None])
                    self.tracked_list.track_new_file(**filelist)

    @qcore.pyqtSlot()
    def save_metadata_xml_file(self, flag):
        if self.tabWidget.currentIndex() == 0:
            return

        # Load filename where to save
        filedict = None
        but_saveas = False

        # if the name of the file is Novo Ficheiro, or the file is not in the
        # tracking system, launch a save as
        if flag == SAVE_FLAG:
            name = self.tabWidget.currentWidget().objectName()
            if name not in self.tracked_list:
                but_saveas = True

        if flag == SAVEAS_FLAG or but_saveas:
            # Open the Save As dialog and get the filename for the new XML document. Then,
            # convert the filename to unicode.
            doc_ = qwidgets.QFileDialog.getSaveFileName(self, u'Guardar ficheiro XML', self.last_open_dir,
                                                    u"XML files (*.xml);;All Files (*.*)")[0]

            if doc_.strip() == "":
                return

            try:
                doc = str(doc_)
            except UnicodeError as e:
                # fix_print_with_import
                print("ERROR:", e.message)
                doc = doc_

            # Update the open_list for this entry
            path = self.tabWidget.currentWidget().objectName()
            popped_fo = {  # new file case
                           "id": None,
                           "path": "Novo Ficheiro",
                           "added": datetime.datetime.now(),
                           "name": "Novo Ficheiro",
                           "title": None,
                           "doc_type": SCOPES.get_rich_text_translation(SCOPES.get_string_representation(
                               self.tabWidget.currentWidget().scope))
                           }
            if not self.tabWidget.currentWidget().is_new_file:
                popped_fo = self.open_list.pop(path, None)
            else:
                self.tabWidget.currentWidget().is_new_file = False
            if popped_fo is None:
                return

            if len(doc) > 4 and doc[-4:] != '.xml':
                doc = ''.join([doc, '.xml'])
            popped_fo['path'] = doc
            old_name = popped_fo['name']
            popped_fo['name'] = os.path.basename(doc)
            popped_fo['doc_type'] = SCOPES.get_rich_text_translation(SCOPES.get_string_representation(
                self.tabWidget.currentWidget().scope))
            print('save_metadata_xml_file')
            self.open_list.track_new_file(**popped_fo)
        elif flag == SAVE_FLAG and not but_saveas:
            name = self.tabWidget.currentWidget().objectName()

            doc = self.open_list[name]['path']

        self.statusbar.showMessage('A guardar...')

        # Load data in UI into a buffer md object
        md = snimarProfileModel.MD_Metadata()
        xml_tab = self.tabWidget.currentWidget()
        xml_tab.get_tab_data(md)

        # Save to file
        try:
            xml_str = snimarProfileModel.export_xml(md)

            with open(doc, 'w') as fp:
                fp.write(xml_str.encode('utf-8').decode("utf-8"))
                fp.flush()
                fp.close()
                self.statusbar.clearMessage()
                self.statusbar.showMessage('Guardado', 2000)


            # Add to tracking system
            validity = self.tabWidget.currentWidget().is_doc_Snimar_Valid()
            if SCOPES.get_code_representation(md.hierarchy.term) != SCOPES.SERVICES:
                common = md.identification
            else:
                common = md.serviceidentification
            if doc not in self.tracked_list:
                # Update the doc in the open_list file list using the md object
                self.open_list[doc]['id'] = md.identifier
                self.open_list[doc]['title'] = common.title

                self.open_list[doc]['doc_type'] = SCOPES.get_rich_text_translation(md.hierarchy.term)

                # Add document to tracked_list of files
                self.tracked_list.track_new_file(**self.open_list[doc])

                # Update filetable
                self.filetable.model().addNewRow(
                    [SCOPES.get_rich_text_translation(md.hierarchy.term), common.title, doc, md.identifier,
                     vality_msg(validity), None])
            else:
                index = 0
                model_index_title = None
                model_index_status = None

                model_index_valid = None
                for row in self.filetable.model().matrix:
                    if row[1] == doc:
                        model_index_title = self.filetable.model().index(index, 1)
                        model_index_status = self.filetable.model().index(index, 3)
                        model_index_valid = self.filetable.model().index(index, 4)
                        break
                    else:
                        index += 1

                if model_index_title is not None:
                    self.filetable.model().setData(model_index_title, common.title)
                    self.tracked_list[doc]['title'] = common.title

                if model_index_status is not None:
                    self.filetable.model().setData(model_index_status, md.identifier)
                    self.tracked_list[doc]['id'] = md.identifier
                if model_index_valid is not None:
                    self.filetable.model().setData(model_index_valid, vality_msg(validity))
                self.tracked_list[doc]['doc_type'] = SCOPES.get_rich_text_translation(md.hierarchy.term)

            # Update the widget name and tab title
            if (flag == SAVEAS_FLAG or but_saveas) and old_name is not None and len(old_name) > 0:
                widget = self.tabWidget.currentWidget()
                index = self.tabWidget.currentIndex()
                widget.setObjectName(doc)
                self.tabWidget.setTabText(index, self.open_list[doc]['name'])
        except Exception as e:
            traceback.print_exc()
            self.statusbar.clearMessage()
            #self.statusbar.showMessage(e.message + str(type(e)))
            self.statusbar.showMessage(str(e))

        # Save files list,necessary because of the access before
        self.tracked_list.save()

    @qcore.pyqtSlot()
    def start_dir_track(self):
        directory = qwidgets.QFileDialog.getExistingDirectory(self, directory=self.last_open_dir)
        if directory == "":
            return

        # List all files inside directory that end in .xml
        potential_files = os.listdir(directory)
        potential_files = [os.path.join(directory, x) for x in potential_files]
        potential_files = list(filter(os.path.isfile, potential_files))
        potential_files = [x for x in potential_files if x[-4:] == '.xml']

        for f in potential_files:
            if f not in self.tracked_list:
                try:
                    md = snimarProfileModel.MD_Metadata(snimarProfileModel.iso.etree.parse(f))
                    if SCOPES.get_code_representation(md.hierarchy) != SCOPES.SERVICES:
                        common = md.identification
                    else:
                        common = md.serviceidentification
                    self.tracked_list.track_new_file(path=f, name=os.path.basename(f), title=common.title,
                                                     id=md.identifier,
                                                     doc_type=SCOPES.get_rich_text_translation(md.hierarchy))
                    self.filetable.model().addNewRow(
                        [SCOPES.get_rich_text_translation(md.hierarchy), common.title, f, md.identifier, None, None])
                except:
                    continue

    # -------------------------------
    # EditorMetadadosMarswInforbiomares utils
    # -------------------------------
    def load_codelists(self):
        with open(os.path.join(os.path.dirname(__file__),
                               "resourcesFolder/CodeLists/SNIMar_GMXCODELISTS.json")) as json_data:
            self.codelists = json.load(json_data)
        with open(os.path.join(os.path.dirname(__file__), "resourcesFolder/CodeLists/SNIMar_HELPS.json")) as json_help:
            self.helps = json.load(json_help)
        with open(os.path.join(os.path.dirname(__file__),
                               "resourcesFolder/CodeLists/SNIMar_ReferenceSystems.json")) as json_ref:
            self.reference_systems = json.load(json_ref)
        with open(os.path.join(os.path.dirname(__file__), "resourcesFolder/CodeLists/SNIMar_ORGS.json")) as json_ref:
            self.orgs = json.load(json_ref)

    def selected_file_row(self):
        if self.filetable.model().rowCount() < 1 or not self.filetable.selectionModel().hasSelection():
            return None, -1
        row_index = self.filetable.selectionModel().selection().indexes()[0].row()
        path = self.filetable.model().matrix[row_index][2]
        return path, row_index

    def mouse_selected_row(self):
        if self.filetable.model().rowCount() < 1 or not self.filetable.selectionModel().hasSelection():
            return None, -1
        row_index = self.filetable.indexAt(self.mouse_point).row()
        path = self.filetable.model().matrix[row_index][2]
        return path, row_index

    def visualize_file(self):
        if not self.filetable.selectionModel().hasSelection():
            return
        curr_select = self.filetable.indexAt(self.mouse_point)
        row_index = curr_select.row()
        status = qgui.QDesktopServices.openUrl(qcore.QUrl.fromLocalFile(curr_select.model().matrix[row_index][2]))

    @qcore.pyqtSlot()
    def open_list_contacts(self):
        self.dialog = contacts_dialog.ContactsDialog(self, edition_mode=True)
        self.dialog.btn_add_contact_metadata.clicked.connect(
            lambda: self.loadContactObject(self.dialog.output_contact()))
        self.dialog.exec_()

    @qcore.pyqtSlot()
    def open_about(self):
        self.about = About()
        self.about.exec_()

    def check_validity_not_open_file(self, name, index):
        # Get the filename
        doc = name

        # Check that the string doc is not empty
        if doc is None:
            return None

        if len(doc) < 1:
            return None

        # Verify that the file is not open already
        if doc in self.open_list:
            meta = self.findChild(MetadadoSNIMar, doc)
        else:
            # Open the file
            index = self.tabWidget.count()
            try:
                open(doc, "r")
            except IOError:
                message = QMessageBox(self)
                message.setWindowTitle(u'Erro ao abrir o ficheiro')
                message.setIcon(QMessageBox.Critical)
                message.setText(
                    u'Ocorreu um erro ao abrir o ficheiro %s.\nEste não é um ficheiro XML válido ou ja não existe.\n '
                    u'Por favor seleccione '
                    u'um '
                    u'ficheiro '
                    u'XML.' % doc)
                message.show()
                self.tracked_list.pop(doc, None)
                self.filetable.model().removeSpecificRow(index - 1)
                return None
            md = validation.validate(doc)
            if md is None:
                message = QMessageBox(self)
                message.setWindowTitle(u'Erro ao abrir o ficheiro')
                message.setIcon(QMessageBox.Critical)
                message.setText(
                    u'Ocorreu um erro ao abrir o ficheiro %s.\nEste não é um ficheiro XML válido. Por favor '
                    u'seleccione um ficheiro XML.' % doc)
                message.show()
                return None
            else:
                meta = MetadadoSNIMar(self, xml_doc=doc, md=md)
        return meta.is_doc_Snimar_Valid()

    @qcore.pyqtSlot()
    def update_validity(self, index):
        filename_index = self.filetable.model().index(index.row(), 2)
        validity_index = self.filetable.model().index(index.row(), 4)

        validity = self.check_validity_not_open_file(filename_index.data(), validity_index)

        if validity is None:
            return
        self.filetable.model().setData(validity_index, vality_msg(validity))
        self.filetable.model().refresh(self.filetable.model().index(index.row(), 4))

    def close_editor(self):
        try:
            os.remove(os.path.join(os.path.dirname(__file__), "userFiles/.meLock"))
        except OSError:

            pass
        self.close()

    def closeEvent(self, close_event):
        try:
            os.remove(os.path.join(os.path.dirname(__file__), "userFiles/.meLock"))
        except OSError:
            pass

    @qcore.pyqtSlot()
    def launch_update(self):
        # Launch the progress bar dialog
        self.update_dialog = SNIMarThesaurusUpdateDialog(self)
        self.update_dialog.show()

        # Start the updates
        try:
            self.update_dialog.update_thesaurus()
        except Exception as e:
            crit = QMessageBox(QMessageBox.Critical, u'Erro ao atualizar o Thesaurus SNIMar',
                                    u'Ocorreu um erro ao atualizar o Thesaurus SNIMar. Por favor verifique o estado '
                                    u'da sua ligação à rede.\nEntretanto, poderá continuar ' + \
                                    u'a utilizar o editor com uma versão anterior do Thesaurus.' + \
                                    u'\nSe o problema persistir, por favor envie um email para suporte.snimar@ipma.pt '
                                    u'e inclua o seguinte texto:\n\n{}'.format(
                                        e.message))
            crit.setWindowFlags(crit.windowFlags() | Qt.WindowStaysOnTopHint)
            crit.exec_()

        else:
            # Update the GUI stuff
            #self.thesaurus_version.setText(self.update_dialog.thesaurus.latest_stable_version)

            # Update the thesaurus model of all open tabs
            for tab_index in range(self.tabWidget.count()):
                tab = self.tabWidget.widget(tab_index)
                if isinstance(tab, MetadadoSNIMar):
                    tab.keywords.dialog.update_thesaurus_model()
                    tab.keywords.revalidate_snimar_keywords()

        # Close dialog
        self.update_dialog.accept()

    @qcore.pyqtSlot()
    def use_unstable(self):
        #if self.thesaurus_unstable_checkbox.isChecked():
        if True:
            self.update_thesaurus_label(0, stable=False)
        else:
            self.update_thesaurus_label(0, stable=True)

    def update_thesaurus_label(self, version, stable=False):
        version_string = 'v'
        version_string += str(version)
        version_string += '.x' if not stable else '.0'
        #self.thesaurus_version.setText(version_string)

    def editor_dirname(self):
        """
        Returns the name of the directory for the editor contact and working
        metadata lists.
        """
        return os.path.join(os.path.abspath(os.path.expanduser('~')), '.snimar')

    def setup_editor_dir(self):
        if not os.path.exists(self.editor_dirname()):
            os.mkdir(self.editor_dirname())

    def erase_all(self):

        message = QMessageBox()
        message.setModal(True)
        message.setWindowTitle(u'Apagar Lista de Ficheiros')
        message.setIcon(QMessageBox.Warning)
        message.setText(u"Tem a certeza que deseja apagar todos os metadados da lista?\n(Operação Irreversivel!)")
        message.addButton(u'Remover Todos', QMessageBox.AcceptRole)
        message.addButton(u'Cancelar', QMessageBox.RejectRole)
        ret = message.exec_()
        if not ret == QMessageBox.AcceptRole:
            return
        for x in self.filetable.model().matrix:
            if x[2] in self.open_list:
                meta = self.findChild(MetadadoSNIMar, x[2])
                self.tabWidget.removeTab(self.tabWidget.indexOf(meta))
            self.tracked_list.pop(x[2], None)
        self.filetable.model().remove_all()

    def check_conformity_all(self):

        progress_dialog = QProgressDialog(u"Esta operação pode ser demorada, aguarde...   ", u"Cancelar", 0,
                                          len(self.filetable.model().matrix))
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle(u"Validar Todos os Metadados")
        progress_dialog.adjustSize()
        pb = progress_dialog.findChild(QProgressBar)
        if pb:
            pb.setFormat("%v/%m")

        i = 0
        for x in self.filetable.model().matrix:
            validity_index = self.filetable.model().index(i, 4)
            validity = self.check_validity_not_open_file(x[2], x[4])
            if validity is None:
                return
            self.filetable.model().setData(validity_index, vality_msg(validity))
            self.filetable.model().refresh(self.filetable.model().index(i, 4))
            i = i + 1
            if progress_dialog.wasCanceled():
                progress_dialog.close()
                return
            progress_dialog.setValue(progress_dialog.value() + 1)
        progress_dialog.close()

    def save_all_open(self):
        for i in range(1, (self.tabWidget.count())):
            self.tabWidget.setCurrentIndex(i)
            self.save_metadata_xml_file(SAVE_FLAG)

    def edit_meta(self):
        if len(self.filetable.selectionModel().selectedRows()) <= 0:
            return
        for x in sorted(self.filetable.selectionModel().selectedRows(), key=lambda row: row.row(), reverse=True):
            if self.filetable.model().matrix[x.row()][2] in self.open_list:
                continue
            self.open_metadata_xml_file([self.filetable.model().matrix[x.row()][2], x.row()])

    def refresh_codelist(self):

        codelists = ["SNIMar_GMXCODELISTS.json", "SNIMar_HELPS.json", "SNIMar_ORGS.json",
                     "SNIMar_ReferenceSystems.json"]
        for x in codelists:
            url = os.path.join(CONSTANTS.CODELIST_SERVER_URL, x)
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())
                with open(os.path.join(CONSTANTS.SNIMAR_BASE_DIR, "resourcesFolder/CodeLists/" + x), 'w+') as outfile:
                    json.dump(data, outfile)
            except urllib.error.HTTPError as e:
                # fix_print_with_import
                print("ERROR:", e.reason())
                crit = QMessageBox(QMessageBox.Critical, u'Erro ao atualizar as CodeLists',
                                        u'Ocorreu um erro ao atualizar as CodeLists SNIMar. Por favor verifique o '
                                        u'estado da sua ligação à rede.\nEntretanto, poderá continuar ' + \
                                        u'a utilizar o editor com a versão anterior das CodeLists.' + \
                                        u'\nSe o problema persistir, por favor envie um email para '
                                        u'suporte.snimar@ipma.pt e inclua o seguinte texto:\n\n{}'.format(
                                            e.message))
                crit.setWindowFlags(crit.windowFlags() | Qt.WindowStaysOnTopHint)
                crit.exec_()

        message = QMessageBox()
        message.setModal(True)
        message.setWindowTitle(u'CodeLists Actualizadas')
        message.setIcon(QMessageBox.Information)
        message.setText(u"Reinicie o Editor para refletir as alterações")
        message.addButton(u'OK', QMessageBox.AcceptRole)
        ret = message.exec_()

    def resave_all_in_list(self):

        progress_dialog = QProgressDialog(u"Esta operação pode ser demorada, aguarde...   ", u"Cancelar", 0,
                                          len(self.filetable.model().matrix))
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle(u"Atualizar Metadados")
        progress_dialog.adjustSize()
        pb = progress_dialog.findChild(QProgressBar)
        if pb:
            pb.setFormat("%v/%m")

        i = 0
        for x in self.filetable.model().matrix:
            i += 1
            self.resave_metadata(x[2])
            if progress_dialog.wasCanceled():
                progress_dialog.close()
                return
            progress_dialog.setValue(progress_dialog.value() + 1)
        progress_dialog.close()

    def resave_metadata(self, name):
        # Get the filename
        doc = name

        # Check that the string doc is not empty
        if doc is None:
            return None

        if len(doc) < 1:
            return None

        try:
            open(doc, "r")
        except IOError:
            return None
        md = validation.validate(doc)
        if md is None:
            return None
        else:
            meta = MetadadoSNIMar(self, xml_doc=doc, md=md)
            meta.setObjectName(doc)
            # Load data in UI into a buffer md object
            md = snimarProfileModel.MD_Metadata()
            meta.get_tab_data(md)
            try:
                xml_str = snimarProfileModel.export_xml(md)
                with open(doc, 'w') as fp:
                    fp.write(xml_str.encode('utf-8').decode('utf-8'))
                    fp.flush()
                    fp.close()
            except Exception as e:
                traceback.print_exc()
