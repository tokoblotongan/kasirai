import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config.settings import NAMA_TOKO
from config.theme import (
    BG_UTAMA,
    BG_PANEL,
    BG_SHADOW,
    BG_HEADER_TOP,
    BG_HEADER_BOT,
    BG_INPUT,
    BG_INPUT_FG,
    FG_UTAMA,
    FG_SEKUNDER,
    FG_AKSEN,
    FG_KUNING,
    FG_MERAH,
    FG_SUKSES,
    FG_ABU,
    BG_TABLE_ALT,
    BG_TABLE_SEL,
    BG_HEADING,
    FONT_FAMILY_FB,
    FONT_HEADER,
    FONT_BESAR,
    FONT_JUDUL,
    FONT_INFO,
    FONT_TOTAL_QTY,
    FONT_TABLE_HEAD,
    FONT_TABLE,
    FONT_TABLE_BIG,
    FONT_TOTAL,
    FONT_KECIL
)

from handlers.keranjang import (
    input_barang_barcode,
    update_footer_preview,
    fokus_ke_tree_dari_entry,
    pindah_ke_atas,
    pindah_ke_bawah,
    tampilkan_overlay_qty,
    batal_overlay_qty,
    void_item,
    refund_item,
    retur_item,
    open_plu,
    ubah_harga_transaksi,
    ubah_satuan
)
from handlers.cari_barang import cari_barang_dialog
from handlers.checkout import (
    checkout_dialog,
    buka_laci,
    copy_struk
)
from handlers.pending import (
    set_pending,
    call_pending,
    clear_pending
)
from handlers.aksi_lain import (
    info_bantuan,
    input_nota_manual,
    hapus_transaksi,
    set_member,
    biaya_tambahan_func,
    diskon_global_rp_func,
    cash_out,
    diskon_per_item,
    diskon_item_persen
)

def update_nomor_nota_display(refs, state):
    tgl_hari_ini = datetime.now().strftime("%d-%m-%Y")
    user = state.get("user_aktif") or "UMUM"
    shift = state.get("shift", "A")
    nomor_nota = state.get("nomor_nota", "000001")
    info_str = f"📅  {tgl_hari_ini}   ·   Shift {shift}   ·   {user.upper()}   ·   NOTA: {nomor_nota}"
    if refs and "lbl_nomor_nota" in refs and refs["lbl_nomor_nota"].winfo_exists():
        refs["lbl_nomor_nota"].config(text=info_str)

def escape_global(event, root, refs, state):
    if state.get("overlay_qty") and state["overlay_qty"].winfo_exists():
        batal_overlay_qty(event, root, refs, state)
        return "break"
    if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
        refs["entry_barcode"].focus_set()
    return "break"

