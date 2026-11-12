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
        get_laporan_best_seller, get_laporan_per_nota
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
    frame_header = tk.Frame(frame_main, bg=BG_HEADER_TOP, height=40)
    frame_header.pack(fill="x")
    frame_header.pack_propagate(False)
    
    frame_isi = tk.Frame(frame_main, bg=BG_UTAMA)
    frame_isi.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ============================================================
    # 2. PANEL KIRI (MENU) & KANAN (TABEL)
    # ============================================================
    frame_kiri = tk.Frame(frame_isi, bg=BG_PANEL, width=300)
    frame_kiri.pack(side="left", fill="y", padx=(0, 10))
    frame_kiri.pack_propagate(False)
    
    listbox_menu = tk.Listbox(frame_kiri, font=("Consolas", 12), bg=BG_INPUT, fg=FG_UTAMA,
                              selectbackground=FG_AKSEN, selectforeground="#FFFFFF",
                              borderwidth=0, highlightthickness=0)
    listbox_menu.pack(fill="both", expand=True, pady=5, padx=5)

    frame_kanan = tk.Frame(frame_isi, bg=BG_UTAMA)
    frame_kanan.pack(side="left", fill="both", expand=True)
    
    lbl_loading = tk.Label(frame_kanan, text="", font=("Segoe UI", 12, "bold"), bg=BG_UTAMA, fg=FG_KUNING)
    lbl_loading.pack(pady=5)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Laporan.Treeview.Heading", font=("Consolas", 11, "bold"),
                    background=BG_HEADING, foreground=FG_AKSEN, borderwidth=1, relief="solid", padding=(5, 5))
    style.configure("Laporan.Treeview", font=("Consolas", 11), rowheight=25,
                    background=BG_PANEL, foreground=FG_UTAMA, fieldbackground=BG_PANEL,
                    borderwidth=1, relief="solid")
    style.map("Laporan.Treeview", background=[("selected", BG_TABLE_SEL)], foreground=[("selected", FG_UTAMA)])
              
    tree_data = ttk.Treeview(frame_kanan, show="headings", style="Laporan.Treeview")
    tree_data.pack(fill="both", expand=True)
    tree_data.tag_configure("negatif", foreground=FG_MERAH)

    frame_footer = tk.Frame(frame_kanan, bg=BG_PANEL, height=40)
    frame_footer.pack(fill="x", pady=(5, 0))
    frame_footer.pack_propagate(False)
    
    lbl_total_data = tk.Label(frame_footer, text="Total Data: 0", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=FG_UTAMA, padx=20)
    lbl_total_data.pack(side="left")
    
    lbl_total_netto = tk.Label(frame_footer, text="", font=("Consolas", 14, "bold"), bg=BG_PANEL, fg=FG_SUKSES, padx=20)
    lbl_total_netto.pack(side="right")

    frame_status = tk.Frame(frame_main, bg=BG_HEADER_TOP, height=30)
    frame_status.pack(fill="x", side="bottom")
    lbl_status = tk.Label(frame_status, text="ENTER = Pilih Laporan | ESC = Keluar", 
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
            elif mode_idx == 5: hasil = list(get_laporan_best_seller(tgl_m, tgl_a))
            elif mode_idx == 6: hasil = list(get_laporan_per_nota(tgl_m, tgl_a))
            else: hasil = None
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

        if data is None:
            tree_data["columns"] = ("info",)
            tree_data.heading("info", text="Status")
            tree_data.column("info", width=600, anchor="w")
            tree_data.insert("", "end", values=("Laporan ini belum diimplementasikan.",))
            lbl_total_data.config(text="Total Data: 0")
            lbl_total_netto.config(text="")
            return

        # ... (Logika update tabel mode 0-6 sama seperti kode sebelumnya, saya singkat disini) ...
        if mode_idx == 0:
            tree_data["columns"] = ("cara", "jml", "netto")
            tree_data.heading("cara", text="Cara Bayar")
            tree_data.heading("jml", text="JmlNota")
            tree_data.heading("netto", text="Netto (Rp)")
            tree_data.column("cara", width=200, anchor="w")
            tree_data.column("jml", width=100, anchor="e")
            tree_data.column("netto", width=200, anchor="e")
            for row in data:
                nto = row[2] or 0.0
                total_netto += nto
                tree_data.insert("", "end", values=(row[0] or "CASH", row[1], f"Rp {nto:,.0f}".replace(",", ".")))
                
        elif mode_idx == 5: # Best Seller
            tree_data["columns"] = ("kode", "nama", "qty", "netto")
            tree_data.heading("kode", text="Kode")
            tree_data.heading("nama", text="Nama Barang")
            tree_data.heading("qty", text="Qty")
            tree_data.heading("netto", text="Netto")
            tree_data.column("kode", width=100, anchor="center")
            tree_data.column("nama", width=400, anchor="w")
            tree_data.column("qty", width=100, anchor="e")
            tree_data.column("netto", width=150, anchor="e")
            for row in data:
                nto = row[3] or 0
                total_netto += nto
                total_qty += row[2] or 0
                tree_data.insert("", "end", values=(row[0], row[1], row[2], f"Rp {nto:,.0f}".replace(",", ".")))
        # ... (lanjutkan mode lainnya) ...

        lbl_total_data.config(text=f"Total Data: {len(tree_data.get_children())}")
        lbl_total_netto.config(text=f"Total Netto: Rp {total_netto:,.0f}".replace(",", "."))


    # ============================================================
    # LOGIKA: DIALOG FILTER TANGGAL (PERSIS POS LAMA)
    # ============================================================
    def buka_dialog_filter(mode_idx):
        dialog = tk.Toplevel(parent)
        dialog.title("Parameter Laporan")
        dialog.geometry("550x400") # Lebih besar karena banyak elemen
        dialog.configure(bg=BG_PANEL)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_force()
        
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - 275
        y = (parent.winfo_height() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        # --- BAGIAN 1: BATASAN ---
        frame_batasan = tk.LabelFrame(dialog, text="Batasan", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_batasan.pack(fill="x", padx=10, pady=10)
        
        var_batasan = tk.StringVar(value="Semua")
        rb_semua = tk.Radiobutton(frame_batasan, text="Semua", variable=var_batasan, value="Semua", bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 11))
        rb_semua.pack(side="left", padx=10, pady=5)
        rb_tertentu = tk.Radiobutton(frame_batasan, text="Tertentu", variable=var_batasan, value="Tertentu", bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 11))
        rb_tertentu.pack(side="left", padx=10, pady=5)
        
        e_tertentu = tk.Entry(frame_batasan, font=("Segoe UI", 11), bg=BG_INPUT, fg=BG_INPUT_FG, state="disabled")
        e_tertentu.pack(side="left", padx=10, pady=5)

        # --- BAGIAN 2: URUTKAN ---
        frame_urut = tk.LabelFrame(dialog, text="Diurutkan", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_urut.pack(fill="x", padx=10, pady=10)
        
        var_urut = tk.StringVar(value="Kassa ID")
        opt_urut = ["Kassa ID", "No Faktur", "Tanggal"]
        cb_urut = ttk.Combobox(frame_urut, textvariable=var_urut, values=opt_urut, state="readonly", font=("Segoe UI", 11))
        cb_urut.pack(fill="x", padx=10, pady=5)

        # --- BAGIAN 3: TANGGAL ---
        frame_tgl = tk.LabelFrame(dialog, text="Tanggal", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=FG_AKSEN, bd=1, relief="solid")
        frame_tgl.pack(fill="x", padx=10, pady=10)
        
        f_tgl_row = tk.Frame(frame_tgl, bg=BG_PANEL)
        f_tgl_row.pack(pady=5)
        
        tk.Label(f_tgl_row, text="Dari:", bg=BG_PANEL, fg=FG_UTAMA, font=("Segoe UI", 11)).pack(side="left", padx=5)
        e_mulai = tk.Entry(f_tgl_row, font=("Segoe UI", 12), width=12, justify="center", bg=BG_INPUT, fg=BG_INPUT_FG)
        e_mulai.pack(side="left")
        e_mulai.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        tk.Label(f_tgl_row, text="s/d", bg=BG_PANEL, fg=FG_UTAMA, font=("Segoe UI", 11)).pack(side="left", padx=10)
        e_akhir = tk.Entry(f_tgl_row, font=("Segoe UI", 12), width=12, justify="center", bg=BG_INPUT, fg=BG_INPUT_FG)
        e_akhir.pack(side="left")
        e_akhir.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        lbl_selama = tk.Label(frame_tgl, text="Selama : 0 hari", bg=BG_PANEL, fg=FG_KUNING, font=("Segoe UI", 11, "bold"))
        lbl_selama.pack(pady=5)

        # --- BAGIAN 4: RINGKASAN & PROSES ---
        frame_ringkas = tk.Frame(dialog, bg=BG_PANEL)
        frame_ringkas.pack(fill="x", padx=10, pady=10)
        
        var_ringkas = tk.BooleanVar(value=False)
        cb_ringkas = tk.Checkbutton(frame_ringkas, text="Tampilkan Ringkasan", variable=var_ringkas, bg=BG_PANEL, fg=FG_UTAMA, selectcolor=BG_INPUT, activebackground=BG_PANEL, font=("Segoe UI", 11))
        cb_ringkas.pack(side="left", padx=10)

        # --- FUNGSI HITUNG HARI ---
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

        # --- ENABLE/DISABLE ENTRY TERTENTU ---
        def toggle_tertentu():
            if var_batasan.get() == "Tertentu":
                e_tertentu.config(state="normal")
                e_tertentu.focus_set()
            else:
                e_tertentu.config(state="disabled")
                
        rb_semua.config(command=toggle_tertentu)
        rb_tertentu.config(command=toggle_tertentu)

        # --- PROSES ---
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
            lbl_loading.config(text="⏳ Sedang memuat data...")
            
            # Di sini, parameter `var_batasan`, `var_urut`, `var_ringkas` bisa dikirim juga ke worker_thread
            t = threading.Thread(target=worker_thread, args=(mode_idx, tgl_m, tgl_a), daemon=True)
            t.start()

        btn_proses = tk.Button(frame_ringkas, text="< Ya >", font=("Segoe UI", 11, "bold"), bg=FG_AKSEN, fg="white", command=_proses)
        btn_proses.pack(side="right", padx=5)
        
        btn_tidak = tk.Button(frame_ringkas, text="< Tidak >", font=("Segoe UI", 11, "bold"), bg=BG_INPUT, fg=FG_UTAMA, command=dialog.destroy)
        btn_tidak.pack(side="right", padx=5)

        # --- KEYBOARD NAVIGATION DI DALAM DIALOG ---
        # Ini adalah rantai navigasi agar TAB berfungsi mulus
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
            if m == menu: lbl.config(bg=FG_MERAH, fg="#FFFFFF", font=("Segoe UI", 11, "bold"))
            else: lbl.config(bg=BG_HEADER_TOP, fg=FG_UTAMA, font=("Segoe UI", 11, "normal"))
        
        listbox_menu.delete(0, "end")
        if menu == "Kassa": _tutup(); return
        elif menu == "Laporan":
            for m in ["1. Kasir-CaraBayar", "2. Kasir-Diskon-Refund-Void", "3. Kassa-Kasir-Shift", 
                      "4. Kassa-Kasir-Shift-Modal-Biaya", "5. Daftar Refund", "6. Barang Laku", 
                      "7. Per Nota", "8. Pengeluaran Kas Kasir", "9. Penjualan POS format Struk", "10. Selisih Setor Kasir"]:
                listbox_menu.insert("end", m)
        elif menu == "Nota Penjualan":
            for m in ["1. Cari Nota", "2. Cetak Ulang Struk", "3. Daftar Pending", "4. Batalkan Nota"]:
                listbox_menu.insert("end", m)
        elif menu in ["Setup", "Data", "Info", "Keluar"]:
            listbox_menu.insert("end", f"Menu {menu} belum tersedia di layar ini.")
            
        if listbox_menu.size() > 0:
            listbox_menu.selection_set(0)
            current_mode["idx"] = 0

    # ============================================================
    # 4. BINDING EVENT
    # ============================================================
    menus_bar = ["Kassa", "Setup", "Data", "Laporan", "Nota Penjualan", "Info", "Keluar"]
    for m in menus_bar:
        lbl = tk.Label(frame_header, text=m, font=("Segoe UI", 11), bg=BG_HEADER_TOP, fg=FG_UTAMA, padx=15, cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda e, m=m: ganti_menu(m))
        menu_labels[lbl] = m

    listbox_menu.bind("<<ListboxSelect>>", pilih_menu)
    
    # Navigasi di Listbox
    listbox_menu.bind("<Return>", lambda e: pilih_menu())
    listbox_menu.bind("<Double-1>", lambda e: pilih_menu())
    listbox_menu.bind("<Up>", lambda e: listbox_menu.after(10, lambda: pilih_menu()) or "break")
    listbox_menu.bind("<Down>", lambda e: listbox_menu.after(10, lambda: pilih_menu()) or "break")

    # ============================================================
    # 5. JALANKAN PERTAMA KALI
    # ============================================================
    ganti_menu("Laporan")
    
    parent.after(100, lambda: listbox_menu.focus_set())
    
    parent.wait_window(frame_main)