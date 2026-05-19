from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QScrollArea, QVBoxLayout, QWidget


class ImagePreviewDialog(QDialog):
    def __init__(self, image: Image.Image, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Предпросмотр изображения")
        self.resize(900, 700)

        image_qt = ImageQt(image)
        pixmap = QPixmap.fromImage(image_qt)

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(False)

        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(False)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
