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
    FONT_TOTAL,
    FONT_KECIL,
    FONT_HEADER
)
from database.queries import cari_barang_by_kode, cari_barang_by_nama

def auto_select_row_terakhir(refs):
    """
    Memilih baris terakhir di Treeview keranjang dan melakukan scroll otomatis.
    """
    tree = refs.get("tree")
    if not tree:
        return
    children = tree.get_children()
    if children:
        target = children[-1]
        tree.selection_set(target)
        tree.focus(target)
        tree.see(target)

def update_footer_total(root, refs, state):
    """
    Alias sinkronisasi perhitungan total keranjang belanja.
    """
    perbarui_tampilan_keranjang(root, refs, state)

def perbarui_tampilan_keranjang(root, refs, state, pilih_terakhir=False):
    """
    Merender ulang seluruh baris tabel keranjang dan memperbarui label Total Qty serta Grand Total.
    """
    tree = refs.get("tree")
    if not tree:
        return
        
    selected_idx = -1
    current_sel = tree.selection()
    if current_sel and not pilih_terakhir:
        try:
            selected_idx = tree.index(current_sel[0])
        except Exception:
            selected_idx = -1
            
    for row in tree.get_children():
        tree.delete(row)
        
    total_qty = 0.0
    grand_total = 0.0
    keranjang = state.get("keranjang", [])
    
    for i, item in enumerate(keranjang):
        harga = item["harga"]
        qty = item["qty"]
        diskon_pct = item.get("diskon_pct", 0.0)
        diskon_rp = item.get("diskon_rp", 0.0)
        potongan_pct = harga * diskon_pct / 100.0
        subtotal = (harga - potongan_pct) * qty - diskon_rp
        total_qty += qty
        grand_total += subtotal
        
        tag = "minus" if qty < 0 else ("evenrow" if i % 2 == 0 else "oddrow")
        nama_display = item["nama"][:30].upper()
        
        # [FIX] Tampilkan persentase di kolom DSK meskipun input berupa Rupiah
        if diskon_pct > 0:
            dsk_tampil = f"{diskon_pct:.2f}%"
        elif diskon_rp > 0 and harga > 0:
            persen = (diskon_rp / harga) * 100
            dsk_tampil = f"{persen:.2f}%"
        else:
            dsk_tampil = ""
        
        tree.insert("", "end", values=(
            f"{i+1}",  # NO
            f"{item['kode']:8}",
            f"{nama_display:30}",
            f"{harga:>10,.0f}".replace(",", "."),
            f"{dsk_tampil:>8}",
            f"{qty:>6.2f} {item.get('satuan', 'PC'):<3}",
            f"{subtotal:>13,.0f}".replace(",", ".")
        ), tags=(tag,))
        
    children = tree.get_children()
    if children:
        if pilih_terakhir:
            target_idx = len(children) - 1
        else:
            if 0 <= selected_idx < len(children):
                target_idx = selected_idx
            elif selected_idx >= len(children):
                target_idx = len(children) - 1
            else:
                target_idx = 0
        target_item = children[target_idx]
        tree.selection_set(target_item)
        tree.focus(target_item)
        tree.see(target_item)
        
    diskon_global_rp = state.get("diskon_global_rp", 0.0)
    diskon_global_persen = state.get("diskon_global_persen", 0.0)
    biaya_tambahan = state.get("biaya_tambahan", 0.0)
    
    if grand_total != 0:
        grand_total = grand_total - diskon_global_rp - (grand_total * diskon_global_persen / 100.0) + biaya_tambahan
        
    lbl_total_qty = refs.get("lbl_total_qty")
    if lbl_total_qty and lbl_total_qty.winfo_exists():
        lbl_total_qty.config(text=f"TOTAL QTY : {total_qty:10.2f}")
        
    lbl_grand_total = refs.get("lbl_grand_total")
    if lbl_grand_total and lbl_grand_total.winfo_exists():
        if grand_total < 0:
            lbl_grand_total.config(text=f"{grand_total:,.0f}".replace(",", "."), fg=FG_MERAH)
        elif grand_total > 0:
            lbl_grand_total.config(text=f"{grand_total:,.0f}".replace(",", "."), fg=FG_SUKSES)
        else:
            lbl_grand_total.config(text="0", fg=FG_KUNING)

