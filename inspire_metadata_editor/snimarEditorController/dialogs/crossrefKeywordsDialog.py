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
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import crossrefDialog


def build_author_string(authors):
    author_list = []

    for author in authors:
        name = '{}, {}'.format(author['family'], author['given']) if 'given' in author else '{}'.format(author['family'])
        author_list.append(name)

    return ', '.join(author_list)


class CrossrefKeywordsDialog(QtWidgets.QDialog, crossrefDialog.Ui_crossref_dialog):
    def __init__(self, parent):
        super(CrossrefKeywordsDialog, self).__init__(parent)
        if platform.system() != "Linux":
            font = qgui.QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)
        self.setModal(True)

        # Table setup
        self.results_table.setColumnHidden(2, True)
        self.results_table.setColumnHidden(3, True)
        self.wk_model = TableModel(self, [u"Autor", u"Título", "DOI", "date"], [QtWidgets.QLineEdit, QtWidgets.QLineEdit, QtWidgets.QLineEdit, QtWidgets.QLineEdit], self.results_table)
        self.results_table.setModel(self.wk_model)
        self.results_table.setColumnHidden(2, True)
        self.results_table.setColumnHidden(3, True)
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
        self.btn_search.clicked.connect(self.reset_search)

        # Setup add row
        self.add_row_btn.clicked.connect(self.add_keyword)

        # Pagination
        self.page = 0
        self.previous_page.clicked.connect(self.get_previous_page)
        self.next_page.clicked.connect(self.get_next_page)

    def reset_search(self):
        self.page = 0
        self.current_page.setText('Pag. inicial')
        self.search_thesaurus()

    def get_previous_page(self):
        self.page -= 1
        if self.page < 0:
            self.reset_search()
        else:
            self.current_page.setText('Pag. {}'.format(self.page))
            self.search_thesaurus()

    def get_next_page(self):
        self.page += 1
        self.current_page.setText('Pag. {}'.format(self.page))
        self.search_thesaurus()

    def search_thesaurus(self):
        """
        Send request to the crossref API
        """
        network_manager = QtNetwork.QNetworkAccessManager(self)
        print('call search', self.page)

        while self.wk_model.rowCount() > 0:
            self.wk_model.removeSpecificRow(self.wk_model.rowCount() - 1)

        author = self.author_edit.text()
        title = self.title_edit.text()

        base_url = 'https://api.crossref.org/works'
        params = []
        if author and len(author) > 0:
            params.append('query.author={}'.format(author.replace(' ', '+')))

        if title and len(title) > 0:
            params.append('query.container-title={}'.format(title.replace(' ', '+')))

        if len(params) > 0:
            params.append('offset={}'.format(self.page * 20))
            url = '{}?{}'.format(base_url, '&'.join(params))
            print(url)

            self.search_status.setText('A pesquisar')
            request = QtNetwork.QNetworkRequest(qcore.QUrl(url))
            reply = network_manager.get(request)

            def process_crossref_search():
                if reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute) > 200:
                    self.search_status.setText('Erro')
                    return

                self.search_status.setText('Concluido')
                data = json.loads(str(reply.readAll(), 'utf-8'))

                for item in data['message']['items']:
                    try:
                        if (len(item['title']) < 1 or len(item['title'][0]) < 1) or len(item['author']) < 1:
                            continue

                        self.wk_model.addNewRow([
                            build_author_string(item['author']),
                            item['title'][0],
                            item['DOI'],
                            item['created']['date-time'].split('T')[0],
                        ])
                    except:
                        continue

            reply.finished.connect(process_crossref_search)


    def handle_selection_change(self, selected, deselected):
        self.add_row_btn.setEnabled(True)
        self.current_selection = [item.data() for item in selected.indexes()]

    def add_keyword(self):
        selection = self.results_table.selectionModel()
        self.parent().crossrefkeywords.model().addNewRow([
            self.current_selection[0], self.current_selection[2], self.current_selection[3],
        ])
        self.parent().crossrefkeywords.model().addNewRow([
            self.current_selection[1], self.current_selection[2], self.current_selection[3],
        ])
