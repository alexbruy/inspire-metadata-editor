# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/extent_dialog.py
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
from builtins import range
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
from qgis import core, utils, gui
import qgis

import os
import platform
from qgis.PyQt.QtWidgets import QToolTip, QDialog
from qgis.PyQt.QtGui import QCursor, QFont

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import \
    chooseGeographicExtentOnMapDialog  as mdextent
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import \
    geographicinformationPanel
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import \
    chooseGeographicExtentFromLayer as ly_extent


class SelectionTool(gui.QgsMapToolEmitPoint):
    def __init__(self, canvas, parent):
        self.canvas = canvas
        gui.QgsMapToolEmitPoint.__init__(self, self.canvas)
        #self.tmp_band = gui.QgsRubberBand(self.canvas, core.QGis.Polygon)
        self.tmp_band = gui.QgsRubberBand(self.canvas)#, qgis.core.QgsWkbTypes.Polygon)
        #self.tmp_band.setBorderColor(qcore.Qt.yellow)
        self.tmp_band.setStrokeColor(qcore.Qt.yellow)
        self.tmp_band.setFillColor(qcore.Qt.transparent)
        self.tmp_band.setWidth(3)
        self.reset()
        self.parent = parent

    def reset(self):
        self.start_point = self.end_point = None
        self.emitting_point = False
        self.tmp_band.reset() #core.QGis.Polygon)

    def canvasPressEvent(self, e):
        self.start_point = self.toMapCoordinates(e.pos())
        self.end_point = self.start_point
        self.emitting_point = True
        self.showRect(self.start_point, self.end_point)

    def canvasReleaseEvent(self, e):
        self.emitting_point = False
        r = self.rectangle()
        if r is not None:
            # Set the spinboxes with the current selection values
            self.parent.xMin.setValue(r.xMinimum())
            self.parent.xMax.setValue(r.xMaximum())
            self.parent.yMin.setValue(r.yMinimum())
            self.parent.yMax.setValue(r.yMaximum())

    def canvasMoveEvent(self, e):
        if not self.emitting_point:
            return

        self.end_point = self.toMapCoordinates(e.pos())
        self.showRect(self.start_point, self.end_point)

    def showRect(self, start, end):
        self.tmp_band.reset() #core.QGis.Polygon)
        if start.x() == end.x() or start.y() == end.y():
            return

        point1 = core.QgsPointXY(start.x(), start.y())
        point2 = core.QgsPointXY(start.x(), end.y())
        point3 = core.QgsPointXY(end.x(), end.y())
        point4 = core.QgsPointXY(end.x(), start.y())

        self.tmp_band.addPoint(point1, False)
        self.tmp_band.addPoint(point2, False)
        self.tmp_band.addPoint(point3, False)
        self.tmp_band.addPoint(point4, False)  # true to update canvas
        self.tmp_band.addPoint(point1, True)
        self.tmp_band.show()

    def rectangle(self):
        if self.start_point is None or self.end_point is None:
            self.resetLimites()
            return None
        elif self.start_point.x() == self.end_point.x() or self.start_point.y() == \
                self.end_point.y():
            self.resetLimites()
            return None

        return core.QgsRectangle(self.start_point, self.end_point)

    def resetLimites(self):
        # Clean coords
        self.parent.xMin.setValue(0.)
        self.parent.xMax.setValue(0.)
        self.parent.yMin.setValue(0.)
        self.parent.yMax.setValue(0.)

    def drawRect(self, minx, miny, maxx, maxy):
        self.tmp_band.reset() #(core.QGis.Polygon)

        point1 = core.QgsPointXY(minx, miny)
        point2 = core.QgsPointXY(minx, maxy)
        point3 = core.QgsPointXY(maxx, maxy)
        point4 = core.QgsPointXY(maxx, miny)

        self.tmp_band.addPoint(point1, False)
        self.tmp_band.addPoint(point2, False)
        self.tmp_band.addPoint(point3, False)
        self.tmp_band.addPoint(point4, False)  # true to update canvas
        self.tmp_band.addPoint(point1, True)
        self.tmp_band.show()

    def deactivate(self):
        super(SelectionTool, self).deactivate()
        self.emit(qcore.SIGNAL('deactivated()'))


