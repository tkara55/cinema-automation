from PyQt5 import uic

with open("Sinema_Rezervasyon.py","w",encoding="utf-8") as fout:
    uic.compileUi("sinema_rezervasyon.ui", fout)