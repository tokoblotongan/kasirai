import tkinter as tk
from tkinter import ttk
from config.theme import (
    BG_PANEL,
    BG_HEADER_TOP,
    BG_INPUT,
    BG_INPUT_FG,
    FG_UTAMA,
    FG_AKSEN,
    FG_MERAH,
    FG_ABU,
    FONT_JUDUL,
    FONT_TABLE,
    FONT_TABLE_HEAD
)
from database.queries import cari_barang_full
from handlers.keranjang import tambah_ke_keranjang

def buka_dialog_cari_barang(event=None, root=None, refs=None, state=None, initial_keyword=""):
    from ui.components import buat_dual_shadow_panel
    
    target_root = root or (refs.get("root") if refs else None)
    if not target_root:
        return "break"
        
    shadow_outer, shadow_inner, overlay = buat_dual_shadow_panel(
        target_root, width=960, height=620, relx=0.5, rely=0.5, anchor="center"
    )
    
    try:
        overlay.grab_set()
    except Exception:
        pass
        
    tk.Label(overlay, text="◉  CARI DATA BARANG  ·  ESC untuk keluar",
             font=FONT_JUDUL, bg=BG_HEADER_TOP, fg=FG_UTAMA).pack(fill="x", ipady=8)
             
    frame_input = tk.Frame(overlay, bg=BG_PANEL, pady=10, highlightthickness=0)
    frame_input.pack(fill="x", padx=15, pady=10)
    lbl_dicari = tk.Label(frame_input, text="🔍 DICARI :", font=FONT_JUDUL,
                          bg=BG_PANEL, fg=FG_AKSEN)
    lbl_dicari.pack(side="left", padx=10)
    
    entry_cari = tk.Entry(frame_input, font=FONT_JUDUL, width=50,
                          bg=BG_INPUT, fg=BG_INPUT_FG,
                          insertbackground=FG_AKSEN,
                          relief="flat", bd=6,
                          highlightbackground=FG_AKSEN,
                          highlightthickness=1)
    entry_cari.pack(side="left", padx=10, ipady=3)
    
    columns = ("plu", "barkode", "hrgjual", "nama", "satuan", "stok")
    tree_cari = ttk.Treeview(overlay, columns=columns, show="headings", height=14)
    tree_cari.heading("plu", text="PLU")
    tree_cari.heading("barkode", text="BARCODE")
    tree_cari.heading("hrgjual", text="HARGA JUAL")
    tree_cari.heading("nama", text="NAMA BARANG")
    tree_cari.heading("satuan", text="SATUAN")
    tree_cari.heading("stok", text="STOK")
    
    tree_cari.column("plu", width=90, anchor="center")
    tree_cari.column("barkode", width=120, anchor="center")
    tree_cari.column("hrgjual", width=110, anchor="e")
    tree_cari.column("nama", width=380, anchor="w")
    tree_cari.column("satuan", width=70, anchor="w")
    tree_cari.column("stok", width=90, anchor="e")
    
    tree_cari.tag_configure("stok_minus", foreground=FG_MERAH)
    tree_cari.tag_configure("stok_normal", foreground=FG_UTAMA)
    tree_cari.pack(fill="both", expand=True, padx=15, pady=(0, 10))
    
    # [FIX] Inisialisasi style tabel agar sesuai tema modern
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading",
                    font=FONT_TABLE_HEAD,
                    background=BG_PANEL,
                    foreground=FG_AKSEN,
                    borderwidth=0,
                    relief="flat",
                    padding=(8, 6))
    style.configure("Treeview",
                    font=FONT_TABLE,
                    rowheight=30,
                    background=BG_PANEL,
                    foreground=FG_UTAMA,
                    fieldbackground=BG_PANEL,
                    borderwidth=0,
                    focuscolor=FG_AKSEN)
    
    # ============================================================
    # EFEK BLINK
    # ============================================================
    blink_state = {"target": "entry", "on": False, "job": None}
    TREE_BLINK_ON  = FG_AKSEN
    TREE_BLINK_OFF = BG_PANEL
    LABEL_BLINK_ON_COLOR  = FG_AKSEN
    LABEL_BLINK_OFF_COLOR = FG_ABU
    ENTRY_BLINK_ON_BG  = "#282A36"
    ENTRY_BLINK_OFF_BG = BG_INPUT
    
    def _stop_blink():
        if blink_state["job"] is not None:
            try:
                target_root.after_cancel(blink_state["job"])
            except Exception:
                pass
            blink_state["job"] = None
            
    def _restore_all_visual():
        sel = tree_cari.selection()
        if sel:
            val = tree_cari.item(sel[0], "values")
            try:
                stok_val = float((val[5] or "0").replace(",", ""))
            except Exception:
                stok_val = 0
            tag = "stok_minus" if stok_val < 0 else "stok_normal"
            tree_cari.item(sel[0], tags=(tag,))
        lbl_dicari.config(fg=FG_ABU)
        entry_cari.config(bg=BG_INPUT)
        
    def _blink_tick():
        if not overlay.winfo_exists():
            return
        on = not blink_state["on"]
        blink_state["on"] = on
        
        if blink_state["target"] == "tree":
            sel = tree_cari.selection()
            if sel:
                warna = TREE_BLINK_ON if on else TREE_BLINK_OFF
                tag_name = f"blink_{'on' if on else 'off'}"
                tree_cari.tag_configure(tag_name, background=warna)
                tree_cari.item(sel[0], tags=(tag_name,))
            lbl_dicari.config(fg=FG_ABU)
            entry_cari.config(bg=BG_INPUT)
        else:
            if on:
                lbl_dicari.config(fg=LABEL_BLINK_ON_COLOR)
                entry_cari.config(bg=ENTRY_BLINK_ON_BG)
            else:
                lbl_dicari.config(fg=LABEL_BLINK_OFF_COLOR)
                entry_cari.config(bg=ENTRY_BLINK_OFF_BG)
            sel = tree_cari.selection()
            if sel:
                val = tree_cari.item(sel[0], "values")
                try:
                    stok_val = float((val[5] or "0").replace(",", ""))
                except Exception:
                    stok_val = 0
                tag = "stok_minus" if stok_val < 0 else "stok_normal"
                tree_cari.item(sel[0], tags=(tag,))
                
        blink_state["job"] = target_root.after(500, _blink_tick)
        
    def _set_blink_target(target):
        _stop_blink()
        _restore_all_visual()
        blink_state["target"] = target
        blink_state["on"] = False
        _blink_tick()
        
    def fokus_ke_entry(ev=None):
        entry_cari.focus_force()
        entry_cari.icursor(tk.END)
        _set_blink_target("entry")
        return "break"
        
    def fokus_ke_tree(ev=None):
        children = tree_cari.get_children()
        if children:
            sel = tree_cari.selection()
            if not sel:
                tree_cari.selection_set(children[0])
                tree_cari.focus(children[0])
            tree_cari.focus_set()
            _set_blink_target("tree")
        return "break"
        
    def pindah_ke_atas(ev=None):
        children = tree_cari.get_children()
        if not children:
            return "break"
        sel = tree_cari.selection()
        if sel:
            idx = children.index(sel[0])
            if idx > 0:
                _restore_all_visual()
                tree_cari.selection_set(children[idx - 1])
                tree_cari.focus(children[idx - 1])
                tree_cari.see(children[idx - 1])
                _set_blink_target("tree")
            else:
                fokus_ke_entry()
        else:
            tree_cari.selection_set(children[0])
            tree_cari.focus(children[0])
            _set_blink_target("tree")
        return "break"
        
    def pindah_ke_bawah(ev=None):
        children = tree_cari.get_children()
        if not children:
            return "break"
        sel = tree_cari.selection()
        if sel:
            idx = children.index(sel[0])
            if idx < len(children) - 1:
                _restore_all_visual()
                tree_cari.selection_set(children[idx + 1])
                tree_cari.focus(children[idx + 1])
                tree_cari.see(children[idx + 1])
                _set_blink_target("tree")
        else:
            tree_cari.selection_set(children[0])
            tree_cari.focus(children[0])
            _set_blink_target("tree")
        return "break"
        
    def lakukan_pencarian(ev=None):
        keyword = entry_cari.get().strip()
        for r in tree_cari.get_children():
            tree_cari.delete(r)
        try:
            rows = cari_barang_full(keyword, limit=200)
            for r in rows:
                stok_val = float(r[5] or 0)
                stok_display = f"{stok_val:,.2f}"
                tag_stok = "stok_minus" if stok_val < 0 else "stok_normal"
                tree_cari.insert("", "end", values=(
                    r[0], r[3] or "",
                    f"{float(r[2] or 0):,.0f}".replace(",", "."),
                    r[1] or "", r[4] or "PC", stok_display
                ), tags=(tag_stok,))
            children = tree_cari.get_children()
            if children:
                tree_cari.selection_set(children[0])
                tree_cari.focus(children[0])
                tree_cari.see(children[0])
                tree_cari.focus_set()
                _set_blink_target("tree")
            else:
                entry_cari.focus_set()
                _set_blink_target("entry")
        except Exception as e:
            print(f"Error cari: {e}")
        return "break"
        
    def ketik_di_tree(ev=None):
        if ev is None:
            return "break"
        if ev.keysym in ("Up", "Down", "Return", "KP_Enter", "Escape", "Tab",
                         "Shift_L", "Shift_R", "Control_L", "Control_R",
                         "Alt_L", "Alt_R", "Caps_Lock", "BackSpace", "ISO_Left_Tab"):
            return None
        if not ev.char or not ev.char.isprintable():
            return "break"
        entry_cari.focus_set()
        entry_cari.insert(tk.END, ev.char)
        entry_cari.icursor(tk.END)
        _set_blink_target("entry")
        lakukan_pencarian()
        return "break"
        
    def tab_dari_entry(ev=None):
        children = tree_cari.get_children()
        if children:
            sel = tree_cari.selection()
            if not sel:
                tree_cari.selection_set(children[0])
                tree_cari.focus(children[0])
                tree_cari.see(children[0])
            tree_cari.focus_set()
            _set_blink_target("tree")
        return "break"
        
    def tab_dari_tree(ev=None):
        entry_cari.focus_set()
        entry_cari.select_range(0, tk.END)
        entry_cari.icursor(tk.END)
        _set_blink_target("entry")
        return "break"
        
    def pilih_item_cari(ev=None):
        sel = tree_cari.selection()
        if not sel:
            return "break"
        val = tree_cari.item(sel[0], "values")
        _stop_blink()
        try:
            overlay.grab_release()
        except Exception:
            pass
        overlay.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        tambah_ke_keranjang(val[0], val[3], float(val[2].replace(".", "")), 1.0, val[4],
                            target_root, refs, state)
        return "break"
        
    def tutup(ev=None):
        _stop_blink()
        try:
            overlay.grab_release()
        except Exception:
            pass
        overlay.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            target_root.after(10, lambda: refs["entry_barcode"].focus())
        return "break"
        
    entry_cari.bind("<Return>", lakukan_pencarian)
    entry_cari.bind("<Down>", fokus_ke_tree)
    entry_cari.bind("<Escape>", tutup)
    entry_cari.bind("<Tab>", tab_dari_entry)
    entry_cari.bind("<Shift-Tab>", tab_dari_entry)
    
    tree_cari.bind("<Tab>", tab_dari_tree)
    tree_cari.bind("<Shift-Tab>", tab_dari_tree)
    tree_cari.bind("<Return>", pilih_item_cari)
    tree_cari.bind("<Double-1>", pilih_item_cari)
    tree_cari.bind("<Up>", pindah_ke_atas)
    tree_cari.bind("<Down>", pindah_ke_bawah)
    tree_cari.bind("<Escape>", tutup)
    tree_cari.bind("<Key>", ketik_di_tree)
    
    overlay.bind("<Escape>", tutup)
    
    if initial_keyword:
        entry_cari.insert(0, initial_keyword)
        
    lakukan_pencarian()
    overlay.update_idletasks()
    entry_cari.focus_force()
    entry_cari.icursor(tk.END)
    _set_blink_target("entry")
    target_root.after(50, lambda: entry_cari.focus_force())
    return "break"

cari_barang_dialog = buka_dialog_cari_barang