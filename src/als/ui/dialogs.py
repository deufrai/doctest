"""
Provides all dialogs used in ALS GUI
"""
import logging

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from als import config, datastore
from als.code_utilities import log
from generated.about_ui import Ui_AboutDialog
from generated.prefs_ui import Ui_PrefsDialog

_LOGGER = logging.getLogger(__name__)


class PreferencesDialog(QDialog):
    """
    Our main preferences dialog box
    """

    @log
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_PrefsDialog()
        self._ui.setupUi(self)

        self._ui.ln_scan_folder_path.setText(config.get_scan_folder_path())
        self._ui.ln_work_folder_path.setText(config.get_work_folder_path())
        self._ui.ln_web_server_port.setText(str(config.get_www_server_port_number()))
        self._ui.chk_debug_logs.setChecked(config.is_debug_log_on())

    # FIXME : using @log on this causes
    # TypeError: accept() takes 1 positional argument but 2 were given
    def accept(self):
        """checks and stores user settings"""
        config.set_scan_folder_path(self._ui.ln_scan_folder_path.text())
        config.set_work_folder_path(self._ui.ln_work_folder_path.text())

        web_server_port_number_str = self._ui.ln_web_server_port.text()

        if web_server_port_number_str.isdigit() and 1024 <= int(web_server_port_number_str) <= 65535:
            config.set_www_server_port_number(web_server_port_number_str)
        else:
            message = "Web server port number must be a number between 1024 and 65535"
            error_box("Wrong value", message)
            _LOGGER.error(f"Port number validation failed : {message}")
            self._ui.ln_web_server_port.setFocus()
            self._ui.ln_web_server_port.selectAll()
            return

        config.set_debug_log(self._ui.chk_debug_logs.isChecked())
        config.save()

        super().accept()

    @pyqtSlot(name="on_btn_browse_scan_clicked")
    @log
    def browse_scan(self):
        """Opens a folder dialog to choose scan folder"""
        scan_folder_path = QFileDialog.getExistingDirectory(self,
                                                            _("Select scan folder"),
                                                            self._ui.ln_scan_folder_path.text())
        if scan_folder_path:
            self._ui.ln_scan_folder_path.setText(scan_folder_path)

    @pyqtSlot(name="on_btn_browse_work_clicked")
    @log
    def browse_work(self):
        """Opens a folder dialog to choose work folder"""
        work_folder_path = QFileDialog.getExistingDirectory(self,
                                                            _("Select work folder"),
                                                            self._ui.ln_work_folder_path.text())
        if work_folder_path:
            self._ui.ln_work_folder_path.setText(work_folder_path)


class AboutDialog(QDialog):
    """
    Our about dialog box
    """

    @log
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)
        self._ui.lblVersionValue.setText(datastore.VERSION)


def question(title, message):
    """
    Asks a question to user in a Qt MessageBox and return True/False as Yes/No

    :param title: Title of the box
    :param message: Message displayed in the box
    :return: True if user replies "Yes", False otherwise
    """
    return QMessageBox.Yes == QMessageBox.question(None, title, message, QMessageBox.Yes | QMessageBox.No)


def warning_box(title, message):
    """
    Displays a waring Qt MessageBox

    :param title: Title of the box
    :param message: Message displayed in the box
    :return: None
    """
    message_box('Warning : ' + title, message, QMessageBox.Warning)


def error_box(title, message):
    """
    Displays an error Qt MessageBox

    :param title: Title of the box
    :param message: Message displayed in the box
    :return: None
    """
    message_box('Error : ' + title, message, QMessageBox.Critical)


def message_box(title, message, icon=QMessageBox.Information):
    """
    Displays a Qt MessageBox with custom icon : Info by default

    :param title: Title of the box
    :param message: Message displayed in the box
    :param icon: The icon to show
    :return: None
    """
    box = QMessageBox()
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(message)
    box.exec()
