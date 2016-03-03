from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg \
			    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D       


class MplCanvas(FigureCanvas):
 
    def __init__(self):
	self.fig = Figure()
	
	#self.ax.mouse_init()   # keine wirkung
	self.ax = self.fig.add_subplot(111, projection='3d')
	FigureCanvas.__init__(self, self.fig)
	FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,\
					QtGui.QSizePolicy.Expanding)
	FigureCanvas.updateGeometry(self)
	

 
 
class matplotlibWidget(QtGui.QWidget):
 
    def __init__(self, parent = None):
	QtGui.QWidget.__init__(self, parent)
	self.canvas = MplCanvas()


