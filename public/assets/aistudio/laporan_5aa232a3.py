from database.connection import get_connection

def get_laporan_penjualan(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Total Netto diambil dari TOTALJUAL di Header, bukan HARGANET di Detail
        cursor.execute("""
            SELECT CARABAYAR, COUNT(NOFAKTUR), SUM(TOTALJUAL) 
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY CARABAYAR
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_audit(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                NOOPERATOR, 
                SUM(TTLDSKITEM) AS diskon_item, 
                SUM(RPDISKON) AS diskon_global,
                SUM(TTLVOID) AS total_void,
                SUM(TTLJUALRFN) AS total_refund
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY NOOPERATOR
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_shift(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT NOMORKASSA, NOOPERATOR, SHIFT, COUNT(NOFAKTUR), SUM(TOTALJUAL) 
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            GROUP BY NOMORKASSA, NOOPERATOR, SHIFT
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_rekonsiliasi(tgl_mulai, tgl_akhir):
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
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_daftar_refund(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.NOFAKTUR, h.TGLJUAL, p.KODEBRG, p.NAMABRG, p.QTY, p.HARGANET
            FROM pjualpos p
            JOIN hjualpos h ON p.NOFAKTUR = h.NOFAKTUR
            WHERE h.TGLJUAL BETWEEN ? AND ? AND (p.QTY < 0 OR p.VOID = 1)
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_best_seller(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Untuk best seller, kita ambil qty dan total netto. 
        # Gunakan CAST untuk memastikan QTY jadi integer (jika memang desimal)
        cursor.execute("""
            SELECT p.KODEBRG, p.NAMABRG, SUM(p.QTY), SUM(p.HARGANET) 
            FROM pjualpos p 
            JOIN hjualpos h ON p.NOFAKTUR = h.NOFAKTUR
            WHERE h.TGLJUAL BETWEEN ? AND ? AND p.QTY > 0
            GROUP BY p.KODEBRG, p.NAMABRG 
            ORDER BY SUM(p.QTY) DESC LIMIT 50
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()

def get_laporan_per_nota(tgl_mulai, tgl_akhir):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Gunakan TOTALJUAL untuk Netto
        cursor.execute("""
            SELECT NOFAKTUR, TGLJUAL, JAMJUAL, NOOPERATOR, TOTALJUAL 
            FROM hjualpos 
            WHERE TGLJUAL BETWEEN ? AND ? 
            ORDER BY TGLJUAL DESC, NOFAKTUR DESC
            LIMIT 100
        """, (tgl_mulai, tgl_akhir))
        return cursor.fetchall()
    finally:
        conn.close()