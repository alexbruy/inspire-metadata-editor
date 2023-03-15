import platform
import json

from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtNetwork

from qgis.PyQt.QtWidgets import QAbstractItemView, QSizePolicy, QLabel, QDialog

from EditorMetadadosMarswInforbiomares.snimarEditorController.models import TableModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import wormsDialog


class WormsKeywordsDialog(QtWidgets.QDialog, wormsDialog.Ui_worms_dialog):
    def __init__(self, parent):
        super(WormsKeywordsDialog, self).__init__(parent)
        if platform.system() != "Linux":
            font = qgui.QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)
        self.setModal(True)

        # Table setup
        self.results_table.setColumnHidden(1, True)
        self.wk_model = TableModel(self, [u"Nome", 'date'], [QtWidgets.QLineEdit, QtWidgets.QLineEdit], self.results_table)
        self.results_table.setModel(self.wk_model)
        self.results_table.setColumnHidden(1, True)
        self.results_table.resizeColumnsToContents()
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.resizeRowsToContents()
        self.results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.results_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.results_table.selectionModel().selectionChanged.connect(self.handle_selection_change)

        # Close the dialog window
        self.btn_close_dialog.clicked.connect(lambda: self.done(0))

        # Setup search
        self.btn_search.clicked.connect(self.search_thesaurus)

        # Setup add row
        self.add_row_btn.clicked.connect(self.add_keyword)

    def search_thesaurus(self):
        """
        Send request to the WORMS API
        """
        network_manager = QtNetwork.QNetworkAccessManager(self)

        while self.wk_model.rowCount() > 0:
            self.wk_model.removeSpecificRow(self.wk_model.rowCount() - 1)

        name = self.name_edit.text()
        if name and len(name) > 0:
            request_name_url = 'https://www.marinespecies.org/rest/AphiaRecordsByName/{}'.format(name.replace(' ', '+'))
            request_name = QtNetwork.QNetworkRequest(qcore.QUrl(request_name_url))
            reply_name = network_manager.get(request_name)

            def process_name_search():
                if reply_name.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute) > 200:
                    return
                data = json.loads(str(reply_name.readAll(), 'utf-8'))
                for item in data:
                    self.wk_model.addNewRow([item['scientificname'], item['modified'].split('T')[0]])

            reply_name.finished.connect(process_name_search)

        vernacular = self.vernacular_edit.text()
        if vernacular and len(vernacular) > 0:
            request_vernacular_url = 'https://www.marinespecies.org/rest/AphiaRecordsByVernacular/{}'.format(vernacular.replace(' ', '+'))
            request_vernacular = QtNetwork.QNetworkRequest(qcore.QUrl(request_vernacular_url))
            reply_vernacular = network_manager.get(request_vernacular)

            def process_vernacular_search():
                if reply_vernacular.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute) > 200:
                    return
                data = json.loads(str(reply_vernacular.readAll(), 'utf-8'))
                for item in data:
                    self.wk_model.addNewRow([item['scientificname'], item['modified'].split('T')[0]])

            reply_vernacular.finished.connect(process_vernacular_search)

        identifier = self.identifier_edit.text()
        if identifier and len(identifier) > 0:
            request_identifier_url = 'https://www.marinespecies.org/rest/AphiaRecordByAphiaID/{}'.format(identifier.replace(' ', '+'))
            request_identifier = QtNetwork.QNetworkRequest(qcore.QUrl(request_identifier_url))
            reply_identifier = network_manager.get(request_identifier)

            def process_identifier_search():
                if reply_identifier.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute) > 200:
                    return
                data = json.loads(str(reply_identifier.readAll(), 'utf-8'))
                self.wk_model.addNewRow([data['scientificname'], data['modified'].split('T')[0]])

            reply_identifier.finished.connect(process_identifier_search)


    def handle_selection_change(self, selected, deselected):
        self.add_row_btn.setEnabled(True)
        self.current_selection = [item.data() for item in selected.indexes()]

    def add_keyword(self):
        selection = self.results_table.selectionModel()
        self.parent().wormskeywords.model().addNewRow(self.current_selection)