def tambah_ke_keranjang(kode, nama, harga, qty=1.0, satuan="PC", root=None, refs=None, state=None):
    """
    Menambahkan item baru atau menambah qty item yang sudah ada di keranjang.
    Mendukung nilai qty negatif untuk refund / retur barang.
    """
    keranjang = state.get("keranjang", [])
    found = False
    for item in keranjang:
        if item["kode"] == kode:
            item["qty"] += qty
            found = True
            break
    if not found:
        keranjang.append({
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "diskon_pct": 0.0,
            "diskon_rp": 0.0,
            "qty": qty,
            "satuan": satuan
        })
    state["keranjang"] = keranjang
    if root and refs:
        perbarui_tampilan_keranjang(root, refs, state, pilih_terakhir=True)
        
        # [FIX BUG 1] Paksa fokus ke tree setelah update
        tree = refs.get("tree")
        if tree:
            auto_select_row_terakhir(refs)
            tree.focus_set()

def input_barang_barcode(event, root, refs, state):
    """
    Memproses teks dari entry barcode:
    - Mendukung input qty negatif langsung (misal: '-2' atau '-0.5') untuk mengubah item aktif di tabel.
    - Format 'kode qty' (misal: '1001 -2') untuk refund item tertentu.
    - Kode angka barcode/PLU vs pencarian nama.
    """
    from ui.dialogs import info_kk
    
    entry = refs.get("entry_barcode")
    if not entry:
        return "break"
        
    teks = entry.get().strip()
    entry.delete(0, tk.END)
    if "lbl_preview" in refs and refs["lbl_preview"].winfo_exists():
        refs["lbl_preview"].config(text="")
        
    if not teks:
        perbarui_tampilan_keranjang(root, refs, state)
        return "break"
        
    parts = teks.split()
    
    # Cek jika kasir langsung mengetik angka negatif murni di barcode entry (misal: -2 atau -0.5)
    if len(parts) == 1 and parts[0].startswith("-") and parts[0][1:].replace(".", "", 1).isdigit():
        tree = refs.get("tree")
        if tree:
            sel = tree.selection()
            if sel:
                idx = tree.index(sel[0])
                keranjang = state.get("keranjang", [])
                if 0 <= idx < len(keranjang):
                    try:
                        keranjang[idx]["qty"] = float(parts[0])
                        perbarui_tampilan_keranjang(root, refs, state)
                        
                        # [FIX BUG 1] Fokus ke tree
                        auto_select_row_terakhir(refs)
                        tree.focus_set()
                        
                        return "break"
                    except ValueError:
                        pass
                        
    kode = parts[0]
    qty = 1.0
    if len(parts) >= 2:
        try:
            qty = float(parts[1])
        except ValueError:
            qty = 1.0
            
    is_angka = kode.replace(".", "").replace("-", "").isdigit()
    
    try:
        if is_angka:
            row = cari_barang_by_kode(kode)
            if row:
                tambah_ke_keranjang(row[0], row[1] or "TANPA NAMA", float(row[2] or 0), qty, row[3] or "PC", root, refs, state)
                tree = refs.get("tree")
                if tree:
                    # [FIX BUG 1] Fokus ke tree
                    auto_select_row_terakhir(refs)
                    tree.focus_set()
            else:
                info_kk(root, "Error", f"Barang '{kode}' tidak ditemukan!", refs=refs)
        else:
            rows = cari_barang_by_nama(kode, limit=50)
            if not rows:
                info_kk(root, "Error", f"Barang '{kode}' tidak ditemukan!", refs=refs)
            elif len(rows) == 1:
                r = rows[0]
                tambah_ke_keranjang(r[0], r[1] or "TANPA NAMA", float(r[2] or 0), qty, r[3] or "PC", root, refs, state)
                tree = refs.get("tree")
                if tree:
                    # [FIX BUG 1] Fokus ke tree
                    auto_select_row_terakhir(refs)
                    tree.focus_set()
            else:
                from handlers.cari_barang import cari_barang_dialog
                cari_barang_dialog(event, root, refs, state, initial_keyword=kode)
    except Exception as e:
        info_kk(root, "Error", f"Database error: {e}", refs=refs)
        
    return "break"

# Alias sesuai spesifikasi fungsi
tambah_barang_ke_keranjang = input_barang_barcode

