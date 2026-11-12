import os

# ============================================================
# KONFIGURASI SISTEM POS & IDENTITAS TOKO
# ============================================================

# PERBAIKAN: Path dinamis ke folder data/ di dalam proyek V2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "toko.db")

NAMA_TOKO       = "TB.BLOTONGAN"
SLOGAN_TOKO     = "TOKO BESI & BANGUNAN"
ALAMAT_TOKO     = "Jl. Fatmawati 3A-B"
TELEPON_TOKO    = ""  # Dikosongkan sesuai instruksi
NOMOR_KASSA     = "001"
SHIFT_DEFAULT   = "A"

# Pengaturan Window Tkinter
WINDOW_TITLE    = f"{NAMA_TOKO} - POS Kasir V3"
WINDOW_SIZE     = "1200x768"

# Pengaturan Printer Kasir ESC/POS
PRINTER_WIDTH   = 32