def bind_hotkeys(root, refs, state):
    root.bind("<F1>", lambda e: info_bantuan(e, root, refs, state))
    root.bind("<F2>", lambda e: void_item(e, root, refs, state))
    root.bind("<F3>", lambda e: open_plu(e, root, refs, state))
    root.bind("<F4>", lambda e: ubah_harga_transaksi(e, root, refs, state))
    root.bind("<F5>", lambda e: set_pending(e, root, refs, state))
    root.bind("<F6>", lambda e: call_pending(e, root, refs, state))
    root.bind("<F7>", lambda e: clear_pending(e, root, refs, state))
    
    # [FIX] Binding F8 untuk Laporan
    def _buka_laporan(event):
        from ui.laporan import tampilkan_laporan
        tampilkan_laporan(root, refs, state)
        return "break"
    root.bind("<F8>", _buka_laporan)
    
    root.bind("<F9>", lambda e: diskon_per_item(e, root, refs, state))
    root.bind("<F10>", lambda e: cari_barang_dialog(e, root, refs, state))
    root.bind("<F11>", lambda e: buka_laci(e, root, refs, state))
    root.bind("<F12>", lambda e: copy_struk(e, root, refs, state))
    
    def _handle_plus_global(event):
        w = root.focus_get()
        if isinstance(w, tk.Entry):
            return None
        checkout_dialog(event, root, refs, state)
        return "break"
    
    def _handle_minus_global(event):
        w = root.focus_get()
        if isinstance(w, tk.Entry):
            return None
        refund_item(event, root, refs, state)
        return "break"
    
    def _handle_slash_global(event):
        w = root.focus_get()
        if isinstance(w, tk.Entry):
            return None
        input_nota_manual(event, root, refs, state)
        return "break"
    
    root.bind("<plus>", _handle_plus_global)
    root.bind("<KP_Add>", _handle_plus_global)
    root.bind("<minus>", _handle_minus_global)
    root.bind("<KP_Subtract>", _handle_minus_global)
    root.bind("<slash>", _handle_slash_global)
    root.bind("<KP_Divide>", _handle_slash_global)
    
    root.bind("<Shift-F11>", lambda e: set_member(e, root, refs, state))
    root.bind("<Alt-F11>", lambda e: biaya_tambahan_func(e, root, refs, state))
    root.bind("<Control-F11>", lambda e: hapus_transaksi(e, root, refs, state))
    root.bind("<Alt-F12>", lambda e: cash_out(e, root, refs, state))
    root.bind("<Control-F12>", lambda e: ubah_satuan(e, root, refs, state))
    root.bind("<Shift-F3>", lambda e: retur_item(e, root, refs, state))
    root.bind("<Control-F4>", lambda e: diskon_global_rp_func(e, root, refs, state))
    root.bind("<Escape>", lambda e: escape_global(e, root, refs, state))
    
    tree = refs["tree"]
    entry_barcode = refs["entry_barcode"]
    
    tree.bind("<Up>", lambda e: pindah_ke_atas(e, root, refs, state))
    tree.bind("<Down>", lambda e: pindah_ke_bawah(e, root, refs, state))
    tree.bind("<asterisk>", lambda e: tampilkan_overlay_qty(e, root, refs, state))
    tree.bind("<KP_Multiply>", lambda e: tampilkan_overlay_qty(e, root, refs, state))
    
    def _on_tree_key(event):
        if event.char and event.char.isdigit():
            entry_barcode.focus_set()
            entry_barcode.insert(tk.END, event.char)
            return "break"
        return None
    tree.bind("<Key>", _on_tree_key)
    
    entry_barcode.bind("<Down>", lambda e: fokus_ke_tree_dari_entry(e, root, refs, state))
    entry_barcode.bind("<KeyRelease>", lambda e: update_footer_preview(e, root, refs, state))
    entry_barcode.bind("<Return>", lambda e: input_barang_barcode(e, root, refs, state))

