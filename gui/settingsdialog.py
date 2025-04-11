from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QDialogButtonBox,
                               QFormLayout, QLineEdit, QTextEdit, QGroupBox, QPushButton, QFileDialog,
                               QMessageBox)

from gui.schemas.config import ChatbotName, ImgDescGenConfig
from imgdescgenlib.chatbot.gemini.gemini import GeminiConfig, GeminiClient
from imgdescgenlib.chatbot.exceptions import ChatbotHttpRequestFailed

class SettingsDialog(QDialog):
    def __init__(self, config: ImgDescGenConfig, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")

        self._config = config

        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize) # disable resizing
        self.setLayout(self.layout)

        self.createGeneralSettings()
        self.createChatbotSettings()
        self.createDialogButtons()

    def accept(self):
        # collect values from the form and save them to the config
        config_schema = self._config.getSchema()
        config_schema.chatbot = self.chatbot_combobox.currentText()

        config_schema.chatbots[ChatbotName.GEMINI].api_key = self.api_key_line_edit.text()
        config_schema.chatbots[ChatbotName.GEMINI].image_description_prompt = self.prompt_text_edit.toPlainText()
        config_schema.chatbots[ChatbotName.GEMINI].model_name = self.gemini_model_combobox.itemData(self.gemini_model_combobox.currentIndex())

        config_schema.exiftool_path = self.exiftool_path_line_edit.text()

        self._config.saveConfig()
        super(SettingsDialog, self).accept()

    def reject(self):
        super(SettingsDialog, self).reject()

    def browseForExifToolPath(self):
        # Open a file dialog to select the ExifTool executable
        filepath, _ = QFileDialog.getOpenFileName(self, "Select ExifTool executable", "", "Executables (*.exe);;All Files (*)")
        if filepath:
            self.exiftool_path_line_edit.setText(filepath)

    def createGeneralSettings(self):
        general_settings_group = QGroupBox("General settings")

        general_layout = QFormLayout()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browseForExifToolPath)

        browse_layout = QHBoxLayout()
        self.exiftool_path_line_edit = QLineEdit(self._config.getSchema().exiftool_path)
        browse_layout.addWidget(self.exiftool_path_line_edit)
        browse_layout.addWidget(self.browse_button)

        general_layout.addRow(QLabel("ExifTool path"), browse_layout)

        general_settings_group.setLayout(general_layout)
        self.layout.addWidget(general_settings_group)

    def createChatbotSettings(self):
        chatbot_settings_group = QGroupBox("Chatbot settings")
        self.chatbot_form_layout = QFormLayout()

        self.chatbot_combobox = QComboBox()
        self.chatbot_form_layout.addRow(QLabel("Chatbot"), self.chatbot_combobox)
        self.chatbot_combobox.currentIndexChanged.connect(self.onChatbotChanged)
        self.chatbot_combobox.addItem(ChatbotName.GEMINI)
        self.chatbot_combobox.setCurrentText(self._config.getSchema().chatbot)

        chatbot_settings_group.setLayout(self.chatbot_form_layout)
        self.layout.addWidget(chatbot_settings_group)

    def createDialogButtons(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_box)
        self.layout.addLayout(button_layout)

    def refreshGeminiModels(self):
        gemini_config: GeminiConfig = self._config.getSchema().chatbots[ChatbotName.GEMINI].model_copy()
        gemini_config.api_key = self.api_key_line_edit.text()
        client = GeminiClient(gemini_config)

        try:
            response = client.get_available_models()
        except ChatbotHttpRequestFailed:
            QMessageBox.critical(self, "Error", "Failed to fetch models from Gemini API. Please check your API key and internet connection.")
            return
        
        current_model = self.gemini_model_combobox.currentText()

        self.gemini_model_combobox.clear()
        for model in response.models:
            self.gemini_model_combobox.addItem(model.name, model)

        # idk if needed
        self.gemini_model_combobox.setCurrentText(current_model)

    def onChatbotChanged(self, index):
        # display settings that correspond to selected chatbot
        # TODO: remove other chatbot fields when choose another chatbot
        if self.chatbot_combobox.currentText() == ChatbotName.GEMINI:
            gemini_config: GeminiConfig = self._config.getSchema().chatbots[ChatbotName.GEMINI]
        
            model_layout = QHBoxLayout()
            self.gemini_model_combobox = QComboBox()
            model_layout.addWidget(self.gemini_model_combobox)
            refresh_button = QPushButton("Refresh")
            refresh_button.clicked.connect(self.refreshGeminiModels)
            model_layout.addWidget(refresh_button)
            self.chatbot_form_layout.addRow(QLabel("Model"), model_layout)

            self.api_key_line_edit = QLineEdit()
            self.api_key_line_edit.textChanged.connect(
                lambda: self.gemini_model_combobox.setEnabled(self.api_key_line_edit.text() != "")
            )
            self.api_key_line_edit.setText(gemini_config.api_key)
            self.chatbot_form_layout.addRow(QLabel("API key"), self.api_key_line_edit)

            # fill models combobox if not already filled and if api key is set
            if gemini_config.api_key:
                self.refreshGeminiModels()

            self.gemini_model_combobox.setCurrentText(gemini_config.model_name.name)

            self.prompt_text_edit = QTextEdit(gemini_config.image_description_prompt)
            self.chatbot_form_layout.addRow(QLabel("Prompt"), self.prompt_text_edit)
