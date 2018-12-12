from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg, uic
import functools

import numpy
import sys, os
grass_img_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'img', 'grass.svg'))
wall_img_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'img', 'wall.svg'))
SVG_GRASS = QtSvg.QSvgRenderer(grass_img_path)
SVG_WALL = QtSvg.QSvgRenderer(wall_img_path)


CELL_SIZE = 32
VALUE_ROLE = QtCore.Qt.UserRole
DATA = {'Grass':0, 'Wall':1}

def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):

    def __init__(self, array):
        super().__init__()  # musíme zavolat konstruktor předka
        self.array = array
        # nastavíme velikost podle velikosti matice, jinak je náš widget příliš malý
        size = logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)
        self.selected = -1


    def paintEvent(self, event):
        rect = event.rect()  # získáme informace o překreslované oblasti

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

                # trávu dáme všude, protože i zdi stojí na trávě
                SVG_GRASS.render(painter, rect)

                # zdi dáme jen tam, kam patří
                if self.array[row, column] == DATA["Wall"]:
                    SVG_WALL.render(painter, rect)

    def mousePressEvent(self, event):

        if self.selected == -1:
            return
        # převedeme klik na souřadnice matice
        row, column = pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            self.array[row, column] = self.selected

            # tímto zajistíme překreslení widgetu v místě změny:
            # (pro Python 3.4 a nižší volejte jen self.update() bez argumentů)
            self.update(*logical_to_pixels(row, column), CELL_SIZE, CELL_SIZE)


def add_item_to_palette(palette, name, img_path):
    item = QtWidgets.QListWidgetItem(name)  # vytvoříme položku
    icon = QtGui.QIcon(img_path)  # ikonu
    item.setIcon(icon)  # přiřadíme ikonu položce
    palette.addItem(item)  # přidáme položku do palety
    item.setData(VALUE_ROLE, DATA[name])

def item_activated(palette, grid):
    """Tato funkce se zavolá, když uživatel zvolí položku"""

    # Položek může obecně být vybráno víc, ale v našem seznamu je to
    # zakázáno (v Designeru selectionMode=SingleSelection).
    # Projdeme "všechny vybrané položky", i když víme že bude max. jedna.
    for item in palette.selectedItems():
        grid.selected = item.data(VALUE_ROLE)


def main():
    
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()





    with open('mainwindow.ui') as f:
        uic.loadUi(f, window)



    window.show()



    # získáme paletu vytvořenou v Qt Designeru
    palette = window.findChild(QtWidgets.QListWidget, 'palette')

    add_item_to_palette(palette, "Grass", grass_img_path)
    add_item_to_palette(palette, "Wall", wall_img_path)

    
 



    # mapa zatím nadefinovaná rovnou v kódu
    array = numpy.zeros((15, 20), dtype=numpy.int8)
    array[:, 5] = 1  # nějaká zeď

    # získáme oblast s posuvníky z Qt Designeru
    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')

    # dáme do ní náš grid
    grid = GridWidget(array)
    scroll_area.setWidget(grid)


    palette.itemSelectionChanged.connect(lambda: item_activated(palette, grid))

    return app.exec()





	

