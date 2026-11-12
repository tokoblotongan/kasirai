import tkinter as tk
import json
from tkinter import ttk
from datetime import datetime
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
    FONT_KECIL,
    BG_TABLE_ALT,
    BG_TABLE_SEL,
    BG_PANEL_SOFT
)

def set_pending(event=None, root=None, refs=None, state=None):
    """
    Menyimpan transaksi tertunda (F5). KHUSUS MEMBUAT PENDING.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    from database.queries import simpan_pending
    
    keranjang = state.get("keranjang", [])
    if not keranjang:
        info_kk(root, "Perhatian", "Keranjang kosong, tidak ada yang bisa di-pending.", refs=refs)
        return "break"
        
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        parent, width=400, height=200, relx=0.5, rely=0.5, anchor="center"
    )
    
    # [FIX] Paksa fokus ke dialog agar event keyboard tertangkap
    try:
        dlg.grab_set()
        dlg.focus_force()
    except Exception:
        pass
        
    tk.Label(dlg, text="SIMPAN TRANSAKSI (F5)", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_KUNING).pack(pady=(15, 10))
    tk.Label(dlg, text="Nama Pelanggan (opsional):", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(pady=5)
    
    e_nama = tk.Entry(dlg, font=FONT_BESAR, width=25, bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_nama.pack(pady=5)
    e_nama.focus()
    
    def simpan(ev=None):
        nama = e_nama.get().strip() or "Tanpa Nama"
        
        data_to_save = {
            "keranjang": keranjang,
            "diskon_global_rp": state.get("diskon_global_rp", 0.0),
            "diskon_global_persen": state.get("diskon_global_persen", 0.0),
            "biaya_tambahan": state.get("biaya_tambahan", 0.0)
        }
        
        try:
            simpan_pending(nama, data_to_save)
            
            state["keranjang"] = []
            state["diskon_global_rp"] = 0.0
            state["diskon_global_persen"] = 0.0
            state["biaya_tambahan"] = 0.0
            
            from handlers.keranjang import perbarui_tampilan_keranjang
            perbarui_tampilan_keranjang(root, refs, state)
            
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            
            info_kk(parent, "Sukses", f"Transaksi '{nama}' berhasil disimpan ke Pending.", refs=refs)
            
            if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
                parent.after(10, lambda: refs["entry_barcode"].focus())
        except Exception as e:
            info_kk(dlg, "Error Database", f"Gagal menyimpan pending: {e}", refs=refs)
            
    def batal(ev=None):
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
            
    e_nama.bind("<Return>", simpan)
    
    # [FIX] Bind ESC di Entry dan di level Dialog
    e_nama.bind("<Escape>", batal)
    dlg.bind("<Escape>", batal)
    
    parent.wait_window(dlg)
    return "break"

def call_pending(event=None, root=None, refs=None, state=None):
    """
    Memanggil kembali transaksi tertunda (F6). KHUSUS MEMANGGIL.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    from database.queries import load_semua_pending, ambil_pending
    from handlers.keranjang import perbarui_tampilan_keranjang
    
    try:
        rows = load_semua_pending()
    except Exception as e:
        info_kk(root, "Error Database", f"Gagal memuat data pending: {e}", refs=refs)
        return "break"
        
    if not rows:
        info_kk(root, "Info", "Tidak ada transaksi tertunda.", refs=refs)
        return "break"
        
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        parent, width=650, height=400, relx=0.5, rely=0.5, anchor="center"
    )
    try:
        dlg.grab_set()
        dlg.focus_force()
    except Exception:
        pass
        
    tk.Label(dlg, text="PILIH TRANSAKSI PENDING (F6)", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_KUNING).pack(pady=(15, 10))
    
    frame_tabel = tk.Frame(dlg, bg=BG_PANEL)
    frame_tabel.pack(fill="both", expand=True, padx=20, pady=10)
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pending.Treeview.Heading", font=FONT_KECIL, background=BG_INPUT, foreground=FG_AKSEN, borderwidth=0)
    style.configure("Pending.Treeview", font=FONT_KECIL, rowheight=30, background=BG_PANEL, foreground=FG_UTAMA, fieldbackground=BG_PANEL, borderwidth=0)
    style.map("Pending.Treeview", background=[("selected", BG_TABLE_SEL)], foreground=[("selected", "#E8ECF5")])
    
    columns = ("id", "nama", "tgl", "total")
    tree = ttk.Treeview(frame_tabel, columns=columns, show="headings", style="Pending.Treeview", height=8)
    
    tree.heading("id", text="ID")
    tree.heading("nama", text="NAMA PELANGGAN")
    tree.heading("tgl", text="TANGGAL")
    tree.heading("total", text="TOTAL ITEM")
    
    tree.column("id", width=50, anchor="center")
    tree.column("nama", width=250, anchor="w")
    tree.column("tgl", width=180, anchor="center")
    tree.column("total", width=100, anchor="center")
    tree.pack(fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(frame_tabel, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.config(yscrollcommand=scrollbar.set)
    
    for row in rows:
        id_p = row[0]
        nama_p = row[1]
        tgl_p = row[2]
        json_str = row[3]
        
        total_item = 0
        try:
            data_keranjang = json.loads(json_str)
            if isinstance(data_keranjang, dict):
                list_barang = data_keranjang.get("keranjang", [])
            else:
                list_barang = data_keranjang
                
            total_item = sum(float(item.get("qty", 0)) for item in list_barang)
        except Exception:
            total_item = "-"
            
        tree.insert("", "end", iid=str(id_p), values=(id_p, nama_p, tgl_p, f"{total_item:g}"))
        
    def panggil(ev=None):
        sel = tree.selection()
        if not sel:
            return
        id_terpilih = int(sel[0])
        
        try:
            data_row = ambil_pending(id_terpilih)
            if not data_row:
                info_kk(dlg, "Error", "Data pending tidak ditemukan (mungkin sudah dihapus).", refs=refs)
                return
                
            json_str = data_row[0]
            data = json.loads(json_str)
            
            if isinstance(data, dict):
                state["keranjang"] = data.get("keranjang", [])
                state["diskon_global_rp"] = data.get("diskon_global_rp", 0.0)
                state["diskon_global_persen"] = data.get("diskon_global_persen", 0.0)
                state["biaya_tambahan"] = data.get("biaya_tambahan", 0.0)
            else:
                state["keranjang"] = data
                state["diskon_global_rp"] = 0.0
                state["diskon_global_persen"] = 0.0
                state["biaya_tambahan"] = 0.0
            
            perbarui_tampilan_keranjang(root, refs, state)
            
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            
            info_kk(parent, "Sukses", "Transaksi pending berhasil dipanggil kembali.", refs=refs)
            
            if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
                parent.after(10, lambda: refs["entry_barcode"].focus())
                
        except Exception as e:
            info_kk(dlg, "Error", f"Gagal memanggil pending: {e}", refs=refs)
            
    def batal(ev=None):
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
            
    def _on_esc(e=None):
        return batal()
        
    def _tab_next(ev=None):
        tree.focus_set()
        return "break"
            
    tree.bind("<Return>", panggil)
    tree.bind("<Double-1>", panggil)
    tree.bind("<Tab>", _tab_next)
    
    dlg.bind("<Escape>", _on_esc)
    tree.bind("<Escape>", _on_esc)
    
    children = tree.get_children()
    if children:
        tree.selection_set(children[0])
        tree.focus(children[0])
        
    dlg.focus_force()
    tree.focus_set()
    
    parent.wait_window(dlg)
    return "break"

def clear_pending(event=None, root=None, refs=None, state=None):
    """
    Menghapus transaksi tertunda (F7) secara selektif. KHUSUS DELETE.
    """
    from ui.dialogs import info_kk
    from database.queries import load_semua_pending, hapus_pending
    from ui.components import buat_dual_shadow_panel
    
    try:
        rows = load_semua_pending()
    except Exception as e:
        info_kk(root, "Error Database", f"Gagal memuat data pending: {e}", refs=refs)
        return "break"
        
    if not rows:
        info_kk(root, "Info", "Tidak ada transaksi tertunda.", refs=refs)
        return "break"
        
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    # [FIX] Menambah tinggi dialog agar tidak terpotong
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        parent, width=550, height=420, relx=0.5, rely=0.5, anchor="center"
    )
    try:
        dlg.grab_set()
        dlg.focus_force()
    except Exception:
        pass
    
    tk.Label(dlg, text="HAPUS PENDING (F7)", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_MERAH).pack(pady=(15, 5))
    tk.Label(dlg, text="Pilih data lalu tekan [DELETE] untuk menghapus.", font=FONT_KECIL, bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(0, 5))
    
    frame_tabel = tk.Frame(dlg, bg=BG_PANEL)
    frame_tabel.pack(fill="both", expand=True, padx=20, pady=5)
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("ListPending.Treeview.Heading", font=FONT_KECIL, background=BG_INPUT, foreground=FG_AKSEN, borderwidth=0)
    style.configure("ListPending.Treeview", font=FONT_KECIL, rowheight=30, background=BG_PANEL, foreground=FG_UTAMA, fieldbackground=BG_PANEL, borderwidth=0)
    style.map("ListPending.Treeview", background=[("selected", BG_TABLE_SEL)], foreground=[("selected", "#E8ECF5")])
    
    columns = ("id", "nama", "tgl")
    tree = ttk.Treeview(frame_tabel, columns=columns, show="headings", style="ListPending.Treeview", height=6)
    
    tree.heading("id", text="ID")
    tree.heading("nama", text="NAMA PELANGGAN")
    tree.heading("tgl", text="TANGGAL")
    
    tree.column("id", width=50, anchor="center")
    tree.column("nama", width=250, anchor="w")
    tree.column("tgl", width=180, anchor="center")
    tree.pack(fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(frame_tabel, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.config(yscrollcommand=scrollbar.set)
    
    for row in rows:
        id_p = row[0]
        nama_p = row[1]
        tgl_p = row[2]
        tree.insert("", "end", iid=str(id_p), values=(id_p, nama_p, tgl_p))
        
    def lakukan_hapus(ev=None):
        sel = tree.selection()
        if not sel:
            info_kk(dlg, "Perhatian", "Pilih data yang akan dihapus!", refs=refs)
            return
        
        id_terpilih = int(sel[0])
        item_values = tree.item(sel, "values")
        nama_p = item_values[1]
        
        shadow_konf_outer, shadow_konf_inner, konf_dlg = buat_dual_shadow_panel(
            dlg, width=400, height=220, relx=0.5, rely=0.5, anchor="center"
        )
        try:
            konf_dlg.grab_set()
            konf_dlg.focus_force()
        except Exception:
            pass
        
        tk.Label(konf_dlg, text="⚠ PERINGATAN HAPUS ⚠", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_MERAH).pack(pady=(20, 10))
        tk.Label(konf_dlg, text=f"Anda akan menghapus data:", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack()
        tk.Label(konf_dlg, text=f"ID {id_terpilih} - {nama_p}", font=FONT_BESAR, bg=BG_PANEL, fg=FG_KUNING).pack(pady=5)
        
        pilihan = {"idx": 0} # 0 = YA, 1 = TIDAK
        
        frame_btn = tk.Frame(konf_dlg, bg=BG_PANEL)
        frame_btn.pack(pady=15)
        
        btn_ya = tk.Label(frame_btn, text="  YA  ", font=FONT_BESAR, bg=BG_PANEL_SOFT, fg=FG_AKSEN, width=10, pady=5, highlightbackground=FG_AKSEN, highlightthickness=1)
        btn_ya.pack(side="left", padx=10)
        
        btn_tidak = tk.Label(frame_btn, text=" TIDAK ", font=FONT_BESAR, bg=BG_INPUT, fg=FG_UTAMA, width=10, pady=5, highlightbackground=FG_ABU, highlightthickness=1)
        btn_tidak.pack(side="left", padx=10)
        
        def update_buttons():
            if pilihan["idx"] == 0:
                btn_ya.config(bg=BG_PANEL_SOFT, fg=FG_AKSEN, highlightbackground=FG_AKSEN)
                btn_tidak.config(bg=BG_INPUT, fg=FG_UTAMA, highlightbackground=FG_ABU)
            else:
                btn_ya.config(bg=BG_INPUT, fg=FG_UTAMA, highlightbackground=FG_ABU)
                btn_tidak.config(bg=BG_PANEL_SOFT, fg=FG_AKSEN, highlightbackground=FG_AKSEN)
                
        update_buttons()
        
        tk.Label(konf_dlg, text="← / →  pilih     ENTER  konfirmasi     ESC  batal",
                 font=FONT_KECIL, bg=BG_PANEL, fg=FG_ABU).pack(pady=(5, 10))
                 
        def pindah_kiri(e=None):
            pilihan["idx"] = 0
            update_buttons()
            return "break"
            
        def pindah_kanan(e=None):
            pilihan["idx"] = 1
            update_buttons()
            return "break"
            
        def hapus_ya(ev=None):
            try:
                hapus_pending(id_terpilih)
                tree.delete(str(id_terpilih))
                
                try:
                    konf_dlg.grab_release()
                except Exception:
                    pass
                konf_dlg.destroy()
                shadow_konf_outer.destroy()
                shadow_konf_inner.destroy()
                
                if not tree.get_children():
                    batal() # Tutup F7 jika kosong
                else:
                    children = tree.get_children()
                    tree.selection_set(children[0])
                    tree.focus(children[0])
                    tree.focus_set()
            except Exception as e:
                info_kk(konf_dlg, "Error", f"Gagal hapus: {e}", refs=refs)
            return "break"
            
        def batal_hapus(ev=None):
            try:
                konf_dlg.grab_release()
            except Exception:
                pass
            konf_dlg.destroy()
            shadow_konf_outer.destroy()
            shadow_konf_inner.destroy()
            tree.focus_set()
            return "break"
            
        def eksekusi(e=None):
            if pilihan["idx"] == 0:
                return hapus_ya()
            else:
                return batal_hapus()
                
        btn_ya.bind("<Button-1>", hapus_ya)
        btn_tidak.bind("<Button-1>", batal_hapus)
        
        konf_dlg.bind("<Left>", pindah_kiri)
        konf_dlg.bind("<Right>", pindah_kanan)
        konf_dlg.bind("<Return>", eksekusi)
        konf_dlg.bind("<Escape>", batal_hapus)
        
        parent.wait_window(konf_dlg)
        
    def batal(ev=None):
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
        
    def _tab_next(ev=None):
        tree.focus_set()
        return "break"
        
    frame_btn = tk.Frame(dlg, bg=BG_PANEL)
    frame_btn.pack(pady=10)
    
    btn_hapus = tk.Label(frame_btn, text="[DELETE] HAPUS", font=FONT_BESAR, bg=BG_INPUT, fg=FG_MERAH, padx=20, pady=5, cursor="hand2")
    btn_hapus.pack(side="left", padx=10)
    btn_hapus.bind("<Button-1>", lakukan_hapus)
    
    btn_batal = tk.Label(frame_btn, text="[ESC] BATAL", font=FONT_BESAR, bg=BG_INPUT, fg=FG_UTAMA, padx=20, pady=5, cursor="hand2")
    btn_batal.pack(side="left", padx=10)
    btn_batal.bind("<Button-1>", batal)
    
    tree.bind("<Delete>", lakukan_hapus)
    tree.bind("<Tab>", _tab_next)
    tree.bind("<Escape>", batal)
    
    dlg.bind("<Delete>", lakukan_hapus)
    dlg.bind("<Escape>", batal)
    
    children = tree.get_children()
    if children:
        tree.selection_set(children[0])
        tree.focus(children[0])
        
    dlg.focus_force()
    tree.focus_set()
    
    parent.wait_window(dlg)
    return "break"