class ExtentDialog(QDialog, mdextent.Ui_MDExtentDialogBase):
    def __init__(self, parent, boundingbox):
        super(ExtentDialog, self).__init__(parent)
        self.setupUi(self)
        self.superParent = None
        temp = self.parent()
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        while self.superParent is None:
            if issubclass(type(temp), geographicinformationPanel.Ui_geographicinfo):
                self.superParent = temp
            else:
                temp = temp.parent()
        for info in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        self.layers = []
        self.maxExt = None
        self.boundingbox = boundingbox
        self.outBB = False

        # Create MapCanvas
        self.canvas = gui.QgsMapCanvas(self)

        # Append to Dialog Layout
        self.toolBar = qwidgets.QToolBar()
        self.layout = qwidgets.QVBoxLayout(self.frame)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.canvas)

        # Trigger on scaleChanged
        self.canvas.scaleChanged.connect(self.scaleChanged)
        # Trigger on renderStarting
        self.canvas.renderStarting.connect(self.renderStarting)

        # Create Map Tools
        actionFullExt = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/globe.svg'), "Mapa total",
                                     self)
        actionPan = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/pan.svg'), "Mover", self)
        actionZoomIn = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/zoom_in.svg'), "Aproximar",
                                    self)
        actionZoomOut = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/zoom_out.svg'), "Afastar",
                                     self)
        actionSelect = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/selection.svg'), 'Desenhar',
                                    self)
        actionFromLayer = qwidgets.QAction(qgui.QIcon(':/resourcesFolder/icons/layers.svg'),
                                       'Obter de camada', self)

        actionFullExt.setCheckable(False)
        actionPan.setCheckable(True)
        actionZoomIn.setCheckable(True)
        actionZoomOut.setCheckable(True)
        actionSelect.setCheckable(True)

        actionFullExt.triggered.connect(self.fullext)
        actionPan.triggered.connect(self.pan)
        actionZoomIn.triggered.connect(self.zoomIn)
        actionZoomOut.triggered.connect(self.zoomOut)
        actionSelect.triggered.connect(self.select)
        actionFromLayer.triggered.connect(self.chooseLayer)

        # Add to created ToolBar
        self.toolBar.addAction(actionFullExt)
        self.toolBar.addSeparator()
        self.toolBar.addAction(actionPan)
        self.toolBar.addAction(actionZoomIn)
        self.toolBar.addAction(actionZoomOut)
        self.toolBar.addAction(actionSelect)
        self.toolBar.addAction(actionFromLayer)

        self.toolFullExtent = gui.QgsMapToolPan(self.canvas)
        self.toolFullExtent.setAction(actionFullExt)
        self.toolPan = gui.QgsMapToolPan(self.canvas)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = gui.QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = gui.QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(actionZoomOut)
        self.toolSelect = SelectionTool(self.canvas, self)
        self.resourcebox.setChecked(True)
        self.pan()

        plugin_path = utils.pluginDirectory('EditorMetadadosMarswInforbiomares')

        # Load Vector
        layerpath = os.path.join(plugin_path, "resourcesFolder/World.shp")
        llayer = core.QgsVectorLayer(layerpath, "WorldLayer", "ogr")

        # Set Layer Symbology
        props = {'color_border': '0,0,0,125', 'style': 'no', 'style_border': 'solid'}
        #s = core.QgsFillSymbolV2.createSimple(props)
        s = core.QgsFillSymbol.createSimple(props)
        #llayer.setRendererV2(core.QgsSingleSymbolRendererV2(s))
        llayer.setRenderer(core.QgsSingleSymbolRenderer(s))

        # Set CRS - necessary to load Raster - it assumes this default CRS
        s = qcore.QSettings()
        oldValidation = str(s.value("/Projections/defaultBehaviour", "useGlobal"))
        s.setValue("/Projections/defaultBehaviour", "useGlobal")

        # Load Raster
        fileName = os.path.join(plugin_path, "resourcesFolder/GMRT.tif")
        fileInfo = qcore.QFileInfo(fileName)
        baseName = fileInfo.baseName()
        layer = core.QgsRasterLayer(fileName, baseName)
        layer.setCrs(
            core.QgsCoordinateReferenceSystem(4326, core.QgsCoordinateReferenceSystem.EpsgCrsId))
        s.setValue("/Projections/defaultBehaviour", oldValidation)

        # Set Raster ColorRamp
        # layer.setDrawingStyle("SingleBandPseudoColor") # deprecated remove in 2.1.0 please
        vmin = -5683.08
        vmax = 2763.86
        vrange = vmax - vmin
        vadd = vrange // 2
        vint = vmin + vadd
        colDic = {'brown': '#90330a', 'lightblue': '#d5f5f9', 'blue': '#2099d4'}
        valueList = [vmin, vint, vmax]

        lst = [core.QgsColorRampShader.ColorRampItem(valueList[0], qgui.QColor(colDic['blue'])), \
               core.QgsColorRampShader.ColorRampItem(valueList[1],
                                                     qgui.QColor(colDic['lightblue'])), \
               core.QgsColorRampShader.ColorRampItem(valueList[2], qgui.QColor(colDic['brown']))]
        myRasterShader = core.QgsRasterShader()
        myColorRamp = core.QgsColorRampShader()
        myColorRamp.setColorRampItemList(lst)
        myColorRamp.setColorRampType(core.QgsColorRampShader.Interpolated)
        myRasterShader.setRasterShaderFunction(myColorRamp)
        myPseudoRenderer = core.QgsSingleBandPseudoColorRenderer(layer.dataProvider(), layer.type(),
                                                                 myRasterShader)
        layer.setRenderer(myPseudoRenderer)

        ## Add vector to map
        #core.QgsMapLayerRegistry.instance().addMapLayer(llayer, False)
        core.QgsProject.instance().addMapLayer(llayer, False)
        ## Add raster to map
        #core.QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        core.QgsProject.instance().addMapLayer(layer, False)

        ## Save Max Extent
        self.maxExt = core.QgsRectangle(-180., -90., 180., 90.)

        # ----------------------------------
        ## Set initial general extent to ZEE or, if one is selected, from the selected boundingbox
        if self.boundingbox.selectionModel().hasSelection() == False:
            ## Change button's title
            self.add_extent.setText(u"Adicionar")
            initialrect = core.QgsRectangle(-46.63064, 22.52146, 9.64473, 47.31826)
        else:
            ## Get selected bounding box coords and resource flag
            index = self.boundingbox.selectionModel().selectedRows()[0].row()
            row = self.boundingbox.model().matrix[index]

            minx = float(row[0].replace(',', '.'))
            miny = float(row[3].replace(',', '.'))
            maxx = float(row[1].replace(',', '.'))
            maxy = float(row[2].replace(',', '.'))

            if minx == 0. and miny == 0. and maxx == 0. and maxy == 0.:
                initialrect = core.QgsRectangle(-46.63064, 22.52146, 9.64473, 47.31826)
            else:
                ## Set fields with these values
                self.xMin.setValue(minx)
                self.xMax.setValue(maxx)
                self.yMin.setValue(miny)
                self.yMax.setValue(maxy)
                self.resourcebox.setChecked(bool(row[4]))

                ## Set the extent and add a bit of zoom out of the selected extent
                initialrect = core.QgsRectangle(minx - minx * 0.1, miny - miny * 0.1,
                                                maxx + maxx * 0.1, maxy + maxy * 0.1)

                ## Draw initial extent on the map
                self.toolSelect.drawRect(minx, miny, maxx, maxy)

                ## Change button's title
                self.add_extent.setText(u"Alterar")

        self.canvas.setExtent(initialrect)
        # ----------------------------------

        ## Append layers to MapCanvas
        self.layers.append(llayer)
        self.layers.append(layer)
        #self.layers.append(gui.QgsMapCanvasLayer(llayer))
        #self.layers.append(gui.QgsMapCanvasLayer(layer))
        #self.canvas.setLayerSet(self.layers)
        self.canvas.setLayers([llayer, layer])

        ## Set triggers to buttons
        self.add_extent.clicked.connect(self.add_new_extent)
        self.btn_close.clicked.connect(lambda: self.done(QDialog.Rejected))
        self.finished.connect(self.cleanup)

        ## Disabled coord fields
        self.xMin.setEnabled(False)
        self.xMax.setEnabled(False)
        self.yMin.setEnabled(False)
        self.yMax.setEnabled(False)

    def cleanup(self):
        for layer in self.layers:
            #core.QgsMapLayerRegistry.instance().removeMapLayer(layer.layer().id())
            core.QgsProject.instance().removeMapLayer(layer.id())

    ## Toolbar actions:
    ## Zoom In
    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)
        # uncheck Select
        self.toolBar.actions()[5].setChecked(False)

    ## Zoom Out
    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)
        # uncheck Select
        self.toolBar.actions()[5].setChecked(False)

    ## Pan Map
    def pan(self):
        self.canvas.setMapTool(self.toolPan)
        # uncheck Select
        self.toolBar.actions()[5].setChecked(False)

    ## Draw Extent on map
    def select(self, e):
        if e:
            self.canvas.setMapTool(self.toolSelect)
        else:
            self.canvas.setMapTool(self.toolPan)

            ## Zoom to Max Extent

    def fullext(self):
        try:
            self.canvas.setExtent(self.maxExt)
            self.canvas.refresh()
        except:
            return

    ## Get extent from layer
    def chooseLayer(self):
        self.dlg = ChooseLayerDialog()
        self.dlg.show()

        result = self.dlg.exec_()
        if result:
            # get layer instance from comboBox
            layer = self.dlg.layer

            # If "use selected features only" create extent from selected features
            if self.dlg.selectionCheckBox.isChecked():
                f_count = layer.selectedFeatureCount()
                features = layer.selectedFeatures()
                box = features[0].geometry().boundingBox()
                for i in range(1, f_count):
                    fbbox = features[i].geometry().boundingBox()
                    box.combineExtentWith(fbbox)
            else:  # No features selected get bounding box of entire layer
                box = layer.extent()

            source_crs = layer.crs()
            dest_crs = core.QgsCoordinateReferenceSystem(4326)
            if source_crs != dest_crs:
                transform = core.QgsCoordinateTransform(source_crs, dest_crs, core.QgsProject.instance())
                extent = transform.transformBoundingBox(box)
            else:
                extent = box

            self.xMin.setValue(extent.xMinimum())
            self.xMax.setValue(extent.xMaximum())
            self.yMin.setValue(extent.yMinimum())
            self.yMax.setValue(extent.yMaximum())

            self.toolSelect.drawRect(extent.xMinimum(), extent.yMinimum(), extent.xMaximum(),
                                     extent.yMaximum())
        return

    ## Map actions:
    ## Check if zoom is out of the Max Extent
    def scaleChanged(self):
        ext = self.canvas.extent()
        if ext.xMinimum() < self.maxExt.xMinimum() or ext.xMaximum() > self.maxExt.xMaximum() \
                or ext.yMinimum() < self.maxExt.yMinimum() or ext.yMaximum() > \
                self.maxExt.yMaximum():
            self.outBB = True
        else:
            self.outBB = False

    ## On Map render check if out of Max Extent and if so set to max extent
    def renderStarting(self):
        if self.outBB:
            try:
                self.canvas.setExtent(self.maxExt)
                self.outBB = False
                self.canvas.refresh()
            except:
                return

    @qcore.pyqtSlot()
    def add_new_extent(self):
        # If Coords filled then add them or update them to the boundingbox view
        if self.xMin.value() == 0. and self.xMax.value() == 0. and self.yMin.value() == 0. and \
                        self.yMax.value() == 0.:
            qgui.QMessageBox.warning(self, u"Alerta",
                                     u"Não existe seleção desenhada no mapa.\nUse a ferramenta "
                                     u"'Desenhar'.")
        else:
            flag = self.resourcebox.isChecked()

            xMin = str(self.xMin.value()).replace(".", ",")
            xMax = str(self.xMax.value()).replace(".", ",")
            yMax = str(self.yMax.value()).replace(".", ",")
            yMin = str(self.yMin.value()).replace(".", ",")

            new_row = [str(xMin), str(xMax), str(yMax), str(yMin), flag]

            ## If coords selected then instead of adding new extent we update the selected one
            if self.boundingbox.selectionModel().hasSelection() == False:
                self.boundingbox.model().addNewRow(new_row)
            else:
                index = self.boundingbox.selectionModel().selectedRows()[0].row()
                row = self.boundingbox.model().index(index, 0)
                self.boundingbox.model().setDataRow(row, new_row)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(
            self.superParent.superParent.helps['chooseGeographicExtentOnMapDialog'][
                self.sender().objectName()]), None)