def update_footer_preview(event, root, refs, state):
    """
    Menampilkan kalkulasi live preview di footer saat kasir mengetik di entry input.
    """
    if event and event.keysym in ("Return", "KP_Enter"):
        return
    entry = refs.get("entry_barcode")
    lbl_preview = refs.get("lbl_preview")
    if not entry or not lbl_preview or not lbl_preview.winfo_exists():
        return
        
    teks = entry.get().strip()
    if not teks:
        lbl_preview.config(text="")
        return
        
    try:
        parts = teks.split()
        kode = parts[0]
        qty = 1.0
        if len(parts) >= 2:
            try:
                qty = float(parts[1])
            except ValueError:
                qty = 1.0
                
        is_angka = kode.replace(".", "").replace("-", "").isdigit()
        if is_angka:
            row = cari_barang_by_kode(kode)
            if row:
                nama = row[1] or "TANPA NAMA"
                harga = float(row[2] or 0)
                sat = row[3] or "PC"
                subtotal = harga * qty
                lbl_preview.config(
                    text=f"  ⟳ {nama[:30]} × {qty:g} {sat} = Rp {subtotal:,.0f}".replace(",", "."),
                    fg=FG_SUKSES
                )
            else:
                lbl_preview.config(text=f"  ⟳ kode '{kode}' belum terdaftar", fg=FG_KUNING)
        else:
            rows = cari_barang_by_nama(kode, limit=1)
            if rows:
                r = rows[0]
                nama = r[1] or "TANPA NAMA"
                harga = float(r[2] or 0)
                sat = r[3] or "PC"
                subtotal = harga * qty
                lbl_preview.config(
                    text=f"  ⟳ {nama[:30]} × {qty:g} {sat} = Rp {subtotal:,.0f}  (nama)".replace(",", "."),
                    fg=FG_SUKSES
                )
            else:
                lbl_preview.config(text=f"  ⟳ nama '{kode}' belum terdaftar", fg=FG_KUNING)
    except Exception as e:
        print(f"[preview error] {e}")

# ============================================================
# OVERLAY RUBAH JUMLAH BARANG (*)
# ============================================================

