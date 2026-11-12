import tkinter as tk
from config.theme import (
    BG_PANEL,
    BG_INPUT,
    BG_INPUT_FG,
    FG_UTAMA,
    FG_AKSEN,
    FG_KUNING,
    FG_MERAH,
    FG_SUKSES,
    FG_ABU,
    FONT_JUDUL,
    FONT_BESAR,
    FONT_KECIL
)

def info_bantuan(event=None, root=None, refs=None, state=None):
    """
    STUB: Informasi bantuan hotkey POS (F1).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Bantuan (F1) belum aktif.", refs=refs)
    return "break"

def open_plu(event=None, root=None, refs=None, state=None):
    """
    STUB: Open Penjualan PLU Manual (F3).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Open PLU (F3) belum aktif.", refs=refs)
    return "break"

def ubah_harga_transaksi(event=None, root=None, refs=None, state=None):
    """
    STUB: Ubah Harga Transaksi (F4).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Ubah Harga (F4) belum aktif.", refs=refs)
    return "break"

def diskon_item_persen(event=None, root=None, refs=None, state=None):
    """
    STUB: Diskon Item Persen (F8).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Diskon Item Persen (F8) belum aktif.", refs=refs)
    return "break"

def diskon_per_item(event=None, root=None, refs=None, state=None):
    """
    Implementasi Diskon Per Item Rp / % (F9) - Desain Baru Dua Kolom Interaktif.
    Kursor awal di kolom Angka (Rp). Menampilkan Harga Lama & Harga Baru.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    from handlers.keranjang import perbarui_tampilan_keranjang
    
    tree = refs.get("tree") if refs else None
    if not tree:
        return "break"
        
    sel = tree.selection()
    if not sel:
        info_kk(root, "Perhatian", "Pilih item dulu di tabel!", refs=refs)
        return "break"
        
    idx = tree.index(sel[0])
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return "break"
        
    item = keranjang[idx]
    harga = item["harga"]
    qty = item["qty"]
    
    # [FIX] Variabel pelacak kolom yang terakhir diedit
    mode_edit = {"kolom": "rp"}
    
    # Ukuran dialog disesuaikan
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=500, height=460, relx=0.5, rely=0.5, anchor="center"
    )
    try:
        dlg.grab_set()
    except Exception:
        pass
        
    main_frame = tk.Frame(dlg, bg=BG_PANEL)
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)
    
    # 1. Judul
    tk.Label(main_frame, text="DISKON PER ITEM (F9)", font=FONT_JUDUL,
             bg=BG_PANEL, fg=FG_KUNING).pack(pady=(0, 15))
             
    # 2. Panel Info
    frame_info = tk.Frame(main_frame, bg=BG_INPUT, highlightthickness=0)
    frame_info.pack(fill="x", pady=(0, 15))
    
    tk.Label(frame_info, text=item["nama"][:40].upper(), font=FONT_BESAR,
             bg=BG_INPUT, fg=FG_UTAMA, anchor="w").pack(fill="x", padx=15, pady=(10, 0))
             
    frame_row2 = tk.Frame(frame_info, bg=BG_INPUT)
    frame_row2.pack(fill="x", padx=15, pady=(0, 10))
    
    # Harga Lama dan Qty ditampilkan eksplisit
    tk.Label(frame_row2, text=f"Harga: Rp {harga:,.0f}".replace(",", "."),
             font=FONT_BESAR, bg=BG_INPUT, fg=FG_AKSEN, anchor="w").pack(side="left")
    tk.Label(frame_row2, text=f"Qty: {qty:g}",
             font=FONT_BESAR, bg=BG_INPUT, fg=FG_AKSEN, anchor="e").pack(side="right")
             
    # 3. Label Input
    tk.Label(main_frame, text="MASUKKAN DISKON :", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA, anchor="w").pack(fill="x", pady=(0, 5))
             
    # 4. Dua Kolom Berdampingan
    frame_cols = tk.Frame(main_frame, bg=BG_PANEL)
    frame_cols.pack(fill="x", pady=(0, 15))
    
    # --- Kolom Kiri (Persen) ---
    frame_kiri = tk.Frame(frame_cols, bg=BG_PANEL)
    frame_kiri.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    tk.Label(frame_kiri, text="Persen %", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN).pack()
    tk.Label(frame_kiri, text="F4", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(2, 5))
             
    e_pct = tk.Entry(frame_kiri, font=FONT_BESAR, width=10,
                     bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN,
                     justify="center", relief="flat", bd=6,
                     highlightbackground=FG_AKSEN, highlightthickness=1)
    e_pct.pack(fill="x")
    
    # --- Kolom Kanan (Angka) ---
    frame_kanan = tk.Frame(frame_cols, bg=BG_PANEL)
    frame_kanan.pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    tk.Label(frame_kanan, text="Angka", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN).pack()
    tk.Label(frame_kanan, text="F5", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(2, 5))
             
    e_rp = tk.Entry(frame_kanan, font=FONT_BESAR, width=10,
                    bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN,
                    justify="center", relief="flat", bd=6,
                    highlightbackground=FG_AKSEN, highlightthickness=1)
    e_rp.pack(fill="x")
    
    # 5. Baris "Perubahan" & "Harga Baru"
    frame_perubahan = tk.Frame(main_frame, bg=BG_PANEL)
    frame_perubahan.pack(fill="x", pady=(0, 5))
    
    tk.Label(frame_perubahan, text="Perubahan :", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN, width=12, anchor="w").pack(side="left")
             
    e_perubahan = tk.Entry(frame_perubahan, font=FONT_BESAR,
                           bg=BG_INPUT, fg=FG_KUNING, insertbackground=FG_AKSEN,
                           justify="center", relief="flat", bd=6,
                           highlightbackground=FG_AKSEN, highlightthickness=1,
                           state="readonly",
                           readonlybackground=BG_INPUT)
    e_perubahan.pack(side="left", fill="x", expand=True)
    
    frame_baru = tk.Frame(main_frame, bg=BG_PANEL)
    frame_baru.pack(fill="x", pady=(0, 15))
    
    tk.Label(frame_baru, text="Harga Baru :", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_SUKSES, width=12, anchor="w").pack(side="left")
             
    e_baru = tk.Entry(frame_baru, font=FONT_BESAR,
                      bg=BG_INPUT, fg=FG_SUKSES, insertbackground=FG_AKSEN,
                      justify="center", relief="flat", bd=6,
                      highlightbackground=FG_SUKSES, highlightthickness=1,
                      state="readonly",
                      readonlybackground=BG_INPUT)
    e_baru.pack(side="left", fill="x", expand=True)
    
    # 6. Teks kecil
    tk.Label(main_frame, text="ENTER = OK | ESC = BATAL", font=FONT_KECIL,
             bg=BG_PANEL, fg=FG_ABU).pack(pady=(5, 0))
             
    # ============================================================
    # LOGIKA INTERAKSI
    # ============================================================
    
    is_updating = False # Mencegah infinite loop saat sinkronisasi
    
    def hitung_dari_persen(event=None):
        nonlocal is_updating
        mode_edit["kolom"] = "pct"
        if is_updating: return
        is_updating = True
        
        try:
            teks = e_pct.get().strip()
            p = float(teks) if teks else 0.0
            
            diskon_rp = harga * (p / 100.0)
            perubahan = (harga - diskon_rp) * qty
            harga_baru = harga - diskon_rp
            
            e_rp.delete(0, tk.END)
            if teks:
                e_rp.insert(0, f"{diskon_rp:.0f}")
                
            e_perubahan.config(state="normal")
            e_perubahan.delete(0, tk.END)
            e_perubahan.insert(0, f"{perubahan:.0f}".replace(",", "."))
            e_perubahan.config(state="readonly")
            
            e_baru.config(state="normal")
            e_baru.delete(0, tk.END)
            e_baru.insert(0, f"{harga_baru:.0f}".replace(",", "."))
            e_baru.config(state="readonly")
        except ValueError:
            pass
        finally:
            is_updating = False

    def hitung_dari_rp(event=None):
        nonlocal is_updating
        mode_edit["kolom"] = "rp"
        if is_updating: return
        is_updating = True
        
        try:
            teks = e_rp.get().strip()
            r = float(teks) if teks else 0.0
            
            p = (r / harga) * 100.0 if harga > 0 else 0.0
            perubahan = (harga - r) * qty
            harga_baru = harga - r
            
            e_pct.delete(0, tk.END)
            if teks:
                e_pct.insert(0, f"{p:.2f}".rstrip("0").rstrip("."))
                
            e_perubahan.config(state="normal")
            e_perubahan.delete(0, tk.END)
            e_perubahan.insert(0, f"{perubahan:.0f}".replace(",", "."))
            e_perubahan.config(state="readonly")
            
            e_baru.config(state="normal")
            e_baru.delete(0, tk.END)
            e_baru.insert(0, f"{harga_baru:.0f}".replace(",", "."))
            e_baru.config(state="readonly")
        except ValueError:
            pass
        finally:
            is_updating = False

    # Binding KeyRelease untuk Live Calculation
    e_pct.bind("<KeyRelease>", hitung_dari_persen)
    e_rp.bind("<KeyRelease>", hitung_dari_rp)
    
    def fokus_persen(ev=None):
        mode_edit["kolom"] = "pct"
        e_pct.focus_set()
        e_pct.selection_range(0, tk.END)
        return "break"
        
    def fokus_rp(ev=None):
        mode_edit["kolom"] = "rp"
        e_rp.focus_set()
        e_rp.selection_range(0, tk.END)
        return "break"

    def simpan(ev=None):
        try:
            p_str = e_pct.get().strip()
            r_str = e_rp.get().strip()
            
            p = float(p_str) if p_str else 0.0
            r = float(r_str) if r_str else 0.0
            
            # [FIX] Gunakan mode_edit untuk menyimpan HANYA kolom yang terakhir diedit
            if mode_edit["kolom"] == "pct":
                item["diskon_pct"] = round(p, 2)
                item["diskon_rp"] = 0.0
            else:
                item["diskon_rp"] = round(r, 2)
                item["diskon_pct"] = 0.0
            
            perbarui_tampilan_keranjang(root, refs, state)
            
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            
            if tree:
                root.after(10, lambda: tree.focus_set())
        except ValueError:
            info_kk(dlg, "Error", "Masukkan angka yang valid!", refs=refs)
            
    def batal(ev=None):
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
        return "break"
        
    # Binding Enter & ESC
    dlg.bind("<Return>", simpan)
    e_pct.bind("<Return>", simpan)
    e_rp.bind("<Return>", simpan)
    
    dlg.bind("<Escape>", batal)
    e_pct.bind("<Escape>", batal)
    e_rp.bind("<Escape>", batal)
    
    # Hotkey F4 & F5
    dlg.bind("<F4>", fokus_persen)
    e_pct.bind("<F4>", fokus_persen)
    e_rp.bind("<F4>", fokus_persen)
    
    dlg.bind("<F5>", fokus_rp)
    e_pct.bind("<F5>", fokus_rp)
    e_rp.bind("<F5>", fokus_rp)
    
    # Hitung inisialisasi awal (jika ada diskon sebelumnya, tampilkan)
    if item.get("diskon_rp", 0) > 0:
        e_rp.insert(0, f"{item['diskon_rp']:.0f}")
        hitung_dari_rp()
    elif item.get("diskon_pct", 0) > 0:
        e_pct.insert(0, f"{item['diskon_pct']:g}")
        hitung_dari_persen()
    else:
        hitung_dari_rp() # Default tampilkan harga normal
    
    # Fokus awal mendarat di kolom ANGKA (Rp)
    e_rp.focus_set()
    
    return "break"

def buka_laci(event=None, root=None, refs=None, state=None):
    """
    STUB: Buka Laci Kasir (F11).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Buka Laci (F11) belum aktif.", refs=refs)
    return "break"

