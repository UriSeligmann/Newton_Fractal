# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QTabWidget, QLabel, QProgressBar, QHBoxLayout, QSpinBox,
    QStyleFactory, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPalette, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect, QSize
import numpy as np
from fractal_engine import NewtonFractalEngine

class FractalWorker(QThread):
    finished = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int)

    def __init__(self, func_str, width, height, xlim, ylim):
        super().__init__()
        self.func_str = func_str
        self.width = width
        self.height = height
        self.xlim = xlim
        self.ylim = ylim

    def run(self):
        engine = NewtonFractalEngine(
            func_str=self.func_str,
            width=self.width,
            height=self.height
        )
        engine.xlim = self.xlim
        engine.ylim = self.ylim
        
        def progress_callback(percent):
            self.progress.emit(percent)
        
        image = engine.compute(progress_callback=progress_callback)
        self.finished.emit(image)

class FractalTab(QWidget):
    def __init__(self, width=600, height=500):
        super().__init__()
        self.base_width = width
        self.base_height = height
        self.zoom_level = 0
        self.max_zoom_level = 5
        self.worker = None

        layout = QVBoxLayout()
        layout.setSpacing(8)  # Reduced spacing
        layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        self.setLayout(layout)

        # Controls with better styling
        hbox_controls = QHBoxLayout()
        hbox_controls.setSpacing(8)  # Reduced spacing
        
        func_label = QLabel("f(z):")
        func_label.setStyleSheet("font-weight: bold; color: #E8E8E8;")
        
        self.func_input = QLineEdit("z**3 - 1")
        self.func_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #FFFFFF;
                selection-background-color: #0078D4;
            }
            QLineEdit:focus {
                border-color: #0078D4;
                background-color: #323232;
            }
            QLineEdit:hover {
                border-color: #505050;
            }
        """)
        
        self.compute_btn = QPushButton("Compute")
        self.compute_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078D4, stop:1 #106EBE);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1084E0, stop:1 #0F7BD4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #006BB3, stop:1 #0E6BAD);
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)
        
        self.reset_btn = QPushButton("Reset Zoom")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A4A4A, stop:1 #3A3A3A);
                border: 1px solid #555555;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555555, stop:1 #454545);
                border-color: #666666;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:1 #2A2A2A);
            }
            QPushButton:disabled {
                background: #2A2A2A;
                color: #606060;
                border-color: #303030;
            }
        """)

        self.save_btn = QPushButton("Save Image")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFC107, stop:1 #FF8F00);
                border: none;
                border-radius: 8px;
                color: #1A1A1A;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD54F, stop:1 #FFA000);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8F00, stop:1 #E65100);
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)
        
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DC3545, stop:1 #C82333);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E85A67, stop:1 #D73E4D);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C82333, stop:1 #A71E2A);
            }
        """)

        hbox_controls.addWidget(func_label)
        hbox_controls.addWidget(self.func_input)
        hbox_controls.addWidget(self.compute_btn)
        hbox_controls.addWidget(self.reset_btn)
        hbox_controls.addWidget(self.save_btn)
        hbox_controls.addWidget(self.exit_btn)

        layout.addLayout(hbox_controls)

        # Resolution control with better styling
        hbox_res = QHBoxLayout()
        hbox_res.setSpacing(8)  # Reduced spacing
        
        res_label = QLabel("Resolution Multiplier:")
        res_label.setStyleSheet("font-weight: bold; color: #E8E8E8;")
        
        self.res_spinbox = QSpinBox()
        self.res_spinbox.setMinimum(1)
        self.res_spinbox.setMaximum(50)
        self.res_spinbox.setValue(1)
        self.res_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2A2A2A;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 4px 8px;    /* Reduced padding */
                font-size: 12px;     /* Smaller font */
                color: #FFFFFF;
                min-width: 60px;     /* Reduced width */
            }
            QSpinBox:focus {
                border-color: #0078D4;
                background-color: #323232;
            }
            QSpinBox:hover {
                border-color: #505050;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #404040;
                border: none;
                width: 16px;
                border-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #505050;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                color: #FFFFFF;
            }
        """)

        self.recompute_btn = QPushButton("Recompute")
        self.recompute_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28A745, stop:1 #1E7E34);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2DB84F, stop:1 #228B3B);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E7E34, stop:1 #186429);
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)

        hbox_res.addWidget(res_label)
        hbox_res.addWidget(self.res_spinbox)
        hbox_res.addWidget(self.recompute_btn)
        hbox_res.addStretch()
        layout.addLayout(hbox_res)

        # Progress bar with fixed positioning
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 10px;
                text-align: center;
                background-color: #2A2A2A;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;     /* Smaller font */
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078D4, stop:0.5 #40A0FF, stop:1 #0078D4);
                border-radius: 8px;
                margin: 1px;
            }
        """)
        self.progress.hide()
        layout.addWidget(self.progress)

        # Image display with fixed size policy
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMouseTracking(True)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px solid #555555;
                border-radius: 12px;
                background-color: #1A1A1A;
            }
        """)
        # Use expanding size policy to fill remaining space
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label.setMinimumSize(400, 300)  # Smaller minimum
        layout.addWidget(self.label)
        
        self.pix = QPixmap()
        self._original_pixmap = QPixmap()

        # Zoom state
        self.start_pos = None
        self.end_pos = None
        self.xlim = (-2, 2)
        self.ylim = (-2, 2)
        self.current_image = None  # Store current image for saving

        # Connections
        self.compute_btn.clicked.connect(self.compute_fractal)
        self.reset_btn.clicked.connect(self.reset_zoom)
        self.recompute_btn.clicked.connect(self.compute_fractal)
        self.save_btn.clicked.connect(self.save_image)
        self.exit_btn.clicked.connect(self.exit_app)

        # Mouse events
        self.label.mousePressEvent = self.mouse_press
        self.label.mouseMoveEvent = self.mouse_move
        self.label.mouseReleaseEvent = self.mouse_release

    def compute_fractal(self):
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()

        func_str = self.func_input.text()
        self.compute_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.recompute_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress.setValue(0)
        self.progress.show()

        res_multiplier = self.res_spinbox.value()
        self.current_width = self.base_width * res_multiplier
        self.current_height = self.base_height * res_multiplier

        self.worker = FractalWorker(
            func_str,
            self.current_width,
            self.current_height,
            self.xlim,
            self.ylim
        )
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()

    def on_worker_finished(self, img):
        self.current_image = img  # Store for saving
        self.display_image(img)
        self.progress.hide()
        self.compute_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.recompute_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def update_progress(self, value):
        self.progress.setValue(value)

    def display_image(self, img):
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
        if img.shape[2] == 3:
            qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format.Format_RGB888)
        else:
            qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format.Format_Grayscale8)

        self.full_res_pix = QPixmap.fromImage(qimg)
        
        # Scale the pixmap to fit the label's current size
        label_size = self.label.size()
        self.pix = self.full_res_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(self.pix)
        
    # Mouse events
    def mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self._original_pixmap = self.pix.copy()

    def mouse_move(self, event):
        if self.start_pos:
            self.end_pos = event.pos()
            temp_pix = self._original_pixmap.copy()
            painter = QPainter(temp_pix)
            painter.setPen(Qt.GlobalColor.red)

            dx = self.end_pos.x() - self.start_pos.x()
            dy = self.end_pos.y() - self.start_pos.y()
            side = min(abs(dx), abs(dy))

            rect = QRect(self.start_pos, QPoint(self.start_pos.x() + (side if dx > 0 else -side), self.start_pos.y() + (side if dy > 0 else -side)))
            painter.drawRect(rect.normalized())
            painter.end()
            self.label.setPixmap(temp_pix)
            self.label.repaint()

    def mouse_release(self, event):
        if self.start_pos and event.button() == Qt.MouseButton.LeftButton and self.zoom_level < self.max_zoom_level:
            x_scale = (self.xlim[1] - self.xlim[0]) / self.pix.width()
            y_scale = (self.ylim[1] - self.ylim[0]) / self.pix.height()

            start_x = self.start_pos.x()
            start_y = self.start_pos.y()
            end_x = event.pos().x()
            end_y = event.pos().y()

            dx = end_x - start_x
            dy = end_y - start_y
            side = min(abs(dx), abs(dy))
            end_x = start_x + (side if dx > 0 else -side)
            end_y = start_y + (side if dy > 0 else -side)

            x0 = self.xlim[0] + min(start_x, end_x) * x_scale
            x1 = self.xlim[0] + max(start_x, end_x) * x_scale
            y0 = self.ylim[0] + min(start_y, end_y) * y_scale
            y1 = self.ylim[0] + max(start_y, end_y) * y_scale

            self.xlim = (x0, x1)
            self.ylim = (y0, y1)
            self.zoom_level += 1

            self.start_pos = None
            self.end_pos = None
            self.compute_fractal()
            self.label.setPixmap(self.pix)

    def reset_zoom(self):
        self.xlim = (-2, 2)
        self.ylim = (-2, 2)
        self.zoom_level = 0
        self.compute_fractal()

    def save_image(self):
        if self.current_image is None:
            return
        
        from PyQt6.QtWidgets import QFileDialog
        import os
        from datetime import datetime
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        func_name = self.func_input.text().replace('*', 'x').replace('/', 'div').replace(' ', '')
        default_name = f"fractal_{func_name}_{timestamp}.png"
        
        # Open file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Fractal Image",
            default_name,
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if filename:
            # Convert numpy array to QImage and save
            img = np.clip(self.current_image * 255, 0, 255).astype(np.uint8)
            if img.shape[2] == 3:
                qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format.Format_RGB888)
            else:
                qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format.Format_Grayscale8)
            
            qimg.save(filename)
    
    def exit_app(self):
        # Clean shutdown
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        QApplication.quit()

class FractalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Newton Fractal Viewer")
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #252525;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:1 #2A2A2A);
                border: 1px solid #404040;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
                padding: 8px 16px;
                color: #E8E8E8;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078D4, stop:1 #106EBE);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #454545, stop:1 #353535);
            }
        """)
        
        self.fractal_tab = FractalTab()
        self.tabs.addTab(self.fractal_tab, "Iterations")
        layout.addWidget(self.tabs)

    def show(self):
        super().show()
        self.showFullScreen()

    def closeEvent(self, event):
        if self.fractal_tab.worker and self.fractal_tab.worker.isRunning():
            self.fractal_tab.worker.quit()
            self.fractal_tab.worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Enhanced dark theme palette
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(232, 232, 232))
    palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 37))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 85, 127))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 120, 212))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 212))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    win = FractalApp()
    win.show()
    sys.exit(app.exec())