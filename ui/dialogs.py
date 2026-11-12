import tkinter as tk
from config.theme import (
    BG_PANEL,
    BG_PANEL_SOFT,
    BG_SHADOW,
    BG_INPUT,
    BG_INPUT_FG,
    FG_UTAMA,
    FG_SEKUNDER,
    FG_AKSEN,
    FG_KUNING,
    FG_MERAH,
    FG_SUKSES,
    FG_ABU,
    FONT_JUDUL,
    FONT_BESAR,
    FONT_TOTAL,
    FONT_KEMBALI,
    FONT_KECIL
)
from ui.components import buat_dual_shadow_panel

def show_overlay(parent=None):
    """
    Hook overlay aktif (kompatibilitas sistem overlay).
    """
    pass

def hide_overlay(overlay_frame=None, root=None, refs=None):
    """
    Menutup frame overlay dan mengembalikan fokus keyboard ke widget utama.
    """
    if overlay_frame and overlay_frame.winfo_exists():
        try:
            overlay_frame.grab_release()
        except Exception:
            pass
        overlay_frame.destroy()
    target_root = root or (refs.get("root") if refs else None)
    entry = refs.get("entry_barcode") if refs else None
    if target_root and entry and entry.winfo_exists():
        try:
            target_root.after(10, lambda: entry.focus())
        except Exception:
            pass

# ============================================================
# DIALOG: info_kk — Soft, no border, dual shadow (BLOCKING)
# ============================================================
def info_kk(root, judul, pesan, callback=None, refs=None):
    """
    Dialog notifikasi popup di tengah layar dengan dual shadow.
    Sifat: Blocking (wait_window).
    """
    judul_upper = judul.upper()
    if "ERROR" in judul_upper or "GAGAL" in judul_upper or "SALAH" in judul_upper:
        ikon, warna_ikon = "✕", FG_MERAH
    elif "PERHATIAN" in judul_upper or "WARNING" in judul_upper:
        ikon, warna_ikon = "⚠", FG_KUNING
    elif "SUKSES" in judul_upper or "BERHASIL" in judul_upper:
        ikon, warna_ikon = "✓", FG_SUKSES
    else:
        ikon, warna_ikon = "ℹ", FG_AKSEN
    
    # [FIX] Cari window induk tertinggi (Main Window) agar popup tidak tertutup dialog lain
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, container = buat_dual_shadow_panel(
        parent, width=380, height=180, relx=0.5, rely=0.5, anchor="center"
    )
    
    try:
        container.grab_set()
    except Exception:
        pass
    
    frame_header = tk.Frame(container, bg=BG_PANEL)
    frame_header.pack(pady=(20, 5))
    tk.Label(frame_header, text=ikon,
             font=("Segoe UI", 32, "bold"),
             bg=BG_PANEL, fg=warna_ikon).pack()
    
    tk.Label(container, text=judul_upper, font=FONT_JUDUL,
             bg=BG_PANEL, fg=warna_ikon).pack(pady=(0, 5))
    
    tk.Label(container, text=pesan, font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA, wraplength=340, justify="center").pack(pady=5)
    
    btn_ok = tk.Label(container, text="  OK  (ENTER)  ", font=FONT_BESAR,
                      bg=BG_PANEL_SOFT, fg=FG_AKSEN, pady=8, padx=24,
                      highlightbackground=FG_AKSEN, highlightthickness=1)
    btn_ok.pack(pady=(10, 15))
    
    def tutup(event=None):
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if callback:
            callback()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
        
    # [FIX ESC] Bind langsung ke lambda dengan return break
    def _on_esc(e=None):
        tutup()
        return "break"

    container.bind("<Return>", tutup)
    container.bind("<space>", tutup)
    container.bind("<Escape>", _on_esc)
    btn_ok.bind("<Escape>", _on_esc)
    btn_ok.bind("<Return>", tutup)
    btn_ok.bind("<Button-1>", tutup)
    
    # Paksa fokus masuk ke container
    container.focus_set()
    container.focus_force()
    
    parent.wait_window(container)

