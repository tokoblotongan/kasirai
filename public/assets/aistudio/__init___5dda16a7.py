# handlers/__init__.py
# Sengaja dibiarkan KOSONG untuk mencegah circular import antara handlers/ dan ui/.
#
# Cara import yang BENAR (langsung dari submodule, bukan dari package):
#   from handlers.keranjang import tambah_barang_ke_keranjang
#   from handlers.checkout import proses_checkout
#   from handlers.cari_barang import buka_dialog_cari_barang
#   from handlers.pending import set_pending, call_pending, clear_pending
#   from handlers.aksi_lain import *
