import json
from datetime import datetime
from .connection import get_connection

# ============================================================
# OTENTIKASI PENGGUNA
# ============================================================

def cek_login(uid, pwd):
    """
    Memeriksa kredensial user di tabel PASSW.
    Return: (NOPEGAWAI, NAMA_USER) jika valid, None jika salah.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT NOPEGAWAI, NAMA_USER FROM PASSW WHERE NOPEGAWAI=? AND PASSWORD=?",
            (uid, pwd)
        )
        return cursor.fetchone()
    finally:
        conn.close()

# ============================================================
# PENCARIAN BARANG
# ============================================================

def cari_barang_by_kode(kode):
    """
    Mencari satu barang berdasarkan KODE (PLU) atau BARKODE persis.
    Return: (BARANG, NAMABRG, HARGAJUAL, SATUAN) atau None.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BARANG, NAMABRG, HARGAJUAL, SATUAN FROM barang WHERE BARANG=? OR BARKODE=?",
            (kode, kode)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def cari_barang_by_nama(kode_atau_nama, limit=50):
    """
    Mencari barang berdasarkan pola nama barang dengan bobot prioritas awalan.
    Return: list of (BARANG, NAMABRG, HARGAJUAL, SATUAN).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BARANG, NAMABRG, HARGAJUAL, SATUAN FROM barang "
            "WHERE NAMABRG LIKE ? "
            "ORDER BY "
            "  CASE "
            "    WHEN UPPER(NAMABRG) LIKE UPPER(?) THEN 1 "
            "    WHEN UPPER(NAMABRG) LIKE UPPER(?) THEN 2 "
            "    ELSE 3 "
            "  END, "
            "  NAMABRG "
            "LIMIT ?",
            (f"%{kode_atau_nama}%", f"{kode_atau_nama}%", f"% {kode_atau_nama}%", limit)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def cari_barang_full(keyword, limit=200):
    """
    Pencarian mendalam untuk dialog F10 Cari Barang (nama atau kode).
    Return: list of (BARANG, NAMABRG, HARGAJUAL, BARKODE, SATUAN, STOKTOKO).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BARANG, NAMABRG, HARGAJUAL, BARKODE, SATUAN, STOKTOKO "
            "FROM barang "
            "WHERE NAMABRG LIKE ? OR BARANG LIKE ? "
            "ORDER BY "
            "  CASE "
            "    WHEN UPPER(NAMABRG) LIKE UPPER(?) THEN 1 "
            "    WHEN UPPER(NAMABRG) LIKE UPPER(?) THEN 2 "
            "    WHEN UPPER(NAMABRG) LIKE UPPER(?) THEN 3 "
            "    ELSE 4 "
            "  END, "
            "  NAMABRG "
            "LIMIT ?",
            (
                f"%{keyword}%", f"%{keyword}%",
                f"{keyword}%", f"% {keyword}%", f"%{keyword}",
                limit
            )
        )
        return cursor.fetchall()
    finally:
        conn.close()

# ============================================================
# STOK & NOTA TRANSAKSI
# ============================================================

def update_stok(kode, qty_terjual, conn=None):
    """
    Mengurangi STOKTOKO sebanyak qty_terjual untuk barang tertentu.
    Jika conn disertakan, eksekusi dalam transaksi yang sama.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE barang SET STOKTOKO = STOKTOKO - ? WHERE BARANG = ?",
            (qty_terjual, kode)
        )
        if close_after:
            conn.commit()
    finally:
        if close_after:
            conn.close()

def get_max_nofaktur(tgl):
    """
    Mengambil angka faktur tertinggi pada tanggal tertentu.
    Return: integer max atau None.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(CAST(NOFAKTUR AS INTEGER)) FROM hjualpos WHERE TGLJUAL=?",
            (tgl,)
        )
        res = cursor.fetchone()
        if res and res[0]:
            return int(res[0])
        return None
    finally:
        conn.close()

def generate_nomor_nota(tgl=None):
    """
    Menghasilkan string nomor nota urut harian 6 digit (misal: '000001').
    """
    if tgl is None:
        tgl = datetime.now().strftime("%Y-%m-%d")
    try:
        max_no = get_max_nofaktur(tgl)
        if max_no is not None:
            return f"{max_no + 1:06d}"
    except Exception:
        pass
    return "000001"

def get_max_no_urut(nomor_nota, conn=None):
    """
    Mendapatkan nomor urut item tertinggi pada faktur tertentu di pjualpos.
    Return: integer urutan terakhir (default 0).
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(NO) FROM pjualpos WHERE NOFAKTUR=?", (nomor_nota,))
        res = cursor.fetchone()
        return res[0] or 0 if res else 0
    finally:
        if close_after:
            conn.close()

# ============================================================
# PENYIMPANAN TRANSAKSI PENJUALAN
# ============================================================

def simpan_header_transaksi(header_data, conn=None):
    """
    Menyimpan data header penjualan ke tabel hjualpos.
    header_data berupa tuple/list nilai untuk 13 kolom faktur.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hjualpos (
                NOFAKTUR, TGLJUAL, JAMJUAL, SHIFT, NOMORKASSA, NOOPERATOR,
                TOTALJUAL, BAYAR, RPKEMBALI, CARABAYAR, MEMBER, RPCARD, CARD
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, header_data)
        if close_after:
            conn.commit()
    finally:
        if close_after:
            conn.close()

def simpan_detail_transaksi(detail_rows, conn=None):
    """
    Menyimpan baris detail item ke tabel pjualpos.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO pjualpos (
                SHIFT, NOMORKASSA, NOFAKTUR, NO, KODEBRG, NAMABRG, HARGAJUAL,
                DISKON, DISKONRP, DISKMEMBERP, DISKGLBAL, DISKMULTI, QTY,
                SATUANJUAL, ISTPHARGA, NAMABRGNET, NOMORNOTA, TGLJUAL, TGLJAMJUAL, JAMJUAL
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, detail_rows)
        if close_after:
            conn.commit()
    finally:
        if close_after:
            conn.close()

# ============================================================
# TRANSAKSI PENDING (HOLD SALE)
# ============================================================

def simpan_pending(nama_pembeli, data_dict):
    """
    Menyimpan transaksi keranjang tertunda ke tabel pending.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        tgl_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO pending (nama_pembeli, data_keranjang, tanggal) VALUES (?, ?, ?)",
            (nama_pembeli, json.dumps(data_dict), tgl_sekarang)
        )
        conn.commit()
    finally:
        conn.close()

def load_semua_pending():
    """
    Mengambil semua data transaksi tertunda.
    Return: list of (id, nama_pembeli, tanggal, data_keranjang).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_pembeli, tanggal, data_keranjang FROM pending")
        return cursor.fetchall()
    finally:
        conn.close()

def ambil_pending(id_pending):
    """
    Mengambil 1 data pending dan langsung menghapusnya dari tabel pending.
    Return: (data_keranjang_json, nama_pembeli) atau None jika tidak ditemukan.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT data_keranjang, nama_pembeli FROM pending WHERE id=?", (id_pending,))
        row = cursor.fetchone()
        if row:
            cursor.execute("DELETE FROM pending WHERE id=?", (id_pending,))
            conn.commit()
        return row
    finally:
        conn.close()

def hapus_pending(id_pending):
    """
    Menghapus 1 baris data pending berdasarkan ID.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending WHERE id=?", (id_pending,))
        conn.commit()
    finally:
        conn.close()

def hapus_semua_pending():
    """
    Menghapus seluruh baris data di tabel pending.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending")
        conn.commit()
    finally:
        conn.close()