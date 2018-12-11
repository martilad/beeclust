from PyQt5 import QtWidgets, QtGui, QtCore, uic
import numpy


CELL_SIZE = 32


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

                # šedá pro zdi, zelená pro trávu
                if self.array[row, column] < 0:
                    color = QtGui.QColor(115, 115, 115)
                else:
                    color = QtGui.QColor(0, 255, 0)

                # vyplníme čtvereček barvou
                painter.fillRect(rect, QtGui.QBrush(color))



def main():
	
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()





    with open('mainwindow.ui') as f:
        uic.loadUi(f, window)







    window.show()




    # mapa zatím nadefinovaná rovnou v kódu
    array = numpy.zeros((15, 20), dtype=numpy.int8)
    array[:, 5] = -1  # nějaká zeď

    # získáme oblast s posuvníky z Qt Designeru
    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')

    # dáme do ní náš grid
    grid = GridWidget(array)
    scroll_area.setWidget(grid)


    return app.exec()





	