# ============================================================
# DIALOG: konfirmasi_kk — Soft, no border (BLOCKING)
# ============================================================
def konfirmasi_kk(root, judul, pesan, callback_ya=None, callback_tidak=None,
                  label_ya="YA", label_tidak="BATAL", refs=None):
    """
    Dialog konfirmasi dua opsi (YA / BATAL) berbasis keyboard di tengah layar.
    Sifat: Blocking (wait_window).
    """
    # [FIX] Cari window induk tertinggi
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, container = buat_dual_shadow_panel(
        parent, width=420, height=190, relx=0.5, rely=0.5, anchor="center"
    )
    
    try:
        container.grab_set()
    except Exception:
        pass
    
    tk.Label(container, text=judul.upper(), font=FONT_JUDUL,
             bg=BG_PANEL, fg=FG_KUNING).pack(pady=(20, 8))
    tk.Label(container, text=pesan, font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA, wraplength=380, justify="center").pack(pady=8)
    
    frame_btn = tk.Frame(container, bg=BG_PANEL)
    frame_btn.pack(pady=15)
    
    selected_btn = tk.IntVar(value=0)
    
    btn_ya = tk.Label(frame_btn, text=f"  {label_ya}  ", font=FONT_BESAR,
                      bg=BG_PANEL_SOFT, fg=FG_AKSEN, width=12, pady=8,
                      highlightbackground=FG_AKSEN, highlightthickness=1)
    btn_ya.pack(side="left", padx=8)
    btn_tidak = tk.Label(frame_btn, text=f"  {label_tidak}  ", font=FONT_BESAR,
                         bg=BG_INPUT, fg=FG_UTAMA, width=12, pady=8,
                         highlightbackground=FG_ABU, highlightthickness=1)
    btn_tidak.pack(side="left", padx=8)
    
    def update_buttons():
        if selected_btn.get() == 0:
            btn_ya.config(bg=BG_PANEL_SOFT, fg=FG_AKSEN,
                          highlightbackground=FG_AKSEN, highlightthickness=1)
            btn_tidak.config(bg=BG_INPUT, fg=FG_UTAMA,
                             highlightbackground=FG_ABU, highlightthickness=1)
        else:
            btn_ya.config(bg=BG_INPUT, fg=FG_UTAMA,
                          highlightbackground=FG_ABU, highlightthickness=1)
            btn_tidak.config(bg=BG_PANEL_SOFT, fg=FG_AKSEN,
                             highlightbackground=FG_AKSEN, highlightthickness=1)
            
    tk.Label(container, text="← / →  pilih     ENTER  konfirmasi     ESC  batal",
             font=FONT_KECIL, bg=BG_PANEL, fg=FG_ABU).pack(pady=(0, 12))
    
    def pilih_kiri(event=None):
        selected_btn.set(0)
        update_buttons()
        return "break"
        
    def pilih_kanan(event=None):
        selected_btn.set(1)
        update_buttons()
        return "break"
    
    def konfirmasi(event=None):
        is_ya = (selected_btn.get() == 0)
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if is_ya and callback_ya:
            callback_ya()
        elif not is_ya and callback_tidak:
            callback_tidak()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
        
    def batal(event=None):
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if callback_tidak:
            callback_tidak()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
        
    container.bind("<Left>", pilih_kiri)
    container.bind("<Right>", pilih_kanan)
    container.bind("<Return>", konfirmasi)
    container.bind("<Escape>", batal)
    
    btn_ya.bind("<Escape>", batal)
    btn_tidak.bind("<Escape>", batal)
    btn_ya.bind("<Return>", konfirmasi)
    btn_tidak.bind("<Return>", konfirmasi)
    
    update_buttons()
    container.focus_set()
    container.focus_force()
    
    parent.wait_window(container)

# ============================================================
# DIALOG: input_kk — Dialog input kecil di tengah layar (BLOCKING)
# ============================================================
def input_kk(root, judul, prompt, default_val="", callback=None, refs=None):
    """
    Dialog input teks kecil di tengah layar dengan return value atau callback.
    """
    # [FIX] Cari window induk tertinggi
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, container = buat_dual_shadow_panel(
        parent, width=420, height=180, relx=0.5, rely=0.5, anchor="center"
    )
    
    try:
        container.grab_set()
    except Exception:
        pass
        
    tk.Label(container, text=judul.upper(), font=FONT_JUDUL,
             bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(18, 5))
    tk.Label(container, text=prompt, font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA).pack(pady=4)
             
    entry = tk.Entry(container, font=FONT_BESAR, width=24,
                     bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN,
                     relief="flat", bd=6, highlightbackground=FG_AKSEN, highlightthickness=1)
    entry.pack(pady=8)
    if default_val:
        entry.insert(0, str(default_val))
        entry.selection_range(0, tk.END)
    entry.focus_set()
    
    hasil = [None]
    
    def simpan(event=None):
        val = entry.get().strip()
        hasil[0] = val
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if callback:
            callback(val)
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
            
    def batal(event=None):
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
            
    entry.bind("<Return>", simpan)
    entry.bind("<Escape>", batal)
    container.bind("<Escape>", batal)
    
    container.focus_force()
    entry.focus_force()
    
    parent.wait_window(container)
    return hasil[0]

