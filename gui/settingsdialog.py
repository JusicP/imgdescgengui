from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QDialogButtonBox,
                               QFormLayout, QLineEdit, QTextEdit)

from gui.schemas.config import ChatbotName, ImgDescGenConfig
from imgdescgenlib.chatbot.gemini.gemini import GeminiConfig

class SettingsDialog(QDialog):
    GEMINI = "Gemini"

    def __init__(self, config: ImgDescGenConfig, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")

        self._config = config

        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize) # disable resizing
        self.setLayout(self.layout)

        self.createChatbotSettings()
        self.createDialogButtons()

    def accept(self):
        # collect values from the form and save them to the config
        self._config.getSchema().chatbots[ChatbotName.GEMINI].api_key = self.api_key_line_edit.text()
        self._config.getSchema().chatbots[ChatbotName.GEMINI].image_description_prompt = self.prompt_text_edit.toPlainText()

        self._config.saveConfig()
        super(SettingsDialog, self).accept()

    def reject(self):
        super(SettingsDialog, self).reject()

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

            gemini_config: GeminiConfig = self._config.getSchema().chatbots[ChatbotName.GEMINI]
        
            self.api_key_line_edit = QLineEdit(gemini_config.api_key)
            box_layout.addRow(QLabel("API key"), self.api_key_line_edit)

            self.prompt_text_edit = QTextEdit(gemini_config.image_description_prompt)
            box_layout.addRow(QLabel("Prompt"), self.prompt_text_edit)

            #box_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
            self.layout.addLayout(box_layout)
