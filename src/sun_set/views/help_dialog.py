from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextBrowser,
    QVBoxLayout,
)


class HelpDialog(QDialog):
    def __init__(self, guide_path: Path, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Справка")
        self.resize(760, 600)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        self.load_guide(guide_path)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_browser)
        layout.addWidget(buttons)

    def load_guide(self, guide_path: Path) -> None:
        try:
            markdown = guide_path.read_text(encoding="utf-8")
        except OSError:
            self.text_browser.setPlainText(
                "Не удалось загрузить руководство пользователя."
            )
            return

        self.text_browser.setMarkdown(markdown)
