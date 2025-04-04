from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QDialogButtonBox,
                               QFormLayout, QLineEdit)

class SettingsDialog(QDialog):
    GEMINI = "Gemini"

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize) # disable resizing
        self.setLayout(self.layout)

        self.createChatbotSettings()
        self.createDialogButtons()

    def createChatbotSettings(self):
        self.combo_box = QComboBox()
        self.layout.addWidget(self.combo_box)

        self.combo_box.currentIndexChanged.connect(self.onChatbotChanged)
        self.combo_box.addItems([SettingsDialog.GEMINI])

    def createDialogButtons(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_box)
        self.layout.addLayout(button_layout)

    def onChatbotChanged(self, index):
        # display settings that correspond to selected chatbot
        # TODO: remove other chatbot fields when choose another chatbot
        if self.combo_box.currentText() == SettingsDialog.GEMINI:
            box_layout = QFormLayout()

            api_key_line_edit = QLineEdit()

            box_layout.addRow(QLabel("API key"), api_key_line_edit)
            #box_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
            self.layout.addLayout(box_layout)
