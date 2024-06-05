from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import sys
import sqlite3
from Sinema_Rezervasyon import *

def veritabani_olustur():
    baglanti = sqlite3.connect("koltuklar.db")
    islem = baglanti.cursor()

    islem.execute('''
    CREATE TABLE IF NOT EXISTS salonlar (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        SalonAdi TEXT
    )
    ''')

    islem.execute('''
    CREATE TABLE IF NOT EXISTS koltuklar (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Koltuk TEXT,
        Durum TEXT,
        SalonId INTEGER,
        FOREIGN KEY (SalonId) REFERENCES salonlar (Id)
    )
    ''')
    islem.execute('SELECT COUNT(*) FROM salonlar')
    if islem.fetchone()[0] == 0:

        islem.execute('INSERT INTO salonlar (SalonAdi) VALUES ("Salon 1")')
        islem.execute('INSERT INTO salonlar (SalonAdi) VALUES ("Salon 2")')

        for salon_id in range(1, 3):
            koltuk_isimleri = ([f'A{i}' for i in range(1, 9)] +
                               [f'B{i}' for i in range(1, 9)] +
                               [f'C{i}' for i in range(1, 9)] +
                               [f'D{i}' for i in range(1, 9)])
            for isim in koltuk_isimleri:
                islem.execute('INSERT INTO koltuklar (Koltuk, Durum, SalonId) VALUES (?, ?, ?)', (isim, "Y", salon_id))

    baglanti.commit()
    baglanti.close()

class PageProduct(QMainWindow):
    def __init__(self, selected_salon_id):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.selected_salon_id = selected_salon_id

        self.baglanti = sqlite3.connect("koltuklar.db")
        self.islem = self.baglanti.cursor()

        self.available_pixmap = QPixmap('C:\\Users\\Tuna\\Desktop\\sinema_rezervasyon\\seat_available.png')
        self.not_available_pixmap = QPixmap('C:\\Users\\Tuna\\Desktop\\sinema_rezervasyon\\seat_not_available.png')

        self.ui.butonRezervasyon.clicked.connect(self.rezervasyon)
        self.ui.butonIptal.clicked.connect(self.iptal)
        self.ui.butonSifirla.clicked.connect(self.sifirla)

        self.ui.butonCikis.clicked.connect(self.cikis_yap)

        self.destroyed.connect(self.closeEvent)

        self.resim_yukle()
        self.set_salon_label()
    
    def set_salon_label(self):
        self.ui.labelSalon.setText(f"Aktif Salon: Salon {self.selected_salon_id}")

    def resim_yukle(self):
        salon_id = self.selected_salon_id

        for i in range(1, 33):
            koltuk_isim = f'{chr(64 + (i - 1) // 8 + 1)}{(i - 1) % 8 + 1}'
            self.islem.execute('SELECT Durum FROM koltuklar WHERE Koltuk = ? AND SalonId = ?', (koltuk_isim, salon_id))
            durum = self.islem.fetchone()
            if durum:
                durum = durum[0]
                label_name = "lbl" + str(i)
                label = getattr(self.ui, label_name)
                if durum == "Y":
                    label.setPixmap(self.available_pixmap)
                else:
                    label.setPixmap(self.not_available_pixmap)

    def closeEvent(self, event):
        self.baglanti.close()

    def rezervasyon(self):
        koltuk_id = self.ui.cmbKoltukSec.currentIndex() + 1
        koltuk_isim = self.ui.cmbKoltukSec.currentText()
        salon_id = self.selected_salon_id

        self.islem.execute('SELECT Durum FROM koltuklar WHERE Koltuk = ? AND SalonId = ?', (koltuk_isim, salon_id))
        durum = self.islem.fetchone()[0]

        if durum == "N":
            self.statusBar().showMessage(f"Koltuk {koltuk_isim} zaten rezerve edilmiş.")
        else:
            self.islem.execute('UPDATE koltuklar SET Durum = "N" WHERE Koltuk = ? AND SalonId = ?', (koltuk_isim, salon_id))
            label_name = "lbl" + str(koltuk_id)
            label = getattr(self.ui, label_name)
            label.setPixmap(self.not_available_pixmap)
            self.baglanti.commit()
            self.statusBar().showMessage(f"Koltuk {koltuk_isim} rezerve edildi.")

    def iptal(self):
        koltuk_id = self.ui.cmbKoltukSec.currentIndex() + 1
        koltuk_isim = self.ui.cmbKoltukSec.currentText()
        salon_id = self.selected_salon_id

        self.islem.execute('SELECT Durum FROM koltuklar WHERE Koltuk = ? AND SalonId = ?', (koltuk_isim, salon_id))
        durum = self.islem.fetchone()[0]

        if durum == "Y":
            self.statusBar().showMessage(f"Koltuk {koltuk_isim} zaten boş.")
        else:
            self.islem.execute('UPDATE koltuklar SET Durum = "Y" WHERE Koltuk = ? AND SalonId = ?', (koltuk_isim, salon_id))
            label_name = "lbl" + str(koltuk_id)
            label = getattr(self.ui, label_name)
            label.setPixmap(self.available_pixmap)
            self.baglanti.commit()
            self.statusBar().showMessage(f"Koltuk {koltuk_isim} rezervesi iptal edildi.")

    def sifirla(self):
        salon_id = self.selected_salon_id
        for i in range(1, 33):
            label_name = "lbl" + str(i)
            label = getattr(self.ui, label_name)
            label.setPixmap(self.available_pixmap)
        self.islem.execute('UPDATE koltuklar SET Durum = "Y" WHERE SalonId = ?', (salon_id,))
        self.statusBar().showMessage(f"Tüm koltuklar sıfırlandı")
        self.baglanti.commit()

    def cikis_yap(self):
        self.login_window = LoginPage()
        self.login_window.show()
        self.close()

class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('login_screen.ui', self)

        self.load_salonlar()

        self.cmbSalonSec.currentIndexChanged.connect(self.load_table_data)
        self.btnGiris.clicked.connect(self.open_main_window)

        self.load_table_data()

    def load_salonlar(self):
        baglanti = sqlite3.connect("koltuklar.db")
        islem = baglanti.cursor()
        islem.execute('SELECT Id, SalonAdi FROM salonlar')
        salonlar = islem.fetchall()
        for salon in salonlar:
            self.cmbSalonSec.addItem(salon[1], salon[0])
        baglanti.close()

    def load_table_data(self):
        selected_salon_id = self.cmbSalonSec.currentData()
        if selected_salon_id is None:
            return

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Id", "Koltuk", "Durum"])

        baglanti = sqlite3.connect("koltuklar.db")
        islem = baglanti.cursor()
        islem.execute('SELECT Id, Koltuk, Durum FROM koltuklar WHERE SalonId = ?', (selected_salon_id,))
        koltuklar = islem.fetchall()

        for row_num, row_data in enumerate(koltuklar):
            self.tableWidget.insertRow(row_num)
            koltuk_id, koltuk_isim, durum = row_data
            durum = "Boş" if durum == "Y" else "Dolu"
            self.tableWidget.setItem(row_num, 0, QTableWidgetItem(str(koltuk_id)))
            self.tableWidget.setItem(row_num, 1, QTableWidgetItem(koltuk_isim))
            self.tableWidget.setItem(row_num, 2, QTableWidgetItem(durum))

        baglanti.close()

    def open_main_window(self):
        selected_salon_id = self.cmbSalonSec.currentData()
        self.main_window = PageProduct(selected_salon_id)
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    veritabani_olustur()
    app = QApplication(sys.argv)
    login_window = LoginPage()
    login_window.show()
    sys.exit(app.exec_())