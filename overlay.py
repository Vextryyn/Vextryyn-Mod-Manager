from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import QRect, Qt

class OverlayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap_original = None
        self.cursors_data = []
        self.setMinimumSize(310, 155)  # force preview window size
        self.setMaximumSize(310, 155)

    def set_image(self, pixmap, cursors_data=None):
        self.pixmap_original = pixmap
        if cursors_data:
            self.cursors_data = cursors_data
        # Force QLabel to have a tiny pixmap so it repaints
        self.setPixmap(QPixmap(1,1))
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # No scaling here; paintEvent handles scaling
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap_original:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        label_size = self.size()
        # Scale the original pixmap to fit the label while keeping aspect ratio
        scaled_pix = self.pixmap_original.scaled(
            label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Center the image in the label
        pix_rect = QRect(
            (label_size.width() - scaled_pix.width()) // 2,
            (label_size.height() - scaled_pix.height()) // 2,
            scaled_pix.width(),
            scaled_pix.height()
        )

        # Draw the scaled image
        painter.drawPixmap(pix_rect, scaled_pix)

        # Compute scaling factors for hotspots/rectangles
        x_scale = scaled_pix.width() / self.pixmap_original.width()
        y_scale = scaled_pix.height() / self.pixmap_original.height()

        # Draw cursors
        cursor_lookup = {c['name']: c for c in self.cursors_data}
        for cursor in self.cursors_data:
            rect_x = rect_y = rect_w = rect_h = 0
            hx = hy = None

            if "rect" in cursor:
                rect_x, rect_y, rect_w, rect_h = cursor["rect"]
            if "hotspot" in cursor:
                hx, hy = cursor["hotspot"]

            ref_name = cursor.get("ref")
            if ref_name and ref_name in cursor_lookup:
                ref_cursor = cursor_lookup[ref_name]
                if "rect" in ref_cursor:
                    rect_x, rect_y, rect_w, rect_h = ref_cursor["rect"]
                if "hotspot" in ref_cursor:
                    hx, hy = ref_cursor["hotspot"]

            # Draw rectangle
            if rect_w and rect_h:
                rect = QRect(
                    pix_rect.left() + int(rect_x * x_scale),
                    pix_rect.top() + int(rect_y * y_scale),
                    int(rect_w * x_scale),
                    int(rect_h * y_scale)
                )
                painter.setBrush(QColor(0, 255, 0, 60))
                pen = QPen(QColor(0, 255, 0, 180) if not ref_name else QColor(0, 200, 0, 180),
                           1, Qt.SolidLine if not ref_name else Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(rect)

            # Draw hotspot
            if hx is not None and hy is not None:
                abs_x = rect_x + hx
                abs_y = rect_y + hy
                hx_disp = pix_rect.left() + int(abs_x * x_scale)
                hy_disp = pix_rect.top() + int(abs_y * y_scale)
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.setBrush(QColor(255, 0, 0))
                painter.drawEllipse(hx_disp - 2, hy_disp - 2, 5, 5)

        painter.end()
