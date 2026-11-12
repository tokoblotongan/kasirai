import os
from datetime import datetime

try:
    import win32print
except ImportError:
    win32print = None

from config.settings import NAMA_TOKO, ALAMAT_TOKO, TELEPON_TOKO
from database.connection import get_koneksi

def _format_baris(kiri, kanan, lebar=32):
    """
    Helper untuk memformat satu baris struk rata kiri dan rata kanan dengan lebar 32 kolom.
    """
    kiri_str = str(kiri)
    kanan_str = str(kanan)
    spasi = max(1, lebar - len(kiri_str) - len(kanan_str))
    return kiri_str + (" " * spasi) + kanan_str

def _kirim_ke_printer(teks_bytes, root=None, nomor_nota="000000", teks_polos=""):
    """
    Mengirim raw bytes ESC/POS ke printer thermal default via win32print.
    Jika printer tidak terdeteksi / gagal, struk disimpan sebagai backup file teks di folder struk_backup/.
    """
    berhasil = False
    if win32print is not None:
        try:
            printer_name = win32print.GetDefaultPrinter()
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(hPrinter, 1, ("Struk POS", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, teks_bytes)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
                berhasil = True
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"[Printer Warning] Gagal kirim ke printer: {e}")
            berhasil = False
            
    if not berhasil:
        # Fallback: Simpan file teks ke folder struk_backup/
        folder_backup = "struk_backup"
        if not os.path.exists(folder_backup):
            try:
                os.makedirs(folder_backup, exist_ok=True)
            except Exception:
                pass
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nama_file = os.path.join(folder_backup, f"nota_{nomor_nota}_{timestamp}.txt")
        try:
            with open(nama_file, "w", encoding="utf-8") as f:
                f.write(teks_polos)
        except Exception as e:
            print(f"[Backup Struk Error] Gagal menulis file struk: {e}")
            
        if root is not None:
            from ui.dialogs import info_kk
            pesan_notif = (
                f"Printer tidak terdeteksi. Struk disimpan sebagai file teks di folder "
                f"struk_backup/nota_{nomor_nota}_{timestamp}.txt"
            )
            info_kk(root, "Info", pesan_notif)