def tampilkan_overlay_qty(event, root, refs, state):
    """
    Membuka modal dialog kecil di tengah untuk merubah qty item terpilih (hotkey * atau tombol -).
    Entry dikosongkan saat dibuka; user langsung ketik nilai baru (positif/negatif).
    Qty lama hanya ditampilkan sebagai info di label terpisah.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    tree = refs.get("tree")
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
    state["overlay_qty_idx"] = idx
    
    if state.get("overlay_qty") and state["overlay_qty"].winfo_exists():
        batal_overlay_qty(event, root, refs, state)
        
    shadow_outer, shadow_inner, container = buat_dual_shadow_panel(
        root, width=500, height=340, relx=0.5, rely=0.5, anchor="center"
    )
    
    # [FIX] Tidak menggunakan grab_set agar background tidak terkunci
    state["overlay_qty"] = container
    state["_overlay_shadow_outer"] = shadow_outer
    state["_overlay_shadow_inner"] = shadow_inner
    
    tk.Label(container, text="RUBAH JUMLAH BARANG", font=FONT_JUDUL,
             bg=BG_PANEL, fg=FG_KUNING).pack(pady=(20, 12))
             
    frame_info = tk.Frame(container, bg=BG_INPUT, highlightthickness=0)
    frame_info.pack(fill="x", padx=25, pady=(0, 12))
    tk.Label(frame_info, text=item["nama"][:40].upper(), font=FONT_BESAR,
             bg=BG_INPUT, fg=FG_UTAMA, anchor="w").pack(fill="x", padx=12, pady=(8, 0))
    frame_info_row2 = tk.Frame(frame_info, bg=BG_INPUT)
    frame_info_row2.pack(fill="x", padx=12, pady=(0, 8))
    tk.Label(frame_info_row2, text=f"Rp {item['harga']:,.0f}".replace(",", "."),
             font=FONT_BESAR, bg=BG_INPUT, fg=FG_AKSEN, anchor="w").pack(side="left")
    tk.Label(frame_info_row2, text=f"Qty: {item['qty']:.2f} {item.get('satuan', 'PC')}",
             font=FONT_BESAR, bg=BG_INPUT, fg=FG_AKSEN, anchor="e").pack(side="right")
             
    frame_input = tk.Frame(container, bg=BG_PANEL)
    frame_input.pack(pady=(0, 6))
    tk.Label(frame_input, text="QTY BARU:", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA).pack(side="left", padx=(0, 10))
             
    entry_qty = tk.Entry(frame_input, font=FONT_BESAR, width=15,
                         bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN,
                         justify="right", relief="flat", bd=6,
                         highlightbackground=FG_AKSEN, highlightthickness=1)
    entry_qty.pack(side="left")
    state["overlay_qty_entry"] = entry_qty
    refs["entry_qty"] = entry_qty
    
    # [FIX BUG 2] Pastikan entry benar-benar bersih saat dideklarasikan
    entry_qty.delete(0, tk.END)
    
    # Hint qty lama sebagai info (bukan di entry)
    tk.Label(container,
             text=f"(qty saat ini: {item['qty']:g} {item.get('satuan', 'PC')})",
             font=FONT_KECIL, bg=BG_PANEL, fg=FG_ABU).pack(pady=(0, 8))
    
    harga = item["harga"]
    diskon_pct = item.get("diskon_pct", 0.0)
    diskon_rp = item.get("diskon_rp", 0.0)
    subtotal_awal = (harga - harga * diskon_pct / 100.0) * item["qty"] - diskon_rp
    warna_awal = FG_MERAH if subtotal_awal < 0 else FG_KUNING
    lbl_total = tk.Label(container, text=f"Rp {subtotal_awal:,.0f}".replace(",", "."),
                         font=FONT_TOTAL, bg=BG_PANEL, fg=warna_awal)
    lbl_total.pack(pady=(0, 10))
    state["overlay_qty_lbl_total"] = lbl_total
    
    tk.Label(container, text="ENTER  OK   |   ESC  BATAL",
             font=FONT_KECIL, bg=BG_PANEL, fg=FG_ABU).pack(pady=(0, 12))
             
    entry_qty.bind("<KeyRelease>", lambda e: update_preview_overlay_qty(e, root, refs, state))
    entry_qty.bind("<Return>", lambda e: apply_overlay_qty(root, refs, state))
    container.bind("<Return>", lambda e: apply_overlay_qty(root, refs, state))
    container.bind("<Escape>", lambda e: batal_overlay_qty(e, root, refs, state))
    
    # Fokus langsung ke entry
    entry_qty.focus_set()
    entry_qty.focus_force()
    
    return "break"

# Alias sesuai brief
ubah_qty_item = tampilkan_overlay_qty
handle_ketik_bintang_di_tree = tampilkan_overlay_qty

def update_preview_overlay_qty(event, root, refs, state):
    """
    Kalkulasi subtotal live saat angka baru diketik di overlay perubahan Qty.
    Mendukung:
    - Angka positif ("5")
    - Angka negatif ("-2", "-4")
    - Desimal ("-0.5", "1.25")
    - In-progress typing ("-", ".", "-.") → tidak crash, tampilkan qty lama
    """
    entry_qty = state.get("overlay_qty_entry")
    lbl_total = state.get("overlay_qty_lbl_total")
    idx = state.get("overlay_qty_idx")
    keranjang = state.get("keranjang", [])
    
    if not entry_qty or not entry_qty.winfo_exists() or idx is None:
        return
    if idx < 0 or idx >= len(keranjang):
        return
        
    try:
        teks = entry_qty.get().strip()
        item = keranjang[idx]
        harga = item["harga"]
        diskon_pct = item.get("diskon_pct", 0.0)
        diskon_rp = item.get("diskon_rp", 0.0)
        
        # Kasus in-progress typing atau kosong: tampilkan qty lama
        if teks in ("", "-", ".", "-."):
            subtotal = (harga - harga * diskon_pct / 100.0) * item["qty"] - diskon_rp
            warna = FG_MERAH if subtotal < 0 else FG_KUNING
            lbl_total.config(text=f"Rp {subtotal:,.0f}".replace(",", "."), fg=warna)
            return
        
        # Coba parse sebagai float (bisa handle "-2", "5", "-0.5")
        qty_baru = float(teks)
        subtotal = (harga - harga * diskon_pct / 100.0) * qty_baru - diskon_rp
        warna_preview = FG_MERAH if subtotal < 0 else FG_KUNING
        lbl_total.config(text=f"Rp {subtotal:,.0f}".replace(",", "."), fg=warna_preview)
    except ValueError:
        # String tidak valid untuk float (misal "--", "1.2.3")
        lbl_total.config(text="Angka tidak valid", fg=FG_MERAH)

def apply_overlay_qty(root, refs, state):
    """
    Menerapkan perubahan Qty ke item keranjang dan memperbarui tampilan.
    Kalau entry kosong atau in-progress typing → tutup dialog tanpa perubahan.
    """
    entry_qty = state.get("overlay_qty_entry")
    lbl_total = state.get("overlay_qty_lbl_total")
    idx = state.get("overlay_qty_idx")
    keranjang = state.get("keranjang", [])
    
    if not entry_qty or not entry_qty.winfo_exists():
        return
        
    teks = entry_qty.get().strip()
    
    # Kalau kosong atau in-progress typing → tidak ada perubahan
    if teks in ("", "-", ".", "-."):
        _bersihkan_overlay_qty_state(root, refs, state)
        return
    
    try:
        qty_baru = float(teks)
    except ValueError:
        if lbl_total and lbl_total.winfo_exists():
            lbl_total.config(text="Angka tidak valid", fg=FG_MERAH)
        return
        
    if idx is not None and 0 <= idx < len(keranjang):
        keranjang[idx]["qty"] = qty_baru
        
    _bersihkan_overlay_qty_state(root, refs, state)

def _bersihkan_overlay_qty_state(root, refs, state):
    """Helper internal: tutup dialog + bersihkan state."""
    container = state.get("overlay_qty")
    if container and container.winfo_exists():
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        
    for key in ("_overlay_shadow_outer", "_overlay_shadow_inner"):
        shadow = state.get(key)
        if shadow and shadow.winfo_exists():
            shadow.destroy()
            
    state["overlay_qty"] = None
    state["overlay_qty_entry"] = None
    state["overlay_qty_lbl_total"] = None
    state["overlay_qty_idx"] = None
    refs.pop("entry_qty", None)
    
    perbarui_tampilan_keranjang(root, refs, state)
    tree = refs.get("tree")
    if tree:
        root.after(10, lambda: tree.focus_set())

def batal_overlay_qty(event, root, refs, state):
    """
    Membatalkan perubahan Qty dan menutup dialog overlay.
    """
    container = state.get("overlay_qty")
    if container and container.winfo_exists():
        try:
            container.grab_release()
        except Exception:
            pass
        container.destroy()
        
    for key in ("_overlay_shadow_outer", "_overlay_shadow_inner"):
        shadow = state.get(key)
        if shadow and shadow.winfo_exists():
            shadow.destroy()
            
    state["overlay_qty"] = None
    state["overlay_qty_entry"] = None
    state["overlay_qty_lbl_total"] = None
    state["overlay_qty_idx"] = None
    refs.pop("entry_qty", None)
    
    tree = refs.get("tree")
    if tree:
        root.after(10, lambda: tree.focus_set())
    return "break"

# ============================================================
# VOID & REFUND ITEM (TUGAS C2)
# ============================================================

def void_item(event, root, refs, state):
    """
    Menghapus item terpilih dari keranjang (F2).
    Mendukung navigasi panah kiri/kanan dan efek kedip pada tombol.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    tree = refs.get("tree")
    if not tree:
        return "break"
    sel = tree.selection()
    if not sel:
        info_kk(root, "Perhatian", "Pilih item dulu!", refs=refs)
        return "break"
        
    idx = tree.index(sel[0])
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return "break"
    nama = keranjang[idx]["nama"]
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=450, height=250, relx=0.5, rely=0.5, anchor="center"
    )
    # [FIX] Tidak ada grab_set
    
    tk.Label(dlg, text="HAPUS ITEM", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_KUNING).pack(pady=(20, 10))
    tk.Label(dlg, text=f"Hapus '{nama}' dari keranjang?", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(pady=10)
    
    frame_btn = tk.Frame(dlg, bg=BG_PANEL)
    frame_btn.pack(pady=20)
    
    # State untuk navigasi dan blinking
    pilihan = {"idx": 0}  # 0 = HAPUS, 1 = BATAL
    blink_state = {"on": True}
    blink_job = {"id": None}
    
    btn_hapus = tk.Label(frame_btn, text="HAPUS", font=FONT_BESAR, bg=BG_INPUT, fg=FG_MERAH, padx=20, pady=5, cursor="hand2")
    btn_hapus.pack(side="left", padx=10)
    
    btn_batal = tk.Label(frame_btn, text="BATAL", font=FONT_BESAR, bg=BG_INPUT, fg=FG_UTAMA, padx=20, pady=5, cursor="hand2")
    btn_batal.pack(side="left", padx=10)
    
    def update_tampilan():
        if pilihan["idx"] == 0:
            btn_hapus.config(bg=FG_MERAH if blink_state["on"] else BG_INPUT)
            btn_batal.config(bg=BG_INPUT)
        else:
            btn_hapus.config(bg=BG_INPUT)
            btn_batal.config(bg=FG_AKSEN if blink_state["on"] else BG_INPUT)
            
    def blink_loop():
        blink_state["on"] = not blink_state["on"]
        update_tampilan()
        blink_job["id"] = root.after(300, blink_loop)  # 300ms interval
        
    def stop_blink():
        if blink_job["id"]:
            try:
                root.after_cancel(blink_job["id"])
            except Exception:
                pass
            blink_job["id"] = None
            
    def lakukan_hapus(ev=None):
        stop_blink()
        del keranjang[idx]
        perbarui_tampilan_keranjang(root, refs, state)
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
        return "break"
        
    def batal(ev=None):
        stop_blink()
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
        return "break"
        
    def pindah_kanan(ev=None):
        pilihan["idx"] = 1
        update_tampilan()
        return "break"
        
    def pindah_kiri(ev=None):
        pilihan["idx"] = 0
        update_tampilan()
        return "break"
        
    def eksekusi_enter(ev=None):
        if pilihan["idx"] == 0:
            lakukan_hapus()
        else:
            batal()
        return "break"
        
    # Binding mouse
    btn_hapus.bind("<Button-1>", lambda e: lakukan_hapus())
    btn_batal.bind("<Button-1>", lambda e: batal())
    
    # Binding keyboard
    dlg.bind("<Escape>", lambda e: batal())
    dlg.bind("<Left>", pindah_kiri)
    dlg.bind("<Right>", pindah_kanan)
    dlg.bind("<Return>", eksekusi_enter)
    
    dlg.focus_force()
    
    # Mulai blink
    blink_loop()
    
    return "break"

def refund_item(event, root, refs, state):
    """
    Hotkey [-]: Toggle item menjadi refund (qty negatif) dan LANGSUNG memindahkan fokus
    ke input Qty di overlay dialog tanpa butuh mouse. Menerima input negatif langsung.
    """
    from ui.dialogs import info_kk
    
    tree = refs.get("tree")
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
        
    # Jika qty positif, jadikan negatif
    if keranjang[idx]["qty"] > 0:
        keranjang[idx]["qty"] = -keranjang[idx]["qty"]
        
    perbarui_tampilan_keranjang(root, refs, state)
    
    # Langsung buka overlay qty dengan fokus keyboard 100% pada entry angka
    tampilkan_overlay_qty(event, root, refs, state)
    
    return "break"

def retur_item(event, root, refs, state):
    """
    Dialog retur item (Shift+F3) untuk mengurangi sebagian qty item.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    tree = refs.get("tree")
    if not tree:
        return "break"
    sel = tree.selection()
    if not sel:
        info_kk(root, "Perhatian", "Pilih item dulu!", refs=refs)
        return "break"
        
    idx = tree.index(sel[0])
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return "break"
    item = keranjang[idx]
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=500, height=280, relx=0.5, rely=0.5, anchor="center"
    )
    dlg.focus_force()
        
    tk.Label(dlg, text="< RETUR ITEM >", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_AKSEN).pack(pady=10)
    tk.Label(dlg, text=f"KODE : {item['kode']}\nNAMA : {item['nama'][:40].upper()}\nQTY SAAT INI: {item['qty']:.2f}",
             font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(anchor="w", padx=30, pady=2)
             
    frame = tk.Frame(dlg, bg=BG_PANEL)
    frame.pack(pady=15)
    tk.Label(frame, text="JUMLAH YANG DIRETUR:", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    e = tk.Entry(frame, font=FONT_BESAR, width=10, bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e.grid(row=0, column=1, padx=10, pady=5)
    e.focus()
    
    def simpan(ev=None):
        try:
            jumlah = float(e.get().strip() or 0)
            if jumlah <= 0:
                info_kk(dlg, "Error", "Jumlah retur harus > 0!", refs=refs)
                return
            item["qty"] -= jumlah
            perbarui_tampilan_keranjang(root, refs, state)
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            if tree:
                root.after(10, lambda: tree.focus_set())
        except ValueError:
            info_kk(dlg, "Error", "Nilai tidak valid!", refs=refs)
            
    def batal(ev=None):
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
            
    e.bind("<Return>", simpan)
    dlg.bind("<Escape>", batal)
    return "break"

# ============================================================
# NAVIGASI KEYBOARD ENTRY ↔ TREE
# ============================================================

def fokus_ke_tree_dari_entry(event, root, refs, state):
    """
    Navigasi tombol Panah Bawah (↓) dari input barcode ke baris tabel keranjang.
    """
    tree = refs.get("tree")
    if not tree:
        return "break"
    children = tree.get_children()
    if children:
        sel = tree.selection()
        if sel:
            tree.focus_set()
            tree.focus(sel[0])
            tree.see(sel[0])
        else:
            tree.selection_set(children[-1])
            tree.focus(children[-1])
            tree.see(children[-1])
            tree.focus_set()
    return "break"

def pindah_ke_atas(event, root, refs, state):
    """
    Navigasi tombol Panah Atas (↑) di tabel; jika di baris paling atas, kembali ke entry barcode.
    """
    tree = refs.get("tree")
    entry_barcode = refs.get("entry_barcode")
    if not tree:
        return "break"
    children = tree.get_children()
    if not children:
        return "break"
    sel = tree.selection()
    if sel:
        idx = children.index(sel[0])
        if idx > 0:
            tree.selection_set(children[idx - 1])
            tree.focus(children[idx - 1])
            tree.see(children[idx - 1])
        else:
            if entry_barcode:
                entry_barcode.focus_set()
    else:
        tree.selection_set(children[0])
        tree.focus(children[0])
    return "break"

def pindah_ke_bawah(event, root, refs, state):
    """
    Navigasi tombol Panah Bawah (↓) di tabel belanja.
    """
    tree = refs.get("tree")
    if not tree:
        return "break"
    children = tree.get_children()
    if not children:
        return "break"
    sel = tree.selection()
    if sel:
        idx = children.index(sel[0])
        if idx < len(children) - 1:
            tree.selection_set(children[idx + 1])
            tree.focus(children[idx + 1])
            tree.see(children[idx + 1])
    else:
        tree.selection_set(children[0])
        tree.focus(children[0])
    return "break"

# ============================================================
# FITUR ITEM LAIN: OPEN PLU, UBAH HARGA, UBAH SATUAN
# ============================================================

def open_plu(event, root, refs, state):
    """
    Menambahkan item manual bebas / Open PLU (F3).
    """
    keranjang = state.get("keranjang", [])
    opn_count = sum(1 for item in keranjang if item["kode"].startswith("OPN"))
    kode_baru = f"OPN{opn_count + 1:03d}"
    keranjang.append({
        "kode": kode_baru,
        "nama": "BARANG",
        "harga": 0.0,
        "diskon_pct": 0.0,
        "diskon_rp": 0.0,
        "qty": 1.0,
        "satuan": "PC",
        "is_manual": True
    })
    perbarui_tampilan_keranjang(root, refs, state, pilih_terakhir=True)
    idx = len(keranjang) - 1
    edit_item_manual(idx, root, refs, state)
    return "break"

def edit_item_manual(idx, root, refs, state):
    """
    Modal dialog edit detail item manual OPNxxx.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return
    item = keranjang[idx]
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=500, height=350, relx=0.5, rely=0.5, anchor="center"
    )
    dlg.focus_force()
        
    tk.Label(dlg, text="<OPEN PENJUALAN> - ESCAPE=BATAL, ENTER=SIMPAN", font=FONT_BESAR,
             bg=BG_PANEL, fg="#E8ECF5").pack(fill="x", pady=5)
    frame = tk.Frame(dlg, bg=BG_PANEL)
    frame.pack(pady=15, padx=20, fill="x")
    
    tk.Label(frame, text="NAMA BARANG :", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=15, anchor="w").grid(row=0, column=0, sticky="w", pady=5)
    e_nama = tk.Entry(frame, font=FONT_BESAR, width=30, bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_nama.grid(row=0, column=1, pady=5)
    e_nama.insert(0, item["nama"])
    e_nama.focus()
    e_nama.selection_range(0, tk.END)
    
    tk.Label(frame, text="HARGA (Rp) :", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=15, anchor="w").grid(row=1, column=0, sticky="w", pady=5)
    e_hrg = tk.Entry(frame, font=FONT_BESAR, width=15, justify="right", bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_hrg.grid(row=1, column=1, sticky="w", pady=5)
    if item["harga"] > 0:
        e_hrg.insert(0, str(int(item["harga"])))
        
    tk.Label(frame, text="DISKON (%) :", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=15, anchor="w").grid(row=2, column=0, sticky="w", pady=5)
    e_dsk = tk.Entry(frame, font=FONT_BESAR, width=10, justify="right", bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_dsk.grid(row=2, column=1, sticky="w", pady=5)
    if item.get("diskon_pct", 0) > 0:
        e_dsk.insert(0, str(item["diskon_pct"]))
        
    tk.Label(frame, text="QTY :", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=15, anchor="w").grid(row=3, column=0, sticky="w", pady=5)
    e_qty = tk.Entry(frame, font=FONT_BESAR, width=10, justify="right", bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_qty.grid(row=3, column=1, sticky="w", pady=5)
    e_qty.insert(0, f"{item['qty']:.2f}")
    
    def simpan(ev=None):
        try:
            item["nama"] = e_nama.get().strip() or "BARANG"
            item["harga"] = float(e_hrg.get().strip().replace(".", "") or 0)
            item["diskon_pct"] = float(e_dsk.get().strip() or 0)
            item["diskon_rp"] = 0.0
            item["qty"] = float(e_qty.get().strip() or 1)
            perbarui_tampilan_keranjang(root, refs, state)
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
                root.after(10, lambda: refs["entry_barcode"].focus())
        except ValueError:
            info_kk(dlg, "Error", "Masukkan angka valid!", refs=refs)
            
    def batal(ev=None):
        keranjang.pop(idx)
        perbarui_tampilan_keranjang(root, refs, state)
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            root.after(10, lambda: refs["entry_barcode"].focus())
            
    e_nama.bind("<Return>", lambda e: e_hrg.focus())
    e_hrg.bind("<Return>", lambda e: e_dsk.focus())
    e_dsk.bind("<Return>", lambda e: e_qty.focus())
    e_qty.bind("<Return>", simpan)
    dlg.bind("<Escape>", batal)

def ubah_harga_transaksi(event, root, refs, state):
    """
    Modal dialog ubah harga transaksi item terpilih (F4), menampilkan harga lama dan harga baru.
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    tree = refs.get("tree")
    if not tree:
        return "break"
    sel = tree.selection()
    if not sel:
        info_kk(root, "Perhatian", "Pilih item dulu!", refs=refs)
        return "break"
        
    idx = tree.index(sel[0])
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return "break"
    item = keranjang[idx]
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=420, height=220, relx=0.5, rely=0.5, anchor="center"
    )
    dlg.focus_force()
        
    tk.Label(dlg, text="< UBAH HARGA >", font=FONT_JUDUL, bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(15, 5))
    tk.Label(dlg, text=f"{item['nama'][:35].upper()}\nHARGA LAMA: Rp {item['harga']:,.0f}".replace(",", "."),
             font=FONT_BESAR, bg=BG_PANEL, fg=FG_KUNING).pack(pady=5)
    tk.Label(dlg, text="HARGA BARU (Rp):", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(pady=4)
    
    e = tk.Entry(dlg, font=FONT_BESAR, width=15, justify="right",
                 bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e.pack(pady=5)
    e.focus()
    e.insert(0, str(int(item["harga"])))
    e.selection_range(0, tk.END)
    
    def simpan(ev=None):
        try:
            harga_baru = float(e.get().strip().replace(".", "") or 0)
            item["harga"] = harga_baru
            perbarui_tampilan_keranjang(root, refs, state)
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            if tree:
                root.after(10, lambda: tree.focus_set())
        except ValueError:
            info_kk(dlg, "Error", "Masukkan angka valid!", refs=refs)
            
    def batal(ev=None):
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
            
    e.bind("<Return>", simpan)
    dlg.bind("<Escape>", batal)
    return "break"

def ubah_satuan(event, root, refs, state):
    """
    Modal dialog ubah satuan item terpilih (Ctrl+F12).
    """
    from ui.dialogs import info_kk
    from ui.components import buat_dual_shadow_panel
    
    tree = refs.get("tree")
    if not tree:
        return "break"
    sel = tree.selection()
    if not sel:
        info_kk(root, "Perhatian", "Pilih item dulu!", refs=refs)
        return "break"
        
    idx = tree.index(sel[0])
    keranjang = state.get("keranjang", [])
    if idx < 0 or idx >= len(keranjang):
        return "break"
    item = keranjang[idx]
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=400, height=200, relx=0.5, rely=0.5, anchor="center"
    )
    dlg.focus_force()
        
    tk.Label(dlg, text=f"SATUAN SAAT INI: {item.get('satuan', 'PC')}\nUBAH KE:",
             font=FONT_BESAR, bg=BG_PANEL, fg=FG_AKSEN).pack(pady=15)
    e = tk.Entry(dlg, font=FONT_BESAR, width=15, bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e.pack(pady=5)
    e.focus()
    e.insert(0, item.get("satuan", "PC"))
    e.selection_range(0, tk.END)
    
    def simpan(ev=None):
        item["satuan"] = e.get().strip().upper() or "PC"
        perbarui_tampilan_keranjang(root, refs, state)
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
            
    def batal(ev=None):
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        if tree:
            root.after(10, lambda: tree.focus_set())
            
    e.bind("<Return>", simpan)
    dlg.bind("<Escape>", batal)
    return "break"
