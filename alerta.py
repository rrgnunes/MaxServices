import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

# exibe uma janela de alerta
aviso = """
Sistema bloqueado por inadimplência de mensalidades.
Entre em contato com o suporte!
(66) 99926-4708
(66) 99926-3159
(66) 99926-3355
-------------------------------
Atenciosamente
Max Suport Sistemas
"""
# Exibição da janela de alerta
app = QApplication(sys.argv)
widget = QWidget()
msgBox = QMessageBox()
msgBox.setIcon(QMessageBox.Warning)
msgBox.setText("Aviso Importante!")
msgBox.setInformativeText(aviso)
msgBox.setWindowTitle("Aviso MaxSuport")
msgBox.exec_()
