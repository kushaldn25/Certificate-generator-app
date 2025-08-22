# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app import CertApp

def main():
    app=QApplication(sys.argv)
    w=CertApp(); w.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
