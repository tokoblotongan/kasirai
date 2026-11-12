import sqlite3
from config.settings import DB_PATH

def get_connection(db_path=None):
    """
    Membuka dan mengembalikan koneksi SQLite3.
    Jika db_path tidak dispesifikasikan, menggunakan DB_PATH dari settings.
    """
    path = db_path if db_path is not None else DB_PATH
    return sqlite3.connect(path)

# Alias kompatibilitas
get_koneksi = get_connection

def init_tabel_passw(conn=None):
    """
    Inisialisasi tabel PASSW (user dan password kasir/admin).
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PASSW (
                NOPEGAWAI TEXT PRIMARY KEY,
                PASSWORD TEXT,
                NAMA_USER TEXT,
                GROUP_USER TEXT
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM PASSW")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO PASSW VALUES (?, ?, ?, ?)",
                ("1", "1", "Administrator", "ADMIN")
            )
        conn.commit()
    except Exception as e:
        print(f"Error init PASSW: {e}")
    finally:
        if close_after:
            conn.close()

def init_tabel_pending(conn=None):
    """
    Inisialisasi tabel pending (transaksi hold/tertunda).
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pembeli TEXT,
                data_keranjang TEXT,
                tanggal TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error init pending: {e}")
    finally:
        if close_after:
            conn.close()

def init_tabel_transaksi(conn=None):
    """
    Inisialisasi tabel hjualpos (header) dan pjualpos (detail penjualan).
    Menjamin ketersediaan semua kolom yang dibutuhkan di hjualpos.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hjualpos (
                NOFAKTUR TEXT PRIMARY KEY,
                TGLJUAL TEXT
            )
        """)
        cursor.execute("PRAGMA table_info(hjualpos)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        required_hjualpos = {
            'TGLJUAL': 'TEXT',
            'JAMJUAL': 'TEXT',
            'SHIFT': 'TEXT',
            'NOMORKASSA': 'TEXT',
            'NOOPERATOR': 'TEXT',
            'TOTALJUAL': 'REAL',
            'BAYAR': 'REAL',
            'RPKEMBALI': 'REAL',
            'CARABAYAR': 'TEXT',
            'MEMBER': 'TEXT',
            'RPCARD': 'REAL',
            'CARD': 'REAL'
        }
        for col_name, col_type in required_hjualpos.items():
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE hjualpos ADD COLUMN {col_name} {col_type}")
                
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pjualpos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                SHIFT TEXT,
                NOMORKASSA TEXT,
                NOFAKTUR TEXT,
                NO INTEGER,
                KODEBRG TEXT,
                NAMABRG TEXT,
                HARGAJUAL REAL,
                DISKON REAL,
                DISKONRP REAL,
                DISKMEMBERP REAL,
                DISKGLBAL REAL,
                DISKMULTI REAL,
                QTY REAL,
                SATUANJUAL TEXT,
                ISTPHARGA REAL,
                NAMABRGNET TEXT,
                NOMORNOTA TEXT,
                TGLJUAL TEXT,
                TGLJAMJUAL TEXT,
                JAMJUAL TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error init transaksi: {e}")
    finally:
        if close_after:
            conn.close()

def init_tabel_barang(conn=None):
    """
    Inisialisasi tabel barang (master produk).
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                BARANG TEXT PRIMARY KEY,
                BARKODE TEXT,
                NAMABRG TEXT,
                SATUAN TEXT,
                HARGABELI REAL,
                HARGAJUAL REAL,
                STOKTOKO REAL
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error init barang: {e}")
    finally:
        if close_after:
            conn.close()

def init_database(db_path=None):
    """
    Menjalankan seluruh inisialisasi tabel dalam satu pemanggilan:
    - PASSW (user & password kasir/admin)
    - pending (transaksi tertunda / hold)
    - 14 tabel lengkap sesuai roadmap schema.sql (migrasi FoxPro 2.6)
    """
    import os
    conn = get_connection(db_path)
    try:
        init_tabel_passw(conn)
        init_tabel_pending(conn)
        
        # Eksekusi schema.sql jika tersedia
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        else:
            init_tabel_transaksi(conn)
            init_tabel_barang(conn)

        # Pastikan kolom kenyamanan (JAMJUAL, RPKEMBALI) tersedia untuk laporan & checkout
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(hjualpos)")
        h_cols = [c[1] for c in cursor.fetchall()]
        if "JAMJUAL" not in h_cols:
            cursor.execute("ALTER TABLE hjualpos ADD COLUMN JAMJUAL TEXT")
        if "RPKEMBALI" not in h_cols:
            cursor.execute("ALTER TABLE hjualpos ADD COLUMN RPKEMBALI REAL DEFAULT 0")
        conn.commit()
    except Exception as e:
        print(f"Error executing schema: {e}")
    finally:
        conn.close()
