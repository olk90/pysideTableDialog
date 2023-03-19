from PySide6.QtWidgets import QMessageBox


class ConfirmationDialog(QMessageBox):

    def __init__(self, parent, label_text):
        super().__init__(parent)

        self.setWindowTitle(" ")

        self.addButton(self.tr("Yes"), QMessageBox.AcceptRole)
        self.addButton(self.tr("No"), QMessageBox.RejectRole)
        self.setIcon(QMessageBox.Question)
        self.setText(label_text)


class ConfirmRestartDialog(ConfirmationDialog):

    def __init__(self, parent):
        label_text: str = self.tr("Changes applied require a restart. Restart now?")
        super(ConfirmRestartDialog, self).__init__(parent, label_text)


class ConfirmScheduleUpdateDialog(ConfirmationDialog):

    def __init__(self, parent):
        label_text: str = self.tr("Write changes to database?")
        super(ConfirmScheduleUpdateDialog, self).__init__(parent, label_text)


class ConfirmDeletionDialog(ConfirmationDialog):

    def __init__(self, parent):
        label_text: str = self.tr("Delete selected item?")
        super(ConfirmDeletionDialog, self).__init__(parent, label_text)