def copy_struk(event=None, root=None, refs=None, state=None):
    """
    Implementasi Cetak Ulang Struk (F12).
    Mengambil data dari state["transaksi_terakhir"] dan mencetaknya kembali.
    """
    from ui.dialogs import info_kk
    from handlers.print_struk import cetak_struk
    
    transaksi = state.get("transaksi_terakhir") if state else None
    if not transaksi:
        info_kk(root, "Info", "Belum ada transaksi yang bisa dicetak ulang.", refs=refs)
        return "break"
    
    try:
        cetak_struk(
            nomor_nota = transaksi["nomor_nota"],
            keranjang_items = transaksi["keranjang"],
            total = transaksi["total"],
            bayar = transaksi["bayar"],
            kembali = transaksi["kembali"],
            is_retur = transaksi.get("is_retur", False),
            user_id = transaksi.get("user_id"),
            root = root,
            diskon_global_rp = transaksi.get("diskon_global_rp", 0.0),
            diskon_global_persen = transaksi.get("diskon_global_persen", 0.0)
        )
        info_kk(root, "Sukses", "Struk berhasil dicetak ulang.", refs=refs)
    except Exception as e:
        info_kk(root, "Error", f"Gagal cetak ulang: {e}", refs=refs)
    return "break"

def input_nota_manual(event=None, root=None, refs=None, state=None):
    """
    STUB: Input Nomor Nota Manual (/).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Input Nota Manual (/) belum aktif.", refs=refs)
    return "break"

def hapus_transaksi(event=None, root=None, refs=None, state=None):
    """
    STUB: Hapus Seluruh Transaksi (Ctrl+F11).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Hapus Transaksi (Ctrl+F11) belum aktif.", refs=refs)
    return "break"

def set_member(event=None, root=None, refs=None, state=None):
    """
    STUB: Input Member Pelanggan (Shift+F11).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Member (Shift+F11) belum aktif.", refs=refs)
    return "break"

def biaya_tambahan_func(event=None, root=None, refs=None, state=None):
    """
    STUB: Biaya Tambahan (Alt+F11).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Biaya Tambahan (Alt+F11) belum aktif.", refs=refs)
    return "break"

def diskon_global_rp_func(event=None, root=None, refs=None, state=None):
    """
    STUB: Diskon Global Rp (Ctrl+F4).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Diskon Global (Ctrl+F4) belum aktif.", refs=refs)
    return "break"

def cash_out(event=None, root=None, refs=None, state=None):
    """
    STUB: Cash Out Pengeluaran Kasir (Alt+F12).
    """
    from ui.dialogs import info_kk
    info_kk(root, "Info", "Fitur Cash Out (Alt+F12) belum aktif.", refs=refs)
    return "break"

def escape_safety_net(event=None, root=None, refs=None, state=None):
    """
    STUB: Escape Safety Net.
    """
    if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
        refs["entry_barcode"].focus_set()
    return "break"
