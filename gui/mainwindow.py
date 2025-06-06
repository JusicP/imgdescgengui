import os
from PySide6.QtCore import QFileInfo, QDir, Qt
from PySide6.QtGui import QIcon, QKeySequence, QAction
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, 
                               QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QWidget,
                               QPushButton, QGroupBox, QLabel, QLineEdit, QMenu, QFormLayout)

from gui.imagedetails import ImageDetailsWidget
from gui.schemas.config import ImgDescGenConfig
from gui.settingsdialog import SettingsDialog
from gui.generationwindow import GenerationWindow

class MainWindow(QMainWindow):
    CONFIG_FILENAME = "config.json"

    def __init__(self):
        super(MainWindow, self).__init__()

        self._image_details_widget = None
        self._generation_window = None

        self.setWindowIcon(QIcon("gui/icon_1024.png"))

        self.window = QWidget()
        self.setCentralWidget(self.window)

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.vLayout.addLayout(self.hLayout)
        self.window.setLayout(self.vLayout)

        self.setFixedSize(1000, 500)
        self.statusBar().setSizeGripEnabled(False)
        self.setWindowTitle("Image description generator")

        self._config = ImgDescGenConfig(MainWindow.CONFIG_FILENAME)

        self.createFooterButtons()
        self.createImageLists()
        self.createActions()
        self.createMenus()
        self.createStatusBar()

        self.restoreSelectedImages()
    
    def saveConfig(self):
        if self._config.saveConfig(MainWindow.CONFIG_FILENAME) == False:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save configuration"))

    def createImageItem(self, filename: str, fullpath: str, flag: Qt.ItemFlag):
        item = QListWidgetItem(filename if filename else fullpath)
        item.setFlags(flag)
        if filename:
            item.setData(Qt.ItemDataRole.UserRole, fullpath)
        return item

    def fillImageList(self, dir):
        self.image_list_widget.clear()

        directory = QDir(dir)
        images = directory.entryList(["*.jpg", "*.JPG"], QDir.Files)
        for image_filename in images:
            image_fullpath = directory.absoluteFilePath(image_filename)

            item = self.createImageItem(
                image_filename, 
                image_fullpath,
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            item.setCheckState(Qt.CheckState.Checked if self.getSelectedImage(image_fullpath) else Qt.CheckState.Unchecked)

            self.image_list_widget.addItem(item)

        self.image_count_label.setText(str(self.image_list_widget.count()))

    def selectImageDirectory(self):
        dir = QFileDialog.getExistingDirectory(self)
        if not dir:
            return

        self._input_path_line_edit.setText(dir)

        self._config.getSchema().input_dir = dir
        self.saveConfig()

        self.fillImageList(dir)

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

    def getSelectedImage(self, image_fullpath: str) -> QListWidgetItem | None:
        for i in range(self.selected_image_list_widget.count()):
            item = self.selected_image_list_widget.item(i)
            if image_fullpath == item.text():
                return item
            
    def saveSelectedImages(self):
        selected_images = []
        for i in range(self.selected_image_list_widget.count()):
            item = self.selected_image_list_widget.item(i)
            selected_images.append(item.text())

        self._config.getSchema().selected_images = selected_images
        self.saveConfig()

    def imageChanged(self, item: QListWidgetItem):
        if item.checkState() == Qt.CheckState.Checked:
            if self.canSelectImage() == False:
                item.setCheckState(Qt.CheckState.Unchecked)
                return

            image_fullpath = item.data(Qt.ItemDataRole.UserRole)
            self.addSelectedImage(image_fullpath)
        elif item.checkState() == Qt.CheckState.Unchecked:
            image_item = self.getSelectedImage(item.data(Qt.ItemDataRole.UserRole))
            if image_item:
                self.removeSelectedItem(image_item)

        self.saveSelectedImages()

    def addSelectedImage(self, image_fullpath: str):
        if self.getSelectedImage(image_fullpath) == None:
            item = self.createImageItem(
                None,
                image_fullpath,
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.selected_image_list_widget.addItem(item)
            self.selected_image_count_label.setText(str(self.selected_image_list_widget.count()))

    def restoreSelectedImages(self):
        # restore selected images from the config
        if self._config.getSchema().selected_images == None:
            return
        
        for image_fullpath in self._config.getSchema().selected_images:
            # find the item in the image list widget and set it to checked
            # it should add also to the selected image list widget (imageChanged() will do that)
            for i in range(self.image_list_widget.count()):
                item = self.image_list_widget.item(i)
                if image_fullpath == item.data(Qt.ItemDataRole.UserRole):
                    item.setCheckState(Qt.CheckState.Checked)
                    break

            # if selected image not found in image list, add it to the selected image list manually
            self.addSelectedImage(image_fullpath)

    def generateImageDesc(self):
        image_list = []
        for i in range(self.selected_image_list_widget.count()):
            item = self.selected_image_list_widget.item(i)
            image_list.append(item.text())

        if not self._generation_window:
            self._generation_window = GenerationWindow(self._config)
        self._generation_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._generation_window.show()
        self._generation_window.run(image_list)

    def onOutputPathChanged(self):
        # enable generate button if output path is not empty
        self.generate_img_desc_button.setEnabled(len(self._output_path_line_edit.text()) > 0)
        self._config.getSchema().output_dir = self._output_path_line_edit.text()
        self.saveConfig()

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
        dlg = SettingsDialog(self._config)
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

    def canSelectImage(self) -> bool:
        max_image_count = self._config.getSchema().chatbots[self._config.getSchema().chatbot].max_image_count
        if self.selected_image_list_widget.count() >= max_image_count:
            QMessageBox.warning(self, "Warning", f"You can select only {max_image_count} images")
            return False
        
        return True

    def removeSelectedItem(self, item):
        row = self.selected_image_list_widget.row(item)
        self.selected_image_list_widget.takeItem(row)
        self.selected_image_count_label.setText(str(self.selected_image_list_widget.count()))

        # uncheck the item in the image list widget, if exists
        for i in range(self.image_list_widget.count()):
            image_item = self.image_list_widget.item(i)
            if image_item.data(Qt.ItemDataRole.UserRole) == item.text():
                image_item.setCheckState(Qt.CheckState.Unchecked)
                break

        self.saveSelectedImages()

    def selectedImageListKeyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            item = self.selected_image_list_widget.currentItem()
            if item:
                self.removeSelectedItem(item)

    def createFooterButtons(self):
        layout = QHBoxLayout()
        self.vLayout.addLayout(layout)

        output_path_label = QLabel("Output path")
        layout.addWidget(output_path_label)

        self.generate_img_desc_button = QPushButton()
        self.generate_img_desc_button.clicked.connect(self.generateImageDesc)
        self.generate_img_desc_button.setMaximumWidth(196)
        self.generate_img_desc_button.setText("Generate image description")

        self._output_path_line_edit = QLineEdit()
        self._output_path_line_edit.textChanged.connect(self.onOutputPathChanged)
        self._output_path_line_edit.setText(self._config.getSchema().output_dir)
        self._output_path_line_edit.setReadOnly(True)
        layout.addWidget(self._output_path_line_edit)

        #self.onOutputPathChanged()

        browse_output_directory = QPushButton()
        browse_output_directory.clicked.connect(self.browseOutputDirectory)
        browse_output_directory.setMaximumWidth(196)
        browse_output_directory.setText("Browse")
        layout.addWidget(browse_output_directory)

        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vLayout.addLayout(footer_layout)
        footer_layout.addWidget(self.generate_img_desc_button)

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

        # create input directory field
        input_directory_layout = QHBoxLayout()
        layout.addLayout(input_directory_layout)

        input_path_label = QLabel("Input path")
        input_directory_layout.addWidget(input_path_label)

        self._input_path_line_edit = QLineEdit()
        input_dir = self._config.getSchema().input_dir
        self._input_path_line_edit.setText(input_dir)
        self._input_path_line_edit.setReadOnly(True)
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
        image_count_layout = QFormLayout()
        self.image_count_label = QLabel("0")
        image_count_layout.addRow(QLabel("Images: "), self.image_count_label)
        layout.addLayout(image_count_layout)

        self.image_list_widget.itemChanged.connect(self.imageChanged)
        self.hLayout.addWidget(image_list_box)

        # create selected image list
        selected_image_list_box = QGroupBox("Selected images")

        selected_images_label = QLabel("Press on checkbox to select image to process. Press Delete key (or open context menu and press Remove button) to remove image from the list.")
        selected_images_label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(selected_images_label)

        self.selected_image_list_widget = QListWidget()
        self.selected_image_list_widget.itemClicked.connect(self.imageClicked)
        self.selected_image_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.selected_image_list_widget.customContextMenuRequested.connect(self.openSelectedImageContextMenu)
        self.selected_image_list_widget.keyPressEvent = self.selectedImageListKeyPressEvent
        layout.addWidget(self.selected_image_list_widget)
        image_count_layout = QFormLayout()
        self.selected_image_count_label = QLabel("0")
        image_count_layout.addRow(QLabel("Images: "), self.selected_image_count_label)
        layout.addLayout(image_count_layout)

        selected_image_list_box.setLayout(layout)

        self.hLayout.addWidget(selected_image_list_box)

        # load images from input dir
        if input_dir:
            self.fillImageList(input_dir)

    def createActions(self):
        root = QFileInfo(__file__).absolutePath()

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
        self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
