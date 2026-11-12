import tkinter as tk
import sys
from database.connection import init_database
from ui.login import tampilkan_login
from ui.main_window import buat_ui_utama
from config.settings import NAMA_TOKO

# Aktifkan High-DPI scaling di Windows agar tampilan tajam dan tidak blur
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    # 1. Init database (buat tabel kalau belum ada)
    init_database()
    
    # 2. Buat root window (hidden dulu)
    root = tk.Tk()
    root.title(f"POS Kasir - {NAMA_TOKO}")
    root.withdraw()   # sembunyikan sampai login sukses
    
    # 3. State global (untuk share keranjang antar handler)
    state = {
        "keranjang": [],       # list of dict item
        "nomor_nota": "000001",
        "user_id": None,
        "user_aktif": None,
        "nama_user": None,
        "total": 0,
        "bayar": 0,
        "kembali": 0,
        "is_retur": False,
        "pending_data": None,  # untuk F5/F6
        "diskon_global": 0,
        "diskon_global_rp": 0.0,
        "diskon_global_persen": 0.0,
        "biaya_tambahan": 0.0,
        "member": None,
        "member_id": "",
        "nomor_kassa": "001",
        "shift": "A"
    }
    
    # 4. Callback setelah login sukses
    def on_login_sukses(user_id, nama_user):
        state["user_id"] = user_id
        state["user_aktif"] = user_id
        state["nama_user"] = nama_user
        root.deiconify()      # munculkan root
        
        # [FIX] Buka dalam mode maximize di Windows
        try:
            root.state('zoomed')
        except Exception:
            root.attributes('-fullscreen', True)
            
        root.lift()           # angkat ke depan
        root.focus_force()    # paksa fokus
        buat_ui_utama(root, user_id, nama_user, state)
    
    # 5. Tampilkan login (BLOCKING sampai user login atau ESC)
    tampilkan_login(root, on_success=on_login_sukses)
    
    # 6. Mainloop — hanya jalan setelah login sukses
    root.mainloop()


if __name__ == "__main__":
    main()
