
import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView

class SibiaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIBIA Control")
        self.setGeometry(100, 100, 400, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Input para IP del servidor
        self.ip_input = QLineEdit("192.168.1.8:5000")
        layout.addWidget(QLabel("IP del Servidor SIBIA:"))
        layout.addWidget(self.ip_input)
        
        # Botón para conectar
        self.connect_btn = QPushButton("Conectar a SIBIA")
        self.connect_btn.clicked.connect(self.conectar_sibia)
        layout.addWidget(self.connect_btn)
        
        # WebView para mostrar la interfaz
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Status
        self.status_label = QLabel("Listo para conectar")
        layout.addWidget(self.status_label)
        
    def conectar_sibia(self):
        ip = self.ip_input.text()
        url = f"http://{ip}"
        try:
            # Verificar conexión
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.web_view.load(url)
                self.status_label.setText(f"✅ Conectado a {ip}")
            else:
                self.status_label.setText(f"❌ Error de conexión")
        except Exception as e:
            self.status_label.setText(f"❌ No se pudo conectar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SibiaApp()
    window.show()
    sys.exit(app.exec_())