# ============================================================
# DIALOG: tampilkan_kembalian — Overlay struk / kembalian (BLOCKING)
# ============================================================
def tampilkan_kembalian(root, bayar, kembali, total=0, refs=None):
    """
    Overlay hasil transaksi / retur lengkap dengan jumlah pembayaran dan kembalian.
    Sifat: Blocking (wait_window).
    """
    # [FIX] Cari window induk tertinggi
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, container = buat_dual_shadow_panel(
        parent, width=640, height=420, relx=0.5, rely=0.5, anchor="center"
    )
    
    try:
        container.grab_set()
    except Exception:
        pass
    
    if total < 0:
        judul_sukses = "✓  RETUR BARANG SUKSES"
        warna_judul = FG_MERAH
    else:
        judul_sukses = "✓  TRANSAKSI SUKSES"
        warna_judul = FG_SUKSES
        
    tk.Label(container, text=judul_sukses, font=("Segoe UI", 20, "bold"),
             bg=BG_PANEL, fg=warna_judul).pack(pady=(25, 12))
    tk.Frame(container, bg=FG_ABU, height=2).pack(fill="x", padx=45, pady=8)
    
    frame_detail = tk.Frame(container, bg=BG_PANEL)
    frame_detail.pack(pady=8, padx=45, fill="x")
    
    row1 = tk.Frame(frame_detail, bg=BG_PANEL)
    row1.pack(fill="x", pady=4)
    tk.Label(row1, text="TOTAL", font=FONT_BESAR, bg=BG_PANEL, fg=FG_SEKUNDER, width=15, anchor="w").pack(side="left")
    warna_total = FG_MERAH if total < 0 else FG_KUNING
    tk.Label(row1, text=f"Rp {total:,.0f}".replace(",", "."), font=FONT_BESAR, bg=BG_PANEL, fg=warna_total, anchor="e").pack(side="right")
    
    row2 = tk.Frame(frame_detail, bg=BG_PANEL)
    row2.pack(fill="x", pady=4)
    tk.Label(row2, text="DIBAYAR", font=FONT_BESAR, bg=BG_PANEL, fg=FG_SEKUNDER, width=15, anchor="w").pack(side="left")
    tk.Label(row2, text=f"Rp {bayar:,.0f}".replace(",", "."), font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, anchor="e").pack(side="right")
    
    tk.Frame(container, bg=FG_AKSEN, height=3).pack(fill="x", padx=45, pady=12)
    
    frame_kembali = tk.Frame(container, bg=BG_PANEL)
    frame_kembali.pack(pady=5)
    if total < 0:
        tk.Label(frame_kembali, text="KASIR BAYAR", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_MERAH).pack(pady=3)
        tk.Label(frame_kembali, text=f"Rp {abs(total):,.0f}".replace(",", "."), font=FONT_KEMBALI, bg=BG_PANEL, fg=FG_MERAH).pack(pady=8)
    else:
        tk.Label(frame_kembali, text="KEMBALIAN", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_KUNING).pack(pady=3)
        tk.Label(frame_kembali, text=f"Rp {kembali:,.0f}".replace(",", "."), font=FONT_KEMBALI, bg=BG_PANEL, fg=FG_SUKSES).pack(pady=8)
        
    tk.Frame(container, bg=FG_ABU, height=2).pack(fill="x", padx=45, pady=12)
    tk.Label(container, text="Tekan tombol APA SAJA untuk tutup", font=FONT_BESAR, bg=BG_PANEL, fg=FG_KUNING).pack(pady=(3, 18))
    
    def tutup(event=None):
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
            
    container.bind("<Key>", tutup)
    container.bind("<Return>", tutup)
    container.bind("<Escape>", tutup)
    container.bind("<space>", tutup)
    container.bind("<Button-1>", tutup)
    container.bind("<Button-3>", tutup)
    container.focus_set()
    container.focus_force()
    
    parent.wait_window(container)
