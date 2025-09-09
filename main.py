from datetime import date
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QMessageBox, QSplitter
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.db.sqlite import initialize_database, get_entry, upsert_entry
from app.renderer.markdown import render_markdown_with_signifiers


class JournalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Journal App")
        self.resize(1200, 800)

        self.editor = QPlainTextEdit(self)
        self.editor.setTabStopDistance(32)
        self.preview = QWebEngineView(self)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([700, 500])
        self.setCentralWidget(splitter)

        self._debounce = QTimer(self)
        self._debounce.setInterval(250)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self.update_preview)
        self.editor.textChanged.connect(self._debounce.start)

        self._setup_menu()
        self._current_date = date.today().isoformat()
        self.load_today()

    def _setup_menu(self):
        save_action = QAction("Guardar (Ctrl+S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current)
        self.addAction(save_action)

        export_action = QAction("Exportar HTML…", self)
        export_action.triggered.connect(self.export_html)
        self.addAction(export_action)

        menu = self.menuBar().addMenu("Ficheiro")
        menu.addAction(save_action)
        menu.addAction(export_action)

    def load_today(self):
        content = get_entry(self._current_date)
        if not content:
            heading = f"# {self._current_date}\n\n"
            content = heading
        self.editor.setPlainText(content)
        self.update_preview()

    def update_preview(self):
        text = self.editor.toPlainText()
        html = render_markdown_with_signifiers(text)
        self.preview.setHtml(html)

    def save_current(self):
        upsert_entry(self.editor.toPlainText(), self._current_date)

    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar HTML", f"journal_{self._current_date}.html", "HTML Files (*.html)")
        if not path:
            return
        html = render_markdown_with_signifiers(self.editor.toPlainText())
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao exportar", str(exc))

    def closeEvent(self, event):
        try:
            self.save_current()
        finally:
            event.accept()


def main():
    initialize_database()
    app = QApplication(sys.argv)
    win = JournalWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


