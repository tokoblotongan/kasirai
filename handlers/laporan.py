from database.connection import get_connection

def get_laporan_penjualan(tgl_mulai, tgl_akhir):
    """
    Tab 1: Penjualan & Cara Bayar
    Total Netto diambil dari TOTALJUAL di Header (hjualpos) agar tidak berlipat ganda.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(CARABAYAR, 'CASH') AS cara_bayar, 
                COUNT(NOFAKTUR) AS jumlah_nota, 
                COALESCE(SUM(TOTALJUAL), 0) AS total_netto
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY CARABAYAR
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_audit(tgl_mulai, tgl_akhir):
    """
    Tab 2: Audit Kasir (Bruto, Diskon Item, Diskon Global, Void, Refund, Netto)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(NOOPERATOR, 'KASIR') AS operator, 
                COALESCE(SUM(TOTALJUAL), 0) AS total_netto,
                COALESCE(SUM(TTLDSKITEM), 0) AS diskon_item, 
                COALESCE(SUM(RPDISKON), 0) AS diskon_global,
                COALESCE(SUM(TTLVOID), 0) AS total_void,
                COALESCE(SUM(TTLJUALRFN), 0) AS total_refund,
                COUNT(NOFAKTUR) AS jumlah_faktur
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY NOOPERATOR
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_shift(tgl_mulai, tgl_akhir):
    """
    Laporan Kassa - Kasir - Shift
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(NOMORKASSA, '001') AS kassa, 
                COALESCE(NOOPERATOR, 'KASIR') AS operator, 
                COALESCE(SHIFT, 'A') AS shift, 
                COUNT(NOFAKTUR) AS jumlah_faktur, 
                COALESCE(SUM(TOTALJUAL), 0) AS total_netto
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY NOMORKASSA, NOOPERATOR, SHIFT
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_rekonsiliasi(tgl_mulai, tgl_akhir):
    """
    Tab 4: Rekonsiliasi Kas (Modal, Biaya, Penjualan Kasir, Setoran, Selisih)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                NOOPERATOR, SHIFT, MODAL, BIAYA, TTLJUALKSR, SETORAN,
                (MODAL + TTLJUALKSR - BIAYA) AS uang_sistem,
                (SETORAN - (MODAL + TTLJUALKSR - BIAYA)) AS selisih
            FROM kasir 
            WHERE TANGGAL BETWEEN ? AND ?
        """, (tgl_mulai, tgl_akhir))
        rows = cursor.fetchall()
        if not rows:
            # Fallback jika data kasir fisik belum diisi: ambil dari hjualpos
            cursor.execute("""
                SELECT 
                    COALESCE(NOOPERATOR, 'KASIR') AS operator,
                    COALESCE(SHIFT, 'A') AS shift,
                    200000.0 AS modal,
                    0.0 AS biaya,
                    COALESCE(SUM(TOTALJUAL), 0) AS total_jual,
                    (200000.0 + COALESCE(SUM(TOTALJUAL), 0)) AS setoran,
                    (200000.0 + COALESCE(SUM(TOTALJUAL), 0)) AS uang_sistem,
                    0.0 AS selisih
                FROM hjualpos
                WHERE TGLJUAL BETWEEN ? AND ?
                GROUP BY NOOPERATOR, SHIFT
            """, (tgl_mulai, tgl_akhir))
            rows = cursor.fetchall()
        return rows
    finally:
        conn.close()

def get_laporan_daftar_refund(tgl_mulai, tgl_akhir):
    """
    Daftar item retur / refund
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                h.NOFAKTUR, 
                h.TGLJUAL, 
                p.KODEBRG, 
                p.NAMABRG, 
                p.QTY, 
                (p.HARGAJUAL * p.QTY) AS total_nilai
            FROM pjualpos p
            JOIN hjualpos h ON p.NOFAKTUR = h.NOFAKTUR
            WHERE h.TGLJUAL BETWEEN ? AND ? AND (p.QTY < 0 OR p.VOID = 1)
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_barang_laku(tgl_mulai, tgl_akhir):
    """
    Tab 6: Laporan Barang Laku (Rekapitulasi Semua Barang Terjual)
    Menampilkan SEMUA barang yang terjual pada periode tanggal tersebut
    untuk melihat pergerakan stok keluar. Diurutkan berdasarkan Kode Barang (A-Z).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.KODEBRG, 
                p.NAMABRG, 
                SUM(p.QTY) AS total_qty, 
                SUM(p.HARGANET) AS total_netto
            FROM pjualpos p 
            JOIN hjualpos h ON p.NOFAKTUR = h.NOFAKTUR
            WHERE h.TGLJUAL BETWEEN ? AND ? AND p.QTY > 0
            GROUP BY p.KODEBRG, p.NAMABRG 
            ORDER BY p.KODEBRG ASC;
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

# Alias kompatibilitas
get_laporan_best_seller = get_laporan_barang_laku

def get_laporan_per_nota(tgl_mulai, tgl_akhir):
    """
    Tab 5: Per Nota Faktur Penjualan
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                NOFAKTUR, 
                TGLJUAL, 
                JAMJUAL, 
                NOOPERATOR, 
                COALESCE(CARABAYAR, 'CASH') AS cara_bayar,
                TOTALJUAL 
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            ORDER BY TGLJUAL DESC, NOFAKTUR DESC
            LIMIT 100
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()