def buat_ui_utama(root, *args, **kwargs):
    if len(args) >= 3 and isinstance(args[2], dict) and "keranjang" in args[2]:
        user_id, nama_user, state = args[0], args[1], args[2]
        refs = kwargs.get("refs") if kwargs.get("refs") is not None else {}
        state["user_id"] = user_id
        state["user_aktif"] = user_id
        state["nama_user"] = nama_user
    elif len(args) >= 2 and isinstance(args[0], dict):
        state, refs = args[0], args[1]
    elif len(args) == 1 and isinstance(args[0], dict):
        state = args[0]
        refs = kwargs.get("refs") if kwargs.get("refs") is not None else {}
    else:
        state = kwargs.get("state") or {}
        refs = kwargs.get("refs") if kwargs.get("refs") is not None else {}
        
    # ============================================================
    # HEADER — Soft gradient, tanpa border
    # ============================================================
    frame_header = tk.Frame(root, bg=BG_HEADER_TOP, height=56)
    frame_header.pack(fill="x", padx=0, pady=0)
    frame_header.pack_propagate(False)
    
    for _ in range(3):
        tk.Frame(root, bg=BG_SHADOW, height=1).pack(fill="x")
        
    header_text = f"◉  KASSA {state.get('nomor_kassa', '001')}  ·  {NAMA_TOKO.upper()}"
    lbl_header = tk.Label(frame_header, text=header_text,
                          font=FONT_HEADER,
                          bg=BG_HEADER_TOP, fg=FG_UTAMA)
    lbl_header.pack(side="left", padx=25, pady=15)
    
    lbl_net = tk.Label(frame_header, text="● ONLINE",
                       font=FONT_KECIL,
                       bg=BG_HEADER_TOP, fg=FG_SUKSES)
    lbl_net.pack(side="right", padx=25)
    
    # ============================================================
    # INFO BAR
    # ============================================================
    frame_info_wrapper = tk.Frame(root, bg=BG_UTAMA)
    frame_info_wrapper.pack(fill="x", padx=10, pady=8)
    
    shadow_info_outer = tk.Frame(frame_info_wrapper, bg=BG_SHADOW)
    shadow_info_outer.place(x=3, y=3, relwidth=1, relheight=1)
    shadow_info_inner = tk.Frame(frame_info_wrapper, bg=BG_SHADOW)
    shadow_info_inner.place(x=2, y=2, relwidth=1, relheight=1)
    
    frame_info = tk.Frame(frame_info_wrapper, bg=BG_PANEL, highlightthickness=0)
    frame_info.pack(fill="x")
    
    tgl_hari_ini = datetime.now().strftime("%d-%m-%Y")
    user = state.get("user_aktif") or "UMUM"
    info_str1 = f"📅  {tgl_hari_ini}   ·   Shift {state.get('shift', 'A')}   ·   {user.upper()}"
    lbl_nomor_nota = tk.Label(frame_info, text=info_str1,
                              font=FONT_INFO,
                              bg=BG_PANEL, fg=FG_AKSEN)
    lbl_nomor_nota.pack(anchor="w", padx=20, pady=(10, 3))
    
    pelanggan = state.get("nama_user", "UMUM")
    lbl_pelanggan = tk.Label(frame_info,
                             text=f"👤  PELANGGAN: {pelanggan.upper()}",
                             font=FONT_INFO,
                             bg=BG_PANEL, fg=FG_UTAMA)
    lbl_pelanggan.pack(anchor="w", padx=20, pady=(0, 10))
    
    lbl_nota = tk.Label(frame_info, text=f"NOTA  ·  {state.get('nomor_nota', '000001')}",
                        font=FONT_INFO,
                        bg=BG_PANEL, fg=FG_KUNING)
    lbl_nota.place(relx=1.0, rely=0.5, anchor="e", x=-20)
    
    # ============================================================
    # QTY BAR
    # ============================================================
    frame_qty_wrapper = tk.Frame(root, bg=BG_UTAMA)
    frame_qty_wrapper.pack(fill="x", padx=10, pady=(0, 8))
    
    shadow_qty_outer = tk.Frame(frame_qty_wrapper, bg=BG_SHADOW)
    shadow_qty_outer.place(x=3, y=3, relwidth=1, relheight=1)
    shadow_qty_inner = tk.Frame(frame_qty_wrapper, bg=BG_SHADOW)
    shadow_qty_inner.place(x=2, y=2, relwidth=1, relheight=1)
    
    frame_qty = tk.Frame(frame_qty_wrapper, bg=BG_PANEL, highlightthickness=0)
    frame_qty.pack(fill="x")
    
    lbl_total_qty = tk.Label(frame_qty,
                             text="TOTAL QTY :     0.00",
                             font=FONT_TOTAL_QTY,
                             bg=BG_PANEL, fg=FG_AKSEN)
    lbl_total_qty.pack(anchor="w", padx=20, pady=10)
    
    # ============================================================
    # STATUS BAR BAWAH
    # ============================================================
    # [FIX] Update teks footer hotkey
    lbl_status = tk.Label(root,
                          text="  [F1] Bantuan  ·  [F8] Laporan  ·  [F10] Cari Barang  ·  [+] Checkout  ·  [*] Ubah Qty  ·  [-] Retur",
                          font=FONT_KECIL,
                          bg=BG_HEADER_BOT,
                          fg="#A0A5B5",
                          anchor="w",
                          padx=20,
                          pady=8)
    lbl_status.pack(fill="x", side="bottom")
    
    # ============================================================
    # FOOTER
    # ============================================================
    frame_footer_wrapper = tk.Frame(root, bg=BG_UTAMA)
    frame_footer_wrapper.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
    
    shadow_footer_outer = tk.Frame(frame_footer_wrapper, bg=BG_SHADOW)
    shadow_footer_outer.place(x=4, y=4, relwidth=1, relheight=1)
    shadow_footer_inner = tk.Frame(frame_footer_wrapper, bg=BG_SHADOW)
    shadow_footer_inner.place(x=2, y=2, relwidth=1, relheight=1)
    
    frame_footer = tk.Frame(frame_footer_wrapper, bg=BG_PANEL, highlightthickness=0)
    frame_footer.pack(fill="x")
    
    frame_footer_row1 = tk.Frame(frame_footer, bg=BG_PANEL)
    frame_footer_row1.pack(fill="x")
    
    tk.Label(frame_footer_row1, text="JUMLAH",
             font=(FONT_FAMILY_FB, 16, "bold"),
             bg=BG_PANEL, fg=FG_SEKUNDER).pack(side="left", padx=(25, 5), pady=12)
    
    tk.Label(frame_footer_row1, text=": Rp",
             font=(FONT_FAMILY_FB, 16, "bold"),
             bg=BG_PANEL, fg=FG_SEKUNDER).pack(side="left")
    
    lbl_grand_total = tk.Label(frame_footer_row1, text="0",
                               font=FONT_TOTAL,
                               bg=BG_PANEL, fg=FG_SUKSES)
    lbl_grand_total.pack(side="right", padx=30, pady=8)
    
    lbl_preview = tk.Label(frame_footer, text="",
                           font=FONT_KECIL,
                           bg=BG_PANEL, fg=FG_SUKSES,
                           anchor="w")
    lbl_preview.pack(fill="x", padx=25, pady=(0, 12))
    
    # ============================================================
    # INPUT BAR
    # ============================================================
    frame_input_wrapper = tk.Frame(root, bg=BG_UTAMA)
    frame_input_wrapper.pack(fill="x", side="bottom", padx=10, pady=(0, 8))
    
    shadow_input_outer = tk.Frame(frame_input_wrapper, bg=BG_SHADOW)
    shadow_input_outer.place(x=3, y=3, relwidth=1, relheight=1)
    shadow_input_inner = tk.Frame(frame_input_wrapper, bg=BG_SHADOW)
    shadow_input_inner.place(x=2, y=2, relwidth=1, relheight=1)
    
    frame_input = tk.Frame(frame_input_wrapper, bg=BG_PANEL, highlightthickness=0)
    frame_input.pack(fill="x")
    
    tk.Label(frame_input, text="🔍 INPUT:",
             font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_AKSEN).pack(side="left", padx=(20, 10), pady=12)
    
    entry_barcode = tk.Entry(frame_input,
                             font=(FONT_FAMILY_FB, 14),
                             width=40,
                             bg=BG_INPUT,
                             fg=BG_INPUT_FG,
                             insertbackground=FG_AKSEN,
                             relief="flat", bd=8,
                             highlightbackground=FG_AKSEN,
                             highlightthickness=2)
    entry_barcode.pack(side="left", padx=(0, 20), pady=12, ipady=4, fill="x", expand=True)
    
    # ============================================================
    # STYLE TABEL
    # ============================================================
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Treeview.Heading",
                    font=FONT_TABLE_HEAD,
                    background=BG_HEADING,
                    foreground=FG_AKSEN,
                    borderwidth=0,
                    relief="flat",
                    padding=(12, 10))
    
    style.configure("Treeview",
                    font=FONT_TABLE,
                    rowheight=38,
                    background=BG_PANEL,
                    foreground=FG_UTAMA,
                    fieldbackground=BG_PANEL,
                    borderwidth=0,
                    focuscolor=BG_TABLE_SEL)
    
    style.map("Treeview",
              background=[("selected", BG_TABLE_SEL)],
              foreground=[("selected", FG_UTAMA)])
    
    # ============================================================
    # TABEL UTAMA
    # ============================================================
    frame_tabel = tk.Frame(root, bg=BG_UTAMA)
    frame_tabel.pack(fill="both", expand=True, padx=10, pady=(0, 8))
    
    columns = ("no", "kode", "nama", "harga", "diskon", "qty", "subtotal")
    tree = ttk.Treeview(frame_tabel, columns=columns, show="headings", height=15)
    
    tree.heading("no", text="NO")
    tree.heading("kode", text="KODE")
    tree.heading("nama", text="NAMA BARANG")
    tree.heading("harga", text="HARGA")
    tree.heading("diskon", text="DISKON %")
    tree.heading("qty", text="QTY")
    tree.heading("subtotal", text="SUBTOTAL")
    
    tree.column("no", width=40, anchor="center")
    tree.column("kode", width=100, anchor="center")
    tree.column("nama", width=400, anchor="w")
    tree.column("harga", width=130, anchor="e")
    tree.column("diskon", width=80, anchor="center")
    tree.column("qty", width=110, anchor="center")
    tree.column("subtotal", width=160, anchor="e")
    tree.pack(fill="both", expand=True, side="left")
    
    scrollbar = tk.Scrollbar(frame_tabel, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.config(yscrollcommand=scrollbar.set)
    
    tree.tag_configure("oddrow", background=BG_PANEL, foreground=FG_UTAMA)
    tree.tag_configure("evenrow", background=BG_TABLE_ALT, foreground=FG_UTAMA)
    tree.tag_configure("minus", background="#2A1520", foreground=FG_MERAH)
    tree.tag_configure("nama_besar", font=FONT_TABLE_BIG)
    
    refs["root"] = root
    refs["tree"] = tree
    refs["entry_barcode"] = entry_barcode
    refs["lbl_nomor_nota"] = lbl_nomor_nota
    refs["lbl_pelanggan"] = lbl_pelanggan
    refs["lbl_total_qty"] = lbl_total_qty
    refs["lbl_grand_total"] = lbl_grand_total
    refs["lbl_preview"] = lbl_preview
    refs["lbl_status"] = lbl_status
    
    bind_hotkeys(root, refs, state)
    entry_barcode.focus()