def cetak_struk(nomor_nota, keranjang_items, total, bayar, kembali,
                is_retur=False, user_id=None, root=None,
                diskon_global_rp=0.0, diskon_global_persen=0.0,
                is_copy=False):
    """
    Mencetak struk transaksi penjualan / retur barang ke printer thermal ESC/POS (lebar 32 karakter).
    """
    lebar = 32
    garis_sama = "=" * lebar
    garis_strip = "-" * lebar
    
    tgl_jam = datetime.now().strftime("%d-%m-%Y %H:%M")
    kasir_str = user_id or "KASIR"
    
    lines = []
    lines.append(garis_sama)
    lines.append(NAMA_TOKO.center(lebar))
    if ALAMAT_TOKO:
        lines.append(ALAMAT_TOKO.center(lebar))
    if TELEPON_TOKO:
        lines.append(f"Telp: {TELEPON_TOKO}".center(lebar))
    lines.append(garis_sama)
    
    if is_retur:
        lines.append("*** STRUK RETUR ***".center(lebar))
        
    # [FIX] Tambahkan penanda COPY STRUK
    if is_copy:
        lines.append("*** COPY STRUK ***".center(lebar))
        
    lines.append(f"No   : {nomor_nota}")
    lines.append(f"Tgl  : {tgl_jam}")
    lines.append(f"Kasir: {kasir_str}")
    lines.append(garis_strip)
    
    total_diskon_item = 0.0
    
    # Body: per item
    for item in keranjang_items:
        nama = item.get("nama", "BARANG")[:lebar].upper()
        lines.append(nama)
        
        qty = item.get("qty", 1.0)
        harga = item.get("harga", 0.0)
        diskon_pct = item.get("diskon_pct", 0.0)
        diskon_rp = item.get("diskon_rp", 0.0)
        potongan_pct = harga * diskon_pct / 100.0
        
        if "subtotal" in item:
            subtotal = item["subtotal"]
        else:
            subtotal = (harga - potongan_pct) * qty - diskon_rp
            
        # Format baris kuantitas & harga (dukung minus eksplisit)
        qty_harga_str = f"  {qty:g} x Rp {harga:,.0f}".replace(",", ".")
        if subtotal < 0:
            subtotal_str = f"-Rp {abs(subtotal):,.0f}".replace(",", ".")
        else:
            subtotal_str = f"Rp {subtotal:,.0f}".replace(",", ".")
            
        lines.append(_format_baris(qty_harga_str, subtotal_str, lebar))
        
        # [FIX] Cetak baris diskon per-item jika ada (POS Lama style)
        diskon_item_rp = (harga * diskon_pct / 100) * qty + diskon_rp
        if diskon_item_rp > 0:
            total_diskon_item += diskon_item_rp
            lines.append(_format_baris(
                f"  Hrg:Rp {harga:,.0f}".replace(",", "."),
                f"(-)Dskn:Rp {diskon_item_rp:,.0f}".replace(",", "."),
                lebar
            ))
        
    lines.append(garis_strip)
    
    # ============================================================
    # FOOTER: Diskon Global & Hemat
    # ============================================================
    if diskon_global_rp > 0:
        lines.append(_format_baris("DISKON GLOBAL (-)", f"Rp {diskon_global_rp:,.0f}".replace(",", "."), lebar))
    elif diskon_global_persen > 0:
        lines.append(_format_baris("DISKON GLOBAL (-)", f"{diskon_global_persen:g}%", lebar))
        
    total_hemat = total_diskon_item + diskon_global_rp
    # ============================================================

    # Format Footer (dukung format minus eksplisit)
    if total < 0:
        total_str = f"-Rp {abs(total):,.0f}".replace(",", ".")
    else:
        total_str = f"Rp {total:,.0f}".replace(",", ".")
        
    if bayar < 0:
        bayar_str = f"-Rp {abs(bayar):,.0f}".replace(",", ".")
    else:
        bayar_str = f"Rp {bayar:,.0f}".replace(",", ".")
        
    if kembali < 0:
        kembali_str = f"-Rp {abs(kembali):,.0f}".replace(",", ".")
    else:
        kembali_str = f"Rp {kembali:,.0f}".replace(",", ".")
        
    label_total = "Total Retur" if is_retur or total < 0 else "TOTAL"
    label_bayar = "Kasir Bayar" if is_retur or total < 0 else "BAYAR"
    
    lines.append(_format_baris(label_total, total_str, lebar))
    lines.append(_format_baris(label_bayar, bayar_str, lebar))
    lines.append(_format_baris("KEMBALI", kembali_str, lebar))
    
    # Tampilkan total hemat jika ada
    if total_hemat > 0:
        lines.append(_format_baris("ANDA MENGHEMAT", f"Rp {total_hemat:,.0f}".replace(",", "."), lebar))
        
    lines.append(garis_sama)
    lines.append("Terima kasih".center(lebar))
    lines.append("Barang yang sudah dibeli".center(lebar))
    lines.append("tidak dapat dikembalikan".center(lebar))
    lines.append(garis_sama)
    
    teks_polos = "\n".join(lines) + "\n"
    
    # Perintah ESC/POS untuk printer thermal TM-P58
    ESC = b'\x1b'
    GS = b'\x1d'
    INIT = ESC + b'@'
    ALIGN_LEFT = ESC + b'a\x00'
    ALIGN_CENTER = ESC + b'a\x01'
    CUT = b'\n\n\n' + GS + b'V\x00'
    OPEN_DRAWER = ESC + b'p\x00\x19\xfa'
    
    raw_data = INIT + ALIGN_LEFT
    for line in lines:
        try:
            raw_data += line.encode("cp437") + b'\n'
        except UnicodeEncodeError:
            raw_data += line.encode("cp437", errors="replace") + b'\n'
            
    raw_data += CUT
    if not is_retur and total >= 0:
        raw_data += OPEN_DRAWER
        
    _kirim_ke_printer(raw_data, root=root, nomor_nota=nomor_nota, teks_polos=teks_polos)
    return teks_polos

def cetak_struk_retur(nomor_nota, items, total, bayar, kembali, root=None, user_id=None):
    """
    Wrapper sederhana untuk cetak struk khusus retur barang.
    """
    return cetak_struk(
        nomor_nota, items, total, bayar, kembali,
        is_retur=True, user_id=user_id, root=root
    )

def copy_struk(event=None, root=None, refs=None, state=None):
    """
    Mencetak ulang struk transaksi terakhir.
    """
    # [FIX] Cek transaksi_terakhir di state
    transaksi = state.get("transaksi_terakhir") if state else None
    if not transaksi:
        if root:
            from ui.dialogs import info_kk
            info_kk(root, "Info", "Belum ada transaksi yang bisa dicetak ulang.", refs=refs)
        return "break"
        
    cetak_struk(
        nomor_nota=transaksi["nomor_nota"],
        keranjang_items=transaksi["keranjang"],
        total=transaksi["total"],
        bayar=transaksi["bayar"],
        kembali=transaksi["kembali"],
        is_retur=transaksi.get("is_retur", False),
        user_id=transaksi.get("user_id"),
        root=root,
        diskon_global_rp=transaksi.get("diskon_global_rp", 0.0),
        diskon_global_persen=transaksi.get("diskon_global_persen", 0.0),
        is_copy=True  # [FIX] Tandai sebagai cetakan ulang
    )
    
    if root:
        from ui.dialogs import info_kk
        info_kk(root, "Sukses", "Struk berhasil dicetak ulang.", refs=refs)
    return "break"

def buka_laci(event=None, root=None, refs=None, state=None):
    """
    Mengirim sinyal ESC/POS p 0 25 250 untuk membuka laci kasir (cash drawer).
    """
    if win32print is not None:
        try:
            printer_name = win32print.GetDefaultPrinter()
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(hPrinter, 1, ("Open Cash Drawer", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, bytes([27, 112, 0, 25, 250]))
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"[Drawer Warning] Gagal membuka laci: {e}")
    return "break"
