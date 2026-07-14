from gui.app import CyberForgeApp
from db import initialiser_bd

if __name__ == "__main__":
    initialiser_bd()  # Crée les tables si elles n'existent pas encore
    app = CyberForgeApp()
    app.mainloop()