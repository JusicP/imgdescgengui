import os
from PySide6.QtCore import QFileInfo, QDir, Qt
from PySide6.QtGui import QIcon, QKeySequence, QAction
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, 
                               QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QWidget,
                               QPushButton, QGroupBox, QLabel, QLineEdit, QMenu)

from gui.imagedetails import ImageDetailsWidget
from gui.settingsdialog import SettingsDialog

from imgdescgenlib.chatbot.gemini import GeminiClient
from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.exceptions import ImgDescGenBaseException

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._image_details_widget = None
        self._img_desc_gen = None

        self.window = QWidget()
        self.setCentralWidget(self.window)

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.vLayout.addLayout(self.hLayout)
        self.window.setLayout(self.vLayout)

        self.setFixedSize(1000, 500)
        self.statusBar().setSizeGripEnabled(False)
        self.setWindowTitle("Image description generator")

        self.createFooterButtons()
        self.createImageLists()
        self.createActions()
        self.createMenus()
        self.createStatusBar()

    def selectImageDirectory(self):
        dir = QFileDialog.getExistingDirectory(self)
        if not dir:
            return

        self._input_path_line_edit.setText(dir)

        # refill listwidget with new images
        self.image_list_widget.clear()

        directory = QDir(dir)
        images = directory.entryList(["*.jpg", "*.JPG"], QDir.Files)
        for image_filename in images:
            image_fullpath = directory.absoluteFilePath(image_filename)

            item = QListWidgetItem(image_filename)
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, image_fullpath)
            self.image_list_widget.addItem(item)

            item.setCheckState(Qt.CheckState.Checked if self.getSelectedImage(image_fullpath) else Qt.CheckState.Unchecked)

    def setImagesCheckState(self, state: Qt.CheckState):
        for i in range(self.image_list_widget.count()):
            item = self.image_list_widget.item(i)
            item.setCheckState(state)

    def imageClicked(self, item: QListWidgetItem):        
        if item.isSelected():
            image_filename = item.text()
            image_fullpath = item.data(Qt.ItemDataRole.UserRole)
            if image_fullpath == None:
                image_fullpath = item.text()
                image_filename = os.path.basename(image_fullpath)

            self.createImageDetails(image_filename, image_fullpath)

    def getSelectedImage(self, image_fullpath: str):
        for i in range(self.selected_image_list_widget.count()):
            item = self.selected_image_list_widget.item(i)
            if image_fullpath == item.text():
                return item, i

    def imageChanged(self, item: QListWidgetItem):
        if item.checkState() == Qt.CheckState.Checked:
            image_fullpath = item.data(Qt.ItemDataRole.UserRole)
            if self.getSelectedImage(image_fullpath) == None:
                item = QListWidgetItem(image_fullpath)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.selected_image_list_widget.addItem(item)
        elif item.checkState() == Qt.CheckState.Unchecked:
            image_row = self.getSelectedImage(item.data(Qt.ItemDataRole.UserRole))
            if image_row:
                self.selected_image_list_widget.takeItem(image_row[1])
                # TODO: clean image details if this item was selected

    def generateImageDesc(self):
        image_list = []
        for i in range(self.selected_image_list_widget.count()):
            item = self.selected_image_list_widget.item(i)
            image_list.append(item.data(Qt.ItemDataRole.UserRole))

        client = GeminiClient("123")
        self._img_desc_gen = ImgDescGen(client)

        try:
            self._img_desc_gen.generate_image_description(image_list, self._output_path_line_edit.text())
        except ImgDescGenBaseException:
            QMessageBox(title="Error", text="Fucked up")

    def onOutputPathChanged(self):
        # enable generate button if output path is not empty
        self.generate_img_desc_button.setEnabled(len(self._output_path_line_edit.text()) > 0)

    def browseOutputDirectory(self):
        dir = QFileDialog.getExistingDirectory(self)
        if not dir:
            return
        
        self._output_path_line_edit.setText(dir)

    def about(self):
        QMessageBox.about(self, "About Application",
                "The <b>Image description generator application</b> designed to easy use of the <b><a href=\"https://github.com/JusicP/imgdescgen\">imgdescgen</a></b> library "
                "with using Qt GUI library.")

    def openSettingsDialog(self):
        dlg = SettingsDialog()
        dlg.exec()

    def openSelectedImageContextMenu(self, position):
        item = self.selected_image_list_widget.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        remove_action = QAction("Remove from list", self)
        remove_action.triggered.connect(lambda: self.removeSelectedItem(item))
        menu.addAction(remove_action)

        menu.exec(self.selected_image_list_widget.viewport().mapToGlobal(position))

    def removeSelectedItem(self, item):
        row = self.selected_image_list_widget.row(item)
        self.selected_image_list_widget.takeItem(row)

        # uncheck the item in the image list widget
        for i in range(self.image_list_widget.count()):
            image_item = self.image_list_widget.item(i)
            if image_item.data(Qt.ItemDataRole.UserRole) == item.text():
                image_item.setCheckState(Qt.CheckState.Unchecked)
                break

    def createFooterButtons(self):
        self.generate_img_desc_button = QPushButton()
        self.generate_img_desc_button.clicked.connect(self.generateImageDesc)
        self.generate_img_desc_button.setMaximumWidth(196)
        self.generate_img_desc_button.setText("Generate image description")

        layout = QHBoxLayout()
        self.vLayout.addLayout(layout)

        output_path_label = QLabel("Output path")
        layout.addWidget(output_path_label)

        self._output_path_line_edit = QLineEdit()
        self._output_path_line_edit.textChanged.connect(self.onOutputPathChanged)
        layout.addWidget(self._output_path_line_edit)

        self.onOutputPathChanged()
        self.vLayout.addWidget(self.generate_img_desc_button)
        # TODO: fill output path with value saved in config

        browse_output_directory = QPushButton()
        browse_output_directory.clicked.connect(self.browseOutputDirectory)
        browse_output_directory.setMaximumWidth(196)
        browse_output_directory.setText("Browse")
        layout.addWidget(browse_output_directory)

    def createImageDetails(self, image_filename: str, image_fullpath: str):
        if self._image_details_widget == None:
            self._image_details_widget = ImageDetailsWidget()
            self.hLayout.addWidget(self._image_details_widget)

        # don't set the same image
        if image_fullpath != self._image_details_widget.getImageFullpath():
            self._image_details_widget.setImage(image_filename, image_fullpath)

    def createImageLists(self):
        image_list_box = QGroupBox("Image list from directory")

        layout = QVBoxLayout()
        image_list_box.setLayout(layout)

        layout.addWidget(QLabel("Go to File -> Select image directory to get a list of images"))

        # create input directory field
        input_directory_layout = QHBoxLayout()
        layout.addLayout(input_directory_layout)

        input_path_label = QLabel("Input path")
        input_directory_layout.addWidget(input_path_label)

        self._input_path_line_edit = QLineEdit()
        # TODO: don't allow to edit input path manually, do it from browse dialog
        #input_path_line_edit.textChanged.connect(self.onInputPathChanged)
        input_directory_layout.addWidget(self._input_path_line_edit)

        browse_input_directory = QPushButton()
        browse_input_directory.clicked.connect(self.selectImageDirectory)
        browse_input_directory.setMaximumWidth(196)
        browse_input_directory.setText("Browse")
        input_directory_layout.addWidget(browse_input_directory)

        # create image list
        self.image_list_widget = QListWidget()
        self.image_list_widget.itemClicked.connect(self.imageClicked)
        layout.addWidget(self.image_list_widget)

        self.image_list_widget.itemChanged.connect(self.imageChanged)
        self.hLayout.addWidget(image_list_box)

        # create selected image list
        image_list_box = QGroupBox("Selected images")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Press on checkbox to select image to process"))

        self.selected_image_list_widget = QListWidget()
        self.selected_image_list_widget.itemClicked.connect(self.imageClicked)
        self.selected_image_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.selected_image_list_widget.customContextMenuRequested.connect(self.openSelectedImageContextMenu)
        layout.addWidget(self.selected_image_list_widget)
        
        image_list_box.setLayout(layout)

        self.hLayout.addWidget(image_list_box)

    def createActions(self):
        root = QFileInfo(__file__).absolutePath()

        self.selectImageDirectoryAct = QAction(QIcon(root + '/images/open.png'), "&Select image directory...",
                self, shortcut=QKeySequence.Open,
                statusTip="Select image directory", triggered=self.selectImageDirectory)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.settingsAct = QAction("Settings", self,
                statusTip="Open settings dialog", triggered=self.openSettingsDialog)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.selectImageDirectoryAct)
        self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
