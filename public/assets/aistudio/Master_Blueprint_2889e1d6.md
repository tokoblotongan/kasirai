# 📋 MASTER BLUEPRINT: POS KASIR AI V3 - TB.BLOTONGAN
**Untuk AI Agent (Master POS / DeepSeek Coding)**
**Status Proyek:** Fase A (Visual Modern) Selesai, Fase B (Laporan) Sedang Berjalan.

---

## 🎯 1. VISI & FILOSOFI UTAMA
Membangun **POS Kasir AI** untuk toko bangunan TB.BLOTONGAN.
**Slogan:** "Logika POS Lama, Tampilan Modern, Otak AI."
**3 Pilar Utama:**
1. **100% Keyboard-Driven:** Kasir tidak boleh butuh mouse untuk transaksi. Navigasi panah, Tab, Enter, dan Hotkey harus berfungsi sempurna.
2. **Visual Modern (Bukan POS Lama):** Mengadopsi *logika* cepat POS lama, TAPI menggunakan desain UI modern (Dark Mode, Font Inter/Segoe UI). Dilarang meniru visual norak/jadul POS lama.
3. **AI Brain (Fase C):** Integrasi multi-provider AI (Gemini, Groq) untuk analisis bisnis.

---

## 🏗️ 2. ARSITEKTUR & STACK
*   **Bahasa:** Python 3.8+
*   **GUI:** Tkinter (Native, tanpa library eksternal berat).
*   **Database:** SQLite 3 (`data/toko.db`).
*   **Printer:** ESC/POS TM-P58 via `win32print`.
*   **Struktur Folder:**
    *   `config/`: `theme.py` (warna/font), `settings.py` (path DB, identitas toko).
    *   `database/`: `connection.py`, `queries.py` (query SQL).
    *   `ui/`: `main_window.py`, `login.py`, `dialogs.py`, `laporan.py`.
    *   `handlers/`: `keranjang.py`, `checkout.py`, `print_struk.py`, `pending.py`, `aksi_lain.py`.
    *   `data/`: `toko.db`.

---

## 🗄️ 3. SKEMA DATABASE (MIGRASI FOXPRO)
Sistem menggunakan nama tabel asli dari FoxPro 2.6. **WAJIB GUNAKAN NAMA INI DALAM QUERY:**
*   **`barang`**: Master barang (91 kolom). Primary Key: `BARANG`. Stok ada di `STOKTOKO`.
*   **`hjualpos`**: Header penjualan. Primary Key gabungan: `(TGLJUAL, SHIFT, NOMORKASSA, NOFAKTUR)`. Total transaksi ada di `TOTALJUAL`.
*   **`pjualpos`**: Detail penjualan. Foreign Key ke `hjualpos`. Menyimpan `KODEBRG`, `QTY`, `HARGAJUAL`, `DISKONRP`, dll.
*   **`PASSW`**: Tabel login kasir. Primary Key: `NOPEGAWAI`.
*   **`member`**, **`supplier`**, **`hbeli`**, **`pbelli`**, **`kasir`**, **`kartustk`**.
*   *(Catatan: Tabel `shift_logs` belum ada, untuk sementara laporan rekonsiliasi di-skip atau menggunakan data tiruan).*

---

## 🎨 4. ATURAN DESAIN & UI/UX
1.  **Palet Warna Wajib (Dark Mode):**
    *   Background Utama: `#1E1E2E`
    *   Panel/Modal: `#282A36`
    *   Teks Utama: `#F8F8F2`
    *   Aksen (Tombol/Header): `#4F46E5` (Indigo)
    *   Uang Positif: `#50FA7B` (Hijau)
    *   Uang Negatif/Error: `#FF5555` (Merah)
2.  **Font:** `Segoe UI` atau `Inter`. Khusus angka tabel gunakan `Consolas` (Monospaced).
3.  **Tabel:** Wajib menggunakan *Zebra Striping* (baris selang-seling). Kolom uang (`Netto`, `Harga`, `Subtotal`) **WAJIB RATA KANAN**.
4.  **Dialog:** Dilarang fullscreen (kecuali Dashboard Laporan). Gunakan dialog "kecil di tengah" dengan *drop shadow*.
5.  **Navigasi:** Setiap dialog WAJIB memiliki binding `<Escape>` untuk batal/tutup, dan `<Enter>` untuk OK/Proses.

---

## 🔄 5. STATUS PROYEK & ROADMAP
**✅ SELESAI (100%):**
*   Login, keranjang, input barcode, edit qty, void (F2), retur (`-`), diskon item (F9), checkout (`+`), print struk, copy print (F12), pending (F5/F6/F7).
*   Migrasi database dari FoxPro ke SQLite.
*   Alur Fokus: Setelah input barang, fokus otomatis pindah ke Tree (bukan input).
*   Visual Modern: Tema dasar sudah diterapkan (warna, font, layout tabel).

**🔄 SEDANG BERJALAN (FASE B - Laporan):**
*   Dashboard Laporan (Full Screen).
*   Tab 1: Penjualan & Cara Bayar.
*   Tab 2: Audit Kasir (Bruto, Diskon, Void, Refund, Netto).
*   Tab 3: Best Seller.
*   Tab 4: Rekonsiliasi Kas (Pending tabel shift_logs).
*   Tab 5: Per Nota.

**⏳ BELUM (FASE C - AI Brain):**
*   Integrasi Multi-Provider AI (Gemini, Groq).

---

## ⚠️ 6. PELAJARAN PENTING (JANGAN ULANGI BUG INI!)
1.  **Circular Import:** File `handlers/__init__.py` WAJIB KOSONG. Import antar file `handlers` dan `ui.dialogs` harus dilakukan **di dalam fungsi**, bukan di *top-level file*.
2.  **Binding Global Bocor:** Hotkey `+`, `-`, `/`, `*` di `root.bind` akan memblokir karakter tersebut di Entry. **Solusi:** Selalu cek `root.focus_get()` sebelum mengeksekusi hotkey.
3.  **ESC Tidak Berfungsi:** Dialog Toplevel sering tidak menerima event ESC. **Solusi:** Panggil `dlg.focus_force()` setelah `grab_set()`, dan bind `<Escape>` langsung ke Toplevel dan widget utamanya. Kembalikan `"break"`.
4.  **Nomor Nota Bentrok:** Jangan pakai `state["nomor_nota"]` lama. Selalu panggil `generate_nomor_nota(tgl)` tepat sebelum menyimpan ke database.
5.  **Query Laporan Membengkak:** Jangan pernah melakukan `JOIN` antara `hjualpos` dan `pjualpos` saat menghitung `SUM(TOTALJUAL)`. Akibatnya angka akan terlipat ganda. Hitung total header dari `hjualpos` saja.
6.  **Floating Point:** Saat menyimpan diskon, simpan sebagai `integer` atau gunakan `round()` untuk mencegah error desimal (misal 1000 menjadi 999.9999).

---

## 📜 7. ATURAN KOMUNIKASI UNTUK AI AGENT (DC2)
*   **Tugas:** Eksekusi kode berdasarkan brief. Jangan berimprovisasi di luar brief.
*   **Format Output:** Selalu kirim file LENGKAP (`=== FILE: nama.py ===`). Jangan kirim potongan kode.
*   **Larangan:** Jangan refactor fungsi yang sudah jalan. Jangan ubah desain UI tanpa instruksi.
*   **Jika Ragu:** Tanya Andro/Master POS sebelum mengeksekusi.

---
**Dokumen ini adalah sumber kebenaran (Single Source of Truth). Segala instruksi di luar dokumen ini harus dikonfirmasi ulang.**