class ChooseLayerDialog(QDialog, ly_extent.Ui_Dialog):
    def __init__(self, parent=None):
        super(ChooseLayerDialog, self).__init__(parent)
        self.setupUi(self)

        self.selectionCheckBox.setEnabled(False)
        self.selectionCheckBox.setChecked(False)
        self.layer = self.mMapLayerComboBox.currentLayer()

        # Triggers for dialog behaviour
        self.mMapLayerComboBox.layerChanged.connect(self.checkSelectedFeatures)

        # Check first item
        self.checkSelectedFeatures()

    def checkSelectedFeatures(self):
        """
        Enable and Disable use selected features only checkbox
        """

        # Try disconnect trigger on previews layer
        # try:
        #     self.layer.selectionChanged.disconnect()
        # except:
        #     pass

        self.layer = self.mMapLayerComboBox.currentLayer()

        if isinstance(self.layer, core.QgsVectorLayer):
            if self.layer.selectedFeatureCount() > 0:
                self.selectionCheckBox.setEnabled(True)
            else:
                self.selectionCheckBox.setEnabled(False)
                self.selectionCheckBox.setCheckState(False)

                # connect trigger to monitor feature selection changes
                # self.layer.selectionChanged.connect(self.checkSelectedFeatures)
        else:
            self.selectionCheckBox.setEnabled(False)
