from qgis.PyQt.QtWidgets import QDialog
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import wormsDialog


class WormsDialog(QDialog, wormsDialog.Ui_worms_dialog):
    """
    Dialog used to allow users to query the Worms REST API.
    """
    def __init__(self, parent):
        super(WormsDialog, self).__init__(parent)
