import logging

from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QTextEdit, QApplication)

from gui.chatbotfactory import create_chatbot
from gui.schemas.config import ImgDescGenConfig
from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.exceptions import ImgDescGenBaseException
from imgdescgenlib.chatbot.gemini.gemini import GeminiConfig, GeminiClient
from imgdescgenlib.chatbot.exceptions import ChatbotFailed

class LoggingHandler(logging.Handler):
    """
    Custom logging handler to redirect log messages to a QTextEdit widget.
    Safe for threading.
    """
    # use inner class to avoid emit() method conflict
    class Emitter(QObject):
        record_signal = Signal(str, str)

    def __init__(self, prefix: str):
        super().__init__()
        self._prefix = prefix
        self.emitter = LoggingHandler.Emitter()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.record_signal.emit(self._prefix, msg)    

class GenerationWindow(QWidget):
    GUI_PREFIX = "GUI"
    LIB_PREFIX = "Library"
    CLIENT_PREFIX = "Client"

    class GenerationWorker(QObject):
        finished = Signal(str)

        def __init__(self, config, image_list: list[str]):
            super().__init__()

            self._config = config
            self._image_list = image_list

        def run(self):
            client = create_chatbot(self._config.getSchema().chatbot, self._config.getSchema().chatbots[self._config.getSchema().chatbot])

            finishMsg = None # in case of error, here will be exception message to print in GUI
            self._img_desc_gen = ImgDescGen(client)
            try:
                self._img_desc_gen.generate_image_description(
                    self._image_list,
                    self._config.getSchema().output_dir,
                    True,
                    self._config.getSchema().exiftool_path,
                )
            # idk but need to handle all exceptions to emit finished signal and quit thread
            except Exception as e:
                finishMsg = f"Exception: {repr(e)}"
            
            self.finished.emit(finishMsg)
            
    def __init__(self, config: ImgDescGenConfig, parent=None):
        super(GenerationWindow, self).__init__(parent)

        self._lib_log_handler = self.createLoggingHandler(self.LIB_PREFIX)
        self._client_log_handler = self.createLoggingHandler(self.CLIENT_PREFIX)
        logging.getLogger("imgdescgenlib").addHandler(self._lib_log_handler)
        logging.getLogger("imgdescgenlib").setLevel(logging.DEBUG)
        logging.getLogger("chatbotclient").addHandler(self._client_log_handler)
        logging.getLogger("chatbotclient").setLevel(logging.DEBUG)

        self._config = config

        self.setWindowTitle("Generation")

        layout = QVBoxLayout()

        self._gen_log_label = QLabel("Here you can see the generation logs. Don't close this window until generation is not stopped.")
        layout.addWidget(self._gen_log_label)

        self._log_text_edit = QTextEdit()
        self._log_text_edit.setReadOnly(True)
        layout.addWidget(self._log_text_edit)

        self.setLayout(layout)

    def closeEvent(self, event):
        # wait for thread to finish
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            
        event.accept()

    def log(self, prefix: str, message: str):
        self._log_text_edit.append(f"[{prefix}] {message}")

    def createLoggingHandler(self, prefix: str) -> LoggingHandler:
        handler = LoggingHandler(prefix)
        handler.emitter.record_signal.connect(self.log)
        return handler

    def finished(self, message: str = None):
        if message:
            self.log(self.GUI_PREFIX, message)

        self.log(self.GUI_PREFIX, f"Working thread finished. Now you can close this window.")
        self.thread = None
        QApplication.beep()

    def run(self, image_list: list[str]):
        self.worker = GenerationWindow.GenerationWorker(self._config, image_list)

        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.worker.finished.connect(self.finished)

        self.log(self.GUI_PREFIX, f"Working thread started")