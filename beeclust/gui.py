from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg, uic
from beeclust.beeclustClass import MapConst, BeeClust
from beeclust.About import ABOUT
import numpy
import os
import sys

PICTURES = {'grass': 0, 'wall': 5, 'heater': 6, 'cooler': 7, 'bee': -1, 'up': 1, 'down': 3, 'right': 2, 'left': 4}


class GridWidget(QtWidgets.QWidget):

    def __init__(self, bee_clust, images):
        super().__init__()
        self.CELL_SIZE = 40
        self.MIN_SIZE = 20
        self.MAX_SIZE = 100
        self.STEP = 3
        self.VALUE_ROLE = QtCore.Qt.UserRole

        self.images = images
        self.bee_clust = bee_clust
        self.recalculate_sizes(*self.bee_clust.map.shape)
        self.selected = None

    def pixels_to_logical(self, x, y):
        return y // self.CELL_SIZE, x // self.CELL_SIZE

    def logical_to_pixels(self, row, column):
        return column * self.CELL_SIZE, row * self.CELL_SIZE

    def tick(self):
        self.bee_clust.tick()
        self.update()

    def recalculate_sizes(self, rows, cols):
        size = self.logical_to_pixels(rows, cols)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def paintEvent(self, event):
        rect = event.rect()

        # zjistíme, jakou oblast naší matice to představuje
        # nesmíme se přitom dostat z matice ven
        row_min, col_min = self.pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = self.pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.bee_clust.map.shape[0])
        col_max = min(col_max + 1, self.bee_clust.map.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = self.logical_to_pixels(row, column)

                rect = QtCore.QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)

                # podkladová barva pod poloprůhledné obrázky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # grass add everywhere
                self.images['grass'].render(painter, rect)

                # Place right images on possitions
                if self.bee_clust.map[row, column] == PICTURES["wall"]:
                    self.images['wall'].render(painter, rect)
                elif self.bee_clust.map[row, column] <= PICTURES["bee"]:
                    self.images['bee'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["up"]:
                    self.images['up'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["down"]:
                    self.images['down'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["right"]:
                    self.images['right'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["left"]:
                    self.images['left'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["heater"]:
                    self.images['heater'].render(painter, rect)
                elif self.bee_clust.map[row, column] == PICTURES["cooler"]:
                    self.images['cooler'].render(painter, rect)

    def mousePressEvent(self, event):
        # Convert to matrix from click
        row, column = self.pixels_to_logical(event.x(), event.y())

        # Update data in matrix
        if 0 <= row < self.bee_clust.map.shape[0] and 0 <= column < self.bee_clust.map.shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected is None:
                    return
                self.bee_clust.map[row, column] = self.selected
                self.bee_clust.recalculate_heat()
            elif event.button() == QtCore.Qt.RightButton:
                self.bee_clust.map[row, column] = PICTURES['grass']
                self.bee_clust.recalculate_heat()
            else:
                return
            # rerender the widget
            self.update(*self.logical_to_pixels(row, column), self.CELL_SIZE, self.CELL_SIZE)

    def wheelEvent(self, event):
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if event.angleDelta().y() < 0:
                if not self.CELL_SIZE < self.MIN_SIZE:
                    self.CELL_SIZE -= self.STEP
                    self.recalculate_sizes(*self.bee_clust.map.shape)
                    self.update()
            else:
                if not self.CELL_SIZE > self.MAX_SIZE:
                    self.CELL_SIZE += self.STEP
                    self.recalculate_sizes(*self.bee_clust.map.shape)
                    self.update()


class myWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.grid = None
        self.bee_clust = None

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.grid.tick()


class App:

    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.bee_clust = BeeClust(numpy.zeros((10, 10), dtype=numpy.int8))

        self.window = myWindow()
        self.window.setWindowIcon(QtGui.QIcon(App.get_img_path("bee.svg")))

        with open(App.get_gui_path('mainwindow.ui')) as f:
            uic.loadUi(f, self.window)

        self.images = {}
        for i in PICTURES:
            self.images[i] = App.create_as_qt_svg(i + ".svg")

        # get range from ui from qt
        self.scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea')

        # create and add grid
        self.grid = GridWidget(self.bee_clust, self.images)
        self.window.grid = self.grid
        self.scroll_area.setWidget(self.grid)

        # get palette from ui
        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        for i in PICTURES:
            self.add_item_to_palette(i, App.get_img_path(i + ".svg"))

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
        item.setData(self.grid.VALUE_ROLE, PICTURES[name])

    def item_activated(self):
        # call when item click
        for item in self.palette.selectedItems():
            self.grid.selected = item.data(self.grid.VALUE_ROLE)

    def change_dialog(self):

        print("change")

    def open_dialog(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self.window)
        try:
            file = open(file[0], 'r')
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.window, "Open error", e.strerror)
        else:
            with file:
                try:
                    array = numpy.loadtxt(file, dtype=numpy.int8)
                    if array.max() > 7:
                        raise TypeError()
                    self.bee_clust.map = array
                    self.bee_clust.recalculate_heat()
                    self.grid.update()
                except TypeError as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self.window, "Type error", "Bad type, need save numpy 2D array.")

    def save_dialog(self):
        file = QtWidgets.QFileDialog.getSaveFileName(self.window)
        try:
            file = open(file[0], 'w')
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.window, "Save error", e.strerror)
        else:
            with file:
                numpy.savetxt(file, self.bee_clust.map.astype(numpy.int8))



    def tick(self):
        self.grid.tick()

    def about(self):
        # Show about dialog
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

        self.grid.bee_clust.map = numpy.zeros((rows, cols), dtype=numpy.int8)
        self.bee_clust.recalculate_heat()
        self.grid.recalculate_sizes(rows, cols)
        self.grid.update()

    def run(self):
        self.window.show()
        return self.app.exec()


def main():
    app = App()
    app.run()
