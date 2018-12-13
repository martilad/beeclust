from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg, uic
from beeclust.beeclustClass import MapConst
from beeclust.About import ABOUT
import numpy
import os
import sys


CELL_SIZE = 45
VALUE_ROLE = QtCore.Qt.UserRole
PICTURES = {'grass': 0, 'wall': 5, 'heater': 6, 'cooler': 7, 'bee': -1, 'up': 1, 'down': 3, 'right': 2, 'left': 4}


def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):

    def __init__(self, array, images):
        super().__init__()
        self.images = images
        # TODO: beeclust map here use
        self.array = array
        size = logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)
        self.selected = None

    def paintEvent(self, event):
        rect = event.rect()

        # zjistíme, jakou oblast naší matice to představuje
        # nesmíme se přitom dostat z matice ven
        row_min, col_min = pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = logical_to_pixels(row, column)

                rect = QtCore.QRectF(x, y, CELL_SIZE, CELL_SIZE)

                # podkladová barva pod poloprůhledné obrázky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # grass add everywhere
                self.images['grass'].render(painter, rect)

                # Place right images on possitions
                if self.array[row, column] == PICTURES["wall"]:
                    self.images['wall'].render(painter, rect)
                if self.array[row, column] <= PICTURES["bee"]:
                    self.images['bee'].render(painter, rect)
                if self.array[row, column] == PICTURES["up"]:
                    self.images['up'].render(painter, rect)
                if self.array[row, column] == PICTURES["down"]:
                    self.images['down'].render(painter, rect)
                if self.array[row, column] == PICTURES["right"]:
                    self.images['right'].render(painter, rect)
                if self.array[row, column] == PICTURES["left"]:
                    self.images['left'].render(painter, rect)
                if self.array[row, column] == PICTURES["heater"]:
                    self.images['heater'].render(painter, rect)
                if self.array[row, column] == PICTURES["cooler"]:
                    self.images['cooler'].render(painter, rect)

    def mousePressEvent(self, event):
        # Convert to matrix from click
        row, column = pixels_to_logical(event.x(), event.y())

        # Update data in matrix
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected is None:
                    return
                self.array[row, column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row, column] = PICTURES['grass']
            else:
                return
            # rerender the widget
            self.update(*logical_to_pixels(row, column), CELL_SIZE, CELL_SIZE)

    def wheelEvent(self, event):
        if event.angleDelta().y() < 0:
            # TODO: zooming
            print("minus downsize cell size and render")
        else:
            print("plus cellsize and render")



class myWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.grid = None
        self.bee_clust = None

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            # TODO: need do tik a render map
            print("Need do tick")


class App:

    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.window = myWindow()
        self.window.setWindowIcon(QtGui.QIcon(App.get_img_path("bee.svg")))

        with open(App.get_gui_path('mainwindow.ui')) as f:
            uic.loadUi(f, self.window)

        self.images = {}
        for i in PICTURES:
            self.images[i] = App.create_as_qt_svg(i + ".svg")

        # get palette from ui
        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        for i in PICTURES:
            self.add_item_to_palette(i, App.get_img_path(i+".svg"))

        # TODO: beeclust map here init
        self.array = numpy.zeros((15, 20), dtype=numpy.int8)
        self.array[:, 5] = 1

        # get range from ui from qt
        self.scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea')

        # create and add grid
        self.grid = GridWidget(self.array, self.images)
        self.window.grid = self.grid
        self.scroll_area.setWidget(self.grid)

        self.palette.itemSelectionChanged.connect(lambda: self.item_activated())

        self.action_bind('actionNew', lambda: self.new_dialog())
        self.action_bind('actionOpen', lambda: self.open_dialog())
        self.action_bind('actionSave', lambda: self.save_dialog())
        self.action_bind('actionAbout', lambda: self.about())
        self.action_bind('actionTick', lambda: self.tick())
        self.action_bind('actionHeat', lambda: self.heatMap())
        self.action_bind('actionParameters', lambda: self.change_dialog())

    def action_bind(self, name, func):
        action = self.window.findChild(QtWidgets.QAction, name)
        action.triggered.connect(func)

    @staticmethod
    def create_as_qt_svg(file_name):
        return QtSvg.QSvgRenderer(App.get_img_path(file_name))

    @staticmethod
    def get_gui_path(file_name):
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'gui', file_name))

    @staticmethod
    def get_img_path(file_name):
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'img', file_name))

    def add_item_to_palette(self, name, img_path):
        # Create item with icon in palette in app
        item = QtWidgets.QListWidgetItem(name)
        icon = QtGui.QIcon(img_path)
        item.setIcon(icon)
        self.palette.addItem(item)
        item.setData(VALUE_ROLE, PICTURES[name])

    def item_activated(self):
        # call when item click
        for item in self.palette.selectedItems():
            self.grid.selected = item.data(VALUE_ROLE)

    def change_dialog(self):
        QtWidgets.QMessageBox.critical(self.window, "vole", "nevim")
        print("change")

    def open_dialog(self):
        print("open")

    def save_dialog(self):
        print("close")

    def tick(self):
        print("tick")

    def about(self):
        QtWidgets.QMessageBox.about(self.window, "BeeClust", ABOUT)

    def heatMap(self):
        print("heatMap")

    def new_dialog(self):
        # create new dialog
        dialog = QtWidgets.QDialog(self.window)

        # load ui
        with open(App.get_gui_path('newmaze.ui')) as f:
            uic.loadUi(f, dialog)

        # show modal dialog
        result = dialog.exec()

        # result from dialog, check what button
        if result == QtWidgets.QDialog.Rejected:
            return

        # load from spin box
        cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
        rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()

        # TODO: beeclust new map
        self.grid.array = numpy.zeros((rows, cols), dtype=numpy.int8)

        # Mapa může být jinak velká, tak musíme změnit velikost Gridu;
        # (tento kód používáme i jinde, měli bychom si na to udělat funkci!)
        # TODO: beeclust new map
        # TODO: recalculate heat
        size = logical_to_pixels(rows, cols)
        self.grid.setMinimumSize(*size)
        self.grid.setMaximumSize(*size)
        self.grid.resize(*size)

        # update grid
        self.grid.update()

    def run(self):
        self.window.show()
        return self.app.exec()


def main():
    app = App()
    app.run()
