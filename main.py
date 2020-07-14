import os
import sys
import threading
from PySide2.QtGui import QKeyEvent
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide2.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLineEdit, QMainWindow, QPushButton, QSizePolicy, QTabWidget, QVBoxLayout, QWidget
from PySide2.QtCore import Qt
import pyqtgraph.opengl as gl
import data_loader

class TopDownView(FigureCanvas):
    '''Top down view of cross-sectional image'''

    def __init__(self):
        try:
            mpl.set_loglevel('error')
        except AttributeError:
            pass
        self._fig = Figure(figsize=(10, 10), dpi=100)
        FigureCanvas.__init__(self, self._fig)
        self._axes = self._fig.add_subplot(111)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def set_data(self, data):
        '''Update data set to view in tab'''
        self._axes.imshow(np.mean(data, axis=2))
        self.draw()


class ModelView(gl.GLViewWidget):
    '''3D View of data'''

    def __init__(self):
        super().__init__()
        self._xgrid = gl.GLGridItem(color=(255, 0, 0))
        self._xgrid.setSize(512, 512, 512)
        self._xgrid.setSpacing(x=1, y=1, z=1)
        self._ygrid = gl.GLGridItem(color=(0, 255, 0))
        self._ygrid.setSize(512, 512, 512)
        self._ygrid.setSpacing(x=1, y=1, z=1)
        self._zgrid = gl.GLGridItem(color=(0, 0, 255))
        self._zgrid.setSize(512, 512, 512)
        self._zgrid.setSpacing(x=1, y=1, z=1)
        self._scatter = gl.GLScatterPlotItem()
        self._xgrid.rotate(90, 1, 0, 0)
        self._ygrid.rotate(90, 0, 1, 0)
        self.addItem(self._xgrid)
        self.addItem(self._ygrid)
        self.addItem(self._zgrid)
        self.addItem(self._scatter)
        self.show()
    
    def _setData(self, x_data, y_data, z_data, color=[1.0, 1.0, 1.0, 100]):
        self._scatter.setData(pos=np.array(np.array(list(zip(x_data, y_data, z_data)))), size=0.0005, pxMode=True)

    def set_data(self, data):
        coordinates = np.where(data == 1)
        self._setData(coordinates[0] - 256, coordinates[1] - 256, coordinates[2] - 128)

class TabWidget(QWidget):
    def __init__(self, parent):
        super(TabWidget, self).__init__(parent)
        self._layout = QVBoxLayout(self)
        self._load_btn = QPushButton("Load Directory")
        self._load_btn.clicked.connect(self._load_data)

        nav_widgets = QWidget(self)
        nav_layout = QHBoxLayout(nav_widgets)
        nav_layout.addWidget(self._load_btn)

        self._layout.addWidget(nav_widgets)

        self._tab_container = QTabWidget()
        self._tabs = [[TopDownView(), "Top Down View"],
                      [ModelView(), "3D Model"]]
        for tab in self._tabs:
            self._tab_container.addTab(tab[0], tab[1])
        self._layout.addWidget(self._tab_container)
        self._data_set = []
        self._data_set_index = 0
        self.setLayout(self._layout)

    def keyPressEvent(self, event):
        if not self._data_set:
            return
        if event.key() == Qt.Key_Equal:
            self._data_set_index = (self._data_set_index + 1) % len(self._data_set)
        elif event.key() == Qt.Key_Minus:
            self._data_set_index = (self._data_set_index - 1) % len(self._data_set)
        for tab in self._tabs:
            tab[0].set_data(self._data_set[self._data_set_index])

    def _load_data(self):
        fdiag = QFileDialog(self)
        fdiag.setDirectory(os.path.curdir)
        fdiag.setFileMode(QFileDialog.ExistingFiles)
        fdiag.setNameFilters("*.nrrd")
        if fdiag.exec_():
            fnames = fdiag.selectedFiles()
            self._data_set = []
            self._data_set_index = 0
            for index, name in enumerate(fnames):
                data, header = data_loader.load(name)
                self._data_set.append(data)
            if self._data_set:
                for tab in self._tabs:
                    tab[0].set_data(self._data_set[0])
            

class MedVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Image Visualizer")
        self._tab_widget = TabWidget(self)
        self.setCentralWidget(self._tab_widget)
        self.show()

app = QApplication(sys.argv)
win = MedVisualizer()
sys.exit(app.exec_())