# coding=utf-8
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtGui import QPixmap, QIcon
from qgis.PyQt import QtCore
import EditorMetadadosMarswInforbiomares
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import about
from EditorMetadadosMarswInforbiomares import resources


class About(QDialog, about.Ui_About):
    def __init__(self):
        super(About, self).__init__()
        self.setupUi(self)
        self.version.setText(u"Versão:" + EditorMetadadosMarswInforbiomares.__version__)
        self.pushButton.clicked.connect(lambda: self.done(1))

        #inforbiomares = QPixmap(":/resourcesFolder/infor_biomares_.png")
        #inforbiomares_icon = QIcon()
        #inforbiomares_icon.addPixmap(inforbiomares)
        #self.inforbiomares_btn.setIcon(inforbiomares_icon)
        #self.inforbiomares_btn.setIconSize(inforbiomares.rect().size())

        #marsw = QPixmap(":/resourcesFolder/marsw.png")
        #marsw_icon = QIcon()
        #marsw_icon.addPixmap(marsw)
        #self.marsw

        #icnf = QPixmap(":/resourcesFolder/icnf.png")
        #icnf_icon = QIcon()
        #icnf_icon.addPixmap(icnf)
        #self.icnf_btn.setIcon(icnf_icon)
        #self.icnf_btn.setIconSize(icnf.rect().size())

        #lpn = QPixmap(":/resourcesFolder/lpn_.jpg")
        #lpn_icon = QIcon()
        #lpn_icon.addPixmap(lpn)
        #self.lpn_btn.setIcon(lpn_icon)
        #self.lpn_btn.setIconSize(lpn.rect().size())

        #fcul = QPixmap(":/resourcesFolder/fcul_.png")
        #fcul_icon = QIcon()
        #fcul_icon.addPixmap(fcul)
        #self.fcul_btn.setIcon(fcul_icon)
        #self.fcul_btn.setIconSize(fcul.rect().size())

        #ue = QPixmap(":/resourcesFolder/univ_evora_.png")
        #ue_icon = QIcon()
        #ue_icon.addPixmap(ue)
        #self.ue_btn.setIcon(ue_icon)
        #self.ue_btn.setIconSize(ue.rect().size())
