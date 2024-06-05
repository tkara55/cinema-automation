from PyQt5 import uic

with open("Login_Screen.py","w",encoding="utf-8") as fout:
    uic.compileUi("login_screen.ui", fout)