import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
from config.theme import (
    BG_UTAMA, BG_PANEL, BG_HEADER_TOP, BG_INPUT, BG_INPUT_FG, FG_UTAMA,
    FG_AKSEN, FG_MERAH, FG_SUKSES, BG_TABLE_SEL, BG_HEADING, FG_KUNING
)

def tampilkan_laporan(root, refs=None, state=None):
    from handlers.laporan import (
        get_laporan_penjualan, get_laporan_audit, get_laporan_shift,
        get_laporan_rekonsiliasi, get_laporan_daftar_refund,
        get_laporan_barang_laku, get_laporan_per_nota
    )
    
    parent = root
    try:
        if isinstance(root, tk.Toplevel):
            parent = root.winfo_toplevel()
    except Exception:
        pass

    was_zoomed = False
    try:
        if parent.state() != 'zoomed':
            parent.state('zoomed')
            was_zoomed = True
    except Exception:
        pass

    old_root_esc_binding = parent.bind("<Escape>")
    old_root_close_protocol = parent.protocol("WM_DELETE_WINDOW")
    
    frame_main = tk.Frame(parent, bg=BG_UTAMA)
    frame_main.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_main.lift()
    frame_main.grab_set()
    frame_main.focus_force()
    
    is_active = {"val": True}
    
    def _tutup(ev=None):
        if not is_active["val"]: return "break"
        is_active["val"] = False
        try: frame_main.grab_release()
        except: pass
        if old_root_esc_binding: parent.bind("<Escape>", old_root_esc_binding)
        else: parent.unbind("<Escape>")
        if old_root_close_protocol: parent.protocol("WM_DELETE_WINDOW", old_root_close_protocol)
        frame_main.destroy()
        if was_zoomed:
            try: parent.state('normal')
            except: pass
        if refs and "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            parent.after(10, lambda: refs["entry_barcode"].focus())
        return "break"

    parent.bind("<Escape>", _tutup)
    parent.protocol("WM_DELETE_WINDOW", _tutup)

    # ============================================================
    # 1. HEADER MENU BAR (Atas)
    # ============================================================
    frame_header = tk.Frame(frame_main, bg=BG_HEADER_TOP, height=44)
    frame_header.pack(fill="x")
    frame_header.pack_propagate(False)
    
    frame_isi = tk.Frame(frame_main, bg=BG_UTAMA)
    frame_isi.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ============================================================
    # 2. PANEL KIRI (MENU) & KANAN (TABEL)
    # ============================================================
    frame_kiri = tk.Frame(frame_isi, bg=BG_PANEL, width=320)
    frame_kiri.pack(side="left", fill="y", padx=(0, 10))
    frame_kiri.pack_propagate(False)
    
    tk.Label(frame_kiri, text="📑 DAFTAR LAPORAN", font=("Segoe UI", 11, "bold"),
             bg=BG_PANEL, fg=FG_AKSEN).pack(anchor="w", padx=12, pady=(12, 6))

    listbox_menu = tk.Listbox(frame_kiri, font=("Consolas", 11), bg=BG_INPUT, fg=FG_UTAMA,
                              selectbackground=FG_AKSEN, selectforeground="#FFFFFF",
                              borderwidth=0, highlightthickness=1, highlightbackground="#343746")
    listbox_menu.pack(fill="both", expand=True, pady=5, padx=10)

    frame_kanan = tk.Frame(frame_isi, bg=BG_UTAMA)
    frame_kanan.pack(side="left", fill="both", expand=True)
    
    lbl_loading = tk.Label(frame_kanan, text="", font=("Segoe UI", 12, "bold"), bg=BG_UTAMA, fg=FG_KUNING)
    lbl_loading.pack(pady=4)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Laporan.Treeview.Heading", font=("Consolas", 10, "bold"),
                    background=BG_HEADING, foreground=FG_AKSEN, borderwidth=1, relief="solid", padding=(6, 6))
    style.configure("Laporan.Treeview", font=("Consolas", 10), rowheight=28,
                    background=BG_PANEL, foreground=FG_UTAMA, fieldbackground=BG_PANEL,
                    borderwidth=1, relief="solid")
    style.map("Laporan.Treeview", background=[("selected", BG_TABLE_SEL)], foreground=[("selected", FG_UTAMA)])
              
    tree_data = ttk.Treeview(frame_kanan, show="headings", style="Laporan.Treeview")
    tree_data.pack(fill="both", expand=True)
    tree_data.tag_configure("negatif", foreground=FG_MERAH)
    tree_data.tag_configure("positif", foreground=FG_SUKSES)
    tree_data.tag_configure("evenrow", background="#282A36")
    tree_data.tag_configure("oddrow", background="#222430")

    frame_footer = tk.Frame(frame_kanan, bg=BG_PANEL, height=44)
    frame_footer.pack(fill="x", pady=(5, 0))
    frame_footer.pack_propagate(False)
    
    lbl_total_data = tk.Label(frame_footer, text="Total Data: 0", font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=FG_UTAMA, padx=20)
    lbl_total_data.pack(side="left")
    
    lbl_total_netto = tk.Label(frame_footer, text="", font=("Consolas", 13, "bold"), bg=BG_PANEL, fg=FG_SUKSES, padx=20)
    lbl_total_netto.pack(side="right")

    frame_status = tk.Frame(frame_main, bg=BG_HEADER_TOP, height=32)
    frame_status.pack(fill="x", side="bottom")
    lbl_status = tk.Label(frame_status, text="  [ENTER] Pilih Laporan   ·   [Double Click] Buka Filter   ·   [ESC] Kembali ke POS Kasir", 
                          font=("Segoe UI", 10), bg=BG_HEADER_TOP, fg=FG_UTAMA, anchor="w", padx=10)
    lbl_status.pack(side="left", fill="y")

    current_mode = {"idx": 0}
    menu_labels = {}

    # ============================================================
    # 3. THREADING & UPDATE UI
    # ============================================================
    def worker_thread(mode_idx, tgl_m, tgl_a):
        hasil = []
        error_msg = None
        try:
            if mode_idx == 0: hasil = list(get_laporan_penjualan(tgl_m, tgl_a))
            elif mode_idx == 1: hasil = list(get_laporan_audit(tgl_m, tgl_a))
            elif mode_idx == 2: hasil = list(get_laporan_shift(tgl_m, tgl_a))
            elif mode_idx == 3: hasil = list(get_laporan_rekonsiliasi(tgl_m, tgl_a))
            elif mode_idx == 4: hasil = list(get_laporan_daftar_refund(tgl_m, tgl_a))
            elif mode_idx == 5: hasil = list(get_laporan_barang_laku(tgl_m, tgl_a))
            elif mode_idx == 6: hasil = list(get_laporan_per_nota(tgl_m, tgl_a))
            else: hasil = []
        except Exception as e:
            error_msg = str(e)
            
        if is_active["val"]:
            parent.after(10, lambda: update_ui(mode_idx, hasil, error_msg))

    def update_ui(mode_idx, data, error_msg):
        if not is_active["val"]: return
        
        lbl_loading.config(text="")
        tree_data.delete(*tree_data.get_children())
        total_netto = 0
        total_qty = 0
        
        if error_msg:
            tree_data["columns"] = ("error",)
            tree_data.heading("error", text="Error")
            tree_data.column("error", width=800, anchor="w")
            tree_data.insert("", "end", values=(f"Gagal: {error_msg}",))
            lbl_total_data.config(text="Total Data: 0")
            lbl_total_netto.config(text="")
            return

        # TAB 1: Penjualan & Cara Bayar
        if mode_idx == 0:
            tree_data["columns"] = ("no", "cara", "jml", "netto")
            tree_data.heading("no", text="NO")
            tree_data.heading("cara", text="CARA BAYAR")
            tree_data.heading("jml", text="JML NOTA")
            tree_data.heading("netto", text="TOTAL NETTO (RP)")
            tree_data.column("no", width=60, anchor="center")
            tree_data.column("cara", width=240, anchor="w")
            tree_data.column("jml", width=120, anchor="e")
            tree_data.column("netto", width=220, anchor="e")
            
            for idx, row in enumerate(data):
                nto = float(row[2] or 0.0)
                total_netto += nto
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                tree_data.insert("", "end", values=(
                    idx + 1,
                    row[0] or "CASH",
                    f"{int(row[1] or 0):,}".replace(",", "."),
                    f"Rp {nto:,.0f}".replace(",", ".")
                ), tags=(tag,))

        # TAB 2: Audit Kasir (Bruto, Diskon, Void, Refund, Netto)
        elif mode_idx == 1:
            tree_data["columns"] = ("no", "opr", "faktur", "bruto", "dsk_item", "dsk_glb", "void", "refund", "netto")
            tree_data.heading("no", text="NO")
            tree_data.heading("opr", text="OPERATOR")
            tree_data.heading("faktur", text="FAKTUR")
            tree_data.heading("bruto", text="BRUTO (RP)")
            tree_data.heading("dsk_item", text="DSK ITEM (RP)")
            tree_data.heading("dsk_glb", text="DSK GLOBAL (RP)")
            tree_data.heading("void", text="VOID (RP)")
            tree_data.heading("refund", text="REFUND (RP)")
            tree_data.heading("netto", text="NETTO (RP)")
            
            tree_data.column("no", width=40, anchor="center")
            tree_data.column("opr", width=140, anchor="w")
            tree_data.column("faktur", width=70, anchor="e")
            tree_data.column("bruto", width=130, anchor="e")
            tree_data.column("dsk_item", width=120, anchor="e")
            tree_data.column("dsk_glb", width=120, anchor="e")
            tree_data.column("void", width=110, anchor="e")
            tree_data.column("refund", width=110, anchor="e")
            tree_data.column("netto", width=150, anchor="e")
            
            for idx, row in enumerate(data):
                # row: (operator, total_netto, diskon_item, diskon_global, total_void, total_refund, jumlah_faktur)
                opr = row[0] or "KASIR"
                nto = float(row[1] or 0.0)
                dsk_i = float(row[2] or 0.0)
                dsk_g = float(row[3] or 0.0)
                vod = float(row[4] or 0.0)
                rfn = float(row[5] or 0.0)
                fkt = int(row[6] or 0)
                bruto = nto + dsk_i + dsk_g
                total_netto += nto
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                tree_data.insert("", "end", values=(
                    idx + 1, opr, fkt,
                    f"Rp {bruto:,.0f}".replace(",", "."),
                    f"Rp {dsk_i:,.0f}".replace(",", "."),
                    f"Rp {dsk_g:,.0f}".replace(",", "."),
                    f"Rp {vod:,.0f}".replace(",", "."),
                    f"Rp {rfn:,.0f}".replace(",", "."),
                    f"Rp {nto:,.0f}".replace(",", ".")
                ), tags=(tag,))

        # TAB: Kassa - Kasir - Shift
        elif mode_idx == 2:
            tree_data["columns"] = ("no", "kassa", "opr", "shift", "jml", "netto")
            tree_data.heading("no", text="NO")
            tree_data.heading("kassa", text="KASSA")
            tree_data.heading("opr", text="KASIR")
            tree_data.heading("shift", text="SHIFT")
            tree_data.heading("jml", text="JML FAKTUR")
            tree_data.heading("netto", text="TOTAL NETTO (RP)")
            tree_data.column("no", width=60, anchor="center")
            tree_data.column("kassa", width=100, anchor="center")
            tree_data.column("opr", width=160, anchor="w")
            tree_data.column("shift", width=80, anchor="center")
            tree_data.column("jml", width=120, anchor="e")
            tree_data.column("netto", width=220, anchor="e")
            
            for idx, row in enumerate(data):
                nto = float(row[4] or 0.0)
                total_netto += nto
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                tree_data.insert("", "end", values=(
                    idx + 1, row[0], row[1], row[2], row[3],
                    f"Rp {nto:,.0f}".replace(",", ".")
                ), tags=(tag,))

        # TAB 4: Rekonsiliasi Kas (Modal, Biaya, Penjualan, Setoran, Selisih)
        elif mode_idx == 3:
            tree_data["columns"] = ("no", "opr", "shift", "modal", "biaya", "jual", "uang_sys", "setoran", "selisih")
            tree_data.heading("no", text="NO")
            tree_data.heading("opr", text="KASIR")
            tree_data.heading("shift", text="SHIFT")
            tree_data.heading("modal", text="MODAL AWAL")
            tree_data.heading("biaya", text="BIAYA")
            tree_data.heading("jual", text="PENJUALAN")
            tree_data.heading("uang_sys", text="UANG SISTEM")
            tree_data.heading("setoran", text="SETORAN FISIK")
            tree_data.heading("selisih", text="SELISIH")
            
            tree_data.column("no", width=40, anchor="center")
            tree_data.column("opr", width=120, anchor="w")
            tree_data.column("shift", width=60, anchor="center")
            tree_data.column("modal", width=120, anchor="e")
            tree_data.column("biaya", width=110, anchor="e")
            tree_data.column("jual", width=130, anchor="e")
            tree_data.column("uang_sys", width=140, anchor="e")
            tree_data.column("setoran", width=140, anchor="e")
            tree_data.column("selisih", width=140, anchor="e")
            
            for idx, row in enumerate(data):
                # row: (operator, shift, modal, biaya, total_jual, setoran, uang_sistem, selisih)
                modal = float(row[2] or 0.0)
                biaya = float(row[3] or 0.0)
                jual = float(row[4] or 0.0)
                setoran = float(row[5] or 0.0)
                uang_sys = float(row[6] or (modal + jual - biaya))
                selisih = float(row[7] or (setoran - uang_sys))
                total_netto += jual
                
                tag_selisih = "negatif" if selisih < 0 else "positif"
                tree_data.insert("", "end", values=(
                    idx + 1, row[0], row[1],
                    f"Rp {modal:,.0f}".replace(",", "."),
                    f"Rp {biaya:,.0f}".replace(",", "."),
                    f"Rp {jual:,.0f}".replace(",", "."),
                    f"Rp {uang_sys:,.0f}".replace(",", "."),
                    f"Rp {setoran:,.0f}".replace(",", "."),
                    f"Rp {selisih:,.0f}".replace(",", ".")
                ), tags=(tag_selisih,))

        # TAB: Daftar Refund
        elif mode_idx == 4:
            tree_data["columns"] = ("no", "faktur", "tgl", "kode", "nama", "qty", "nilai")
            tree_data.heading("no", text="NO")
            tree_data.heading("faktur", text="NO FAKTUR")
            tree_data.heading("tgl", text="TANGGAL")
            tree_data.heading("kode", text="KODE")
            tree_data.heading("nama", text="NAMA BARANG")
            tree_data.heading("qty", text="QTY")
            tree_data.heading("nilai", text="NILAI RETUR (RP)")
            
            tree_data.column("no", width=50, anchor="center")
            tree_data.column("faktur", width=110, anchor="center")
            tree_data.column("tgl", width=110, anchor="center")
            tree_data.column("kode", width=90, anchor="center")
            tree_data.column("nama", width=280, anchor="w")
            tree_data.column("qty", width=80, anchor="e")
            tree_data.column("nilai", width=140, anchor="e")
            
            for idx, row in enumerate(data):
                nilai = float(row[5] or 0.0)
                total_netto += nilai
                tag = "negatif"
                tree_data.insert("", "end", values=(
                    idx + 1, row[0], row[1], row[2], row[3], row[4],
                    f"Rp {nilai:,.0f}".replace(",", ".")
                ), tags=(tag,))

        # TAB 6: Laporan Barang Laku (Rekap Semua Barang Terjual)
        elif mode_idx == 5:
            tree_data["columns"] = ("no", "kode", "nama", "qty", "netto")
            tree_data.heading("no", text="NO")
            tree_data.heading("kode", text="KODE BARANG")
            tree_data.heading("nama", text="NAMA BARANG")
            tree_data.heading("qty", text="TOTAL QTY")
            tree_data.heading("netto", text="TOTAL NETTO (RP)")
            tree_data.column("no", width=60, anchor="center")
            tree_data.column("kode", width=120, anchor="center")
            tree_data.column("nama", width=380, anchor="w")
            tree_data.column("qty", width=120, anchor="e")
            tree_data.column("netto", width=200, anchor="e")
            
            for idx, row in enumerate(data):
                # row: (KODEBRG, NAMABRG, total_qty, total_netto)
                q = float(row[2] or 0.0)
                nto = float(row[3] or 0.0)
                total_qty += q
                total_netto += nto
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                tree_data.insert("", "end", values=(
                    idx + 1, row[0], row[1],
                    f"{q:g}",
                    f"Rp {nto:,.0f}".replace(",", ".")
                ), tags=(tag,))

        # TAB 5: Per Nota Faktur
        elif mode_idx == 6:
            tree_data["columns"] = ("no", "faktur", "tgl", "jam", "opr", "cara", "total")
            tree_data.heading("no", text="NO")
            tree_data.heading("faktur", text="NO FAKTUR")
            tree_data.heading("tgl", text="TANGGAL")
            tree_data.heading("jam", text="JAM")
            tree_data.heading("opr", text="KASIR")
            tree_data.heading("cara", text="CARA BAYAR")
            tree_data.heading("total", text="TOTAL FAKTUR (RP)")
            
            tree_data.column("no", width=50, anchor="center")
            tree_data.column("faktur", width=120, anchor="center")
            tree_data.column("tgl", width=100, anchor="center")
            tree_data.column("jam", width=90, anchor="center")
            tree_data.column("opr", width=140, anchor="w")
            tree_data.column("cara", width=110, anchor="center")
            tree_data.column("total", width=180, anchor="e")
            
            for idx, row in enumerate(data):
                tot = float(row[5] or 0.0)
                total_netto += tot
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                tree_data.insert("", "end", values=(
                    idx + 1, row[0], row[1], row[2], row[3], row[4],
                    f"Rp {tot:,.0f}".replace(",", ".")
                ), tags=(tag,))

        lbl_total_data.config(text=f"Total Data: {len(tree_data.get_children())} baris")
        if mode_idx == 5:
            lbl_total_netto.config(text=f"Total Qty: {total_qty:g}  |  Total Netto: Rp {total_netto:,.0f}".replace(",", "."))
        else:
            lbl_total_netto.config(text=f"Total: Rp {total_netto:,.0f}".replace(",", "."))

    # ============================================================
    # LOGIKA: DIALOG FILTER TANGGAL (PERSIS POS LAMA)
    # ============================================================
    def buka_dialog_filter(mode_idx):
        dialog = tk.Toplevel(parent)
        dialog.title("Parameter Laporan")
        dialog.geometry("560x420")
        dialog.configure(bg=BG_PANEL)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_force()
        
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - 280
        y = (parent.winfo_height() // 2) - 210
        dialog.geometry(f"+{x}+{y}")

        # --- BAGIAN 1: BATASAN ---
        frame_batasan = tk.LabelFrame(dialog, text="Batasan", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_batasan.pack(fill="x", padx=12, pady=8)
        
        var_batasan = tk.StringVar(value="Semua")
        rb_semua = tk.Radiobutton(frame_batasan, text="Semua Data", variable=var_batasan, value="Semua", bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 10))
        rb_semua.pack(side="left", padx=10, pady=5)
        rb_tertentu = tk.Radiobutton(frame_batasan, text="Tertentu", variable=var_batasan, value="Tertentu", bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 10))
        rb_tertentu.pack(side="left", padx=10, pady=5)
        
        e_tertentu = tk.Entry(frame_batasan, font=("Segoe UI", 10), bg=BG_INPUT, fg=BG_INPUT_FG, state="disabled", width=18)
        e_tertentu.pack(side="left", padx=10, pady=5)

        # --- BAGIAN 2: URUTKAN ---
        frame_urut = tk.LabelFrame(dialog, text="Diurutkan Berdasarkan", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_urut.pack(fill="x", padx=12, pady=8)
        
        var_urut = tk.StringVar(value="Tanggal & Waktu")
        opt_urut = ["Tanggal & Waktu", "No Faktur", "Total Nilai Terbesar"]
        cb_urut = ttk.Combobox(frame_urut, textvariable=var_urut, values=opt_urut, state="readonly", font=("Segoe UI", 10))
        cb_urut.pack(fill="x", padx=10, pady=5)

        # --- BAGIAN 3: TANGGAL ---
        frame_tgl = tk.LabelFrame(dialog, text="Periode Tanggal", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_tgl.pack(fill="x", padx=12, pady=8)
        
        f_tgl_row = tk.Frame(frame_tgl, bg=BG_PANEL)
        f_tgl_row.pack(pady=5)
        
        tk.Label(f_tgl_row, text="Dari:", bg=BG_PANEL, fg=FG_UTAMA, font=("Segoe UI", 10)).pack(side="left", padx=5)
        e_mulai = tk.Entry(f_tgl_row, font=("Segoe UI", 11), width=12, justify="center", bg=BG_INPUT, fg=BG_INPUT_FG)
        e_mulai.pack(side="left")
        e_mulai.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        tk.Label(f_tgl_row, text="s/d", bg=BG_PANEL, fg=FG_UTAMA, font=("Segoe UI", 10)).pack(side="left", padx=10)
        e_akhir = tk.Entry(f_tgl_row, font=("Segoe UI", 11), width=12, justify="center", bg=BG_INPUT, fg=BG_INPUT_FG)
        e_akhir.pack(side="left")
        e_akhir.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        lbl_selama = tk.Label(frame_tgl, text="Selama : 0 hari", bg=BG_PANEL, fg=FG_KUNING, font=("Segoe UI", 10, "bold"))
        lbl_selama.pack(pady=4)

        # --- BAGIAN 4: RINGKASAN & PROSES ---
        frame_ringkas = tk.Frame(dialog, bg=BG_PANEL)
        frame_ringkas.pack(fill="x", padx=12, pady=10)
        
        var_ringkas = tk.BooleanVar(value=False)
        cb_ringkas = tk.Checkbutton(frame_ringkas, text="Tampilkan Ringkasan Header", variable=var_ringkas, bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 10))
        cb_ringkas.pack(side="left", padx=5)

        def hitung_selama(ev=None):
            try:
                tgl1 = datetime.strptime(e_mulai.get().strip(), "%d-%m-%Y")
                tgl2 = datetime.strptime(e_akhir.get().strip(), "%d-%m-%Y")
                delta = (tgl2 - tgl1).days
                if delta < 0: delta = 0
                lbl_selama.config(text=f"Selama : {delta} hari")
            except:
                lbl_selama.config(text="Selama : ? hari")
                
        e_mulai.bind("<KeyRelease>", hitung_selama)
        e_akhir.bind("<KeyRelease>", hitung_selama)

        def toggle_tertentu():
            if var_batasan.get() == "Tertentu":
                e_tertentu.config(state="normal")
                e_tertentu.focus_set()
            else:
                e_tertentu.config(state="disabled")
                
        rb_semua.config(command=toggle_tertentu)
        rb_tertentu.config(command=toggle_tertentu)

        def _proses():
            try:
                tgl_m = datetime.strptime(e_mulai.get().strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
                tgl_a = datetime.strptime(e_akhir.get().strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                from ui.dialogs import info_kk
                info_kk(dialog, "Error Format", "Format tanggal harus DD-MM-YYYY", refs=refs)
                return

            dialog.destroy()
            tree_data.delete(*tree_data.get_children())
            lbl_loading.config(text="⏳ Sedang memuat data laporan...")
            
            t = threading.Thread(target=worker_thread, args=(mode_idx, tgl_m, tgl_a), daemon=True)
            t.start()

        btn_proses = tk.Button(frame_ringkas, text="  PROSES (ENTER)  ", font=("Segoe UI", 10, "bold"), bg=FG_AKSEN, fg="white", command=_proses, cursor="hand2")
        btn_proses.pack(side="right", padx=5)
        
        btn_tidak = tk.Button(frame_ringkas, text=" BATAL (ESC) ", font=("Segoe UI", 10), bg=BG_INPUT, fg=FG_UTAMA, command=dialog.destroy, cursor="hand2")
        btn_tidak.pack(side="right", padx=5)

        rb_semua.bind("<Tab>", lambda e: rb_tertentu.focus_set() or "break")
        rb_tertentu.bind("<Tab>", lambda e: cb_urut.focus_set() or "break")
        cb_urut.bind("<Tab>", lambda e: e_mulai.focus_set() or "break")
        e_mulai.bind("<Tab>", lambda e: e_akhir.focus_set() or "break")
        e_akhir.bind("<Tab>", lambda e: cb_ringkas.focus_set() or "break")
        cb_ringkas.bind("<Tab>", lambda e: btn_tidak.focus_set() or "break")
        btn_tidak.bind("<Tab>", lambda e: btn_proses.focus_set() or "break")
        btn_proses.bind("<Tab>", lambda e: rb_semua.focus_set() or "break")
        
        dialog.bind("<Return>", lambda e: _proses())
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        rb_semua.focus_set()

    def pilih_menu(ev=None):
        sel = listbox_menu.curselection()
        if not sel: return
        current_mode["idx"] = sel[0]
        buka_dialog_filter(sel[0])

    def ganti_menu(menu):
        for lbl, m in menu_labels.items():
            if m == menu: lbl.config(bg=FG_AKSEN, fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else: lbl.config(bg=BG_HEADER_TOP, fg=FG_UTAMA, font=("Segoe UI", 10, "normal"))
        
        listbox_menu.delete(0, "end")
        if menu == "Kassa": 
            _tutup()
            return
        elif menu == "Laporan":
            for m in [
                "1. Kasir - Cara Bayar",
                "2. Kasir - Diskon / Refund / Void",
                "3. Kassa - Kasir - Shift", 
                "4. Rekonsiliasi Kas (Modal/Biaya)",
                "5. Daftar Refund / Retur",
                "6. Laporan Barang Laku", 
                "7. Per Nota Faktur"
            ]:
                listbox_menu.insert("end", m)
        elif menu == "Nota Penjualan":
            for m in ["1. Cari Faktur", "2. Cetak Ulang Struk (F12)", "3. Daftar Pending (F6)", "4. Batalkan Faktur (F2)"]:
                listbox_menu.insert("end", m)
        elif menu in ["Setup", "Data", "Info", "Keluar"]:
            listbox_menu.insert("end", f"Menu {menu} siap dikembangkan.")
            
        if listbox_menu.size() > 0:
            listbox_menu.selection_set(0)
            current_mode["idx"] = 0

    # ============================================================
    # 4. BINDING EVENT
    # ============================================================
    menus_bar = ["Kassa", "Setup", "Data", "Laporan", "Nota Penjualan", "Info", "Keluar"]
    for m in menus_bar:
        lbl = tk.Label(frame_header, text=m, font=("Segoe UI", 10), bg=BG_HEADER_TOP, fg=FG_UTAMA, padx=16, cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda e, m=m: ganti_menu(m))
        menu_labels[lbl] = m

    listbox_menu.bind("<<ListboxSelect>>", lambda e: None)
    listbox_menu.bind("<Return>", lambda e: pilih_menu())
    listbox_menu.bind("<Double-1>", lambda e: pilih_menu())

    # ============================================================
    # 5. JALANKAN PERTAMA KALI
    # ============================================================
    ganti_menu("Laporan")
    parent.after(100, lambda: listbox_menu.focus_set())
    parent.wait_window(frame_main)
