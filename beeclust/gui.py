from PyQt5 import QtWidgets


def main():
	

	app = QtWidgets.QApplication([])

	button = QtWidgets.QPushButton("Click to Exit")
	button.setWindowTitle("Goodbye World")
	button.clicked.connect(app.quit)

	button.show()

	app.exec()