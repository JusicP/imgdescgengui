from PySide6.QtWidgets import QWidget, QGroupBox, QFormLayout, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from imgdescgenlib.image import Image

class ImageDetailsWidget(QWidget):
    MAX_THUMBNAIL_WIDTH = 300
    MAX_THUMBNAIL_HEIGHT = 300

    def __init__(self):
        super().__init__()

        self.setMaximumWidth(512)

        self._image_desc_box = QGroupBox("Image details")

        self._image_filename_label = QLabel()
        self._image_fullpath_label = QLabel()
        self._image_widget = QLabel()
        self._image_widget.setMaximumSize(
            ImageDetailsWidget.MAX_THUMBNAIL_WIDTH,
            ImageDetailsWidget.MAX_THUMBNAIL_HEIGHT
        )
        self._image_exif_description = QLabel("(null)")
        self._image_exif_description.setWordWrap(True)

        box_layout = QFormLayout()
        box_layout.addRow(QLabel("Filename: "), self._image_filename_label)
        box_layout.addRow(QLabel("Path: "), self._image_fullpath_label)
        box_layout.addRow(QLabel("Thumbnail: "), self._image_widget)
        box_layout.addRow(QLabel("EXIF:ImageDescription: "), self._image_exif_description)
        box_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self._image_desc_box.setLayout(box_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._image_desc_box)
        self.setLayout(main_layout)

    def setImage(self, image_filename: str, image_fullpath: str):
        self._image_filename_label.setText(image_filename)
        self._image_fullpath_label.setText(image_fullpath)

        pixmap = QPixmap(image_fullpath)

        # scale pixmap to fit bounds with keeping aspect ratio
        scaled_pixmap = pixmap.scaled(
            ImageDetailsWidget.MAX_THUMBNAIL_WIDTH,
            ImageDetailsWidget.MAX_THUMBNAIL_HEIGHT,
            Qt.KeepAspectRatio
        )
        self._image_widget.setPixmap(scaled_pixmap)

        image = Image(image_fullpath)
        metadata = image.read_metadata()

        if "EXIF:ImageDescription" in metadata[0]:
            self._image_exif_description.setText(metadata[0]["EXIF:ImageDescription"])

