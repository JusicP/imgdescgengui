from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")

        main_layout = QVBoxLayout()

        label = QLabel("Settings go here")
        main_layout.addWidget(label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_box)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)