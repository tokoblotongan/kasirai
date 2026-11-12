import tkinter as tk
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
    FONT_TOTAL
)
from database.queries import (
    simpan_header_transaksi,
    simpan_detail_transaksi,
    generate_nomor_nota,
    get_max_no_urut,
    update_stok
)
from handlers.keranjang import perbarui_tampilan_keranjang

def copy_struk(event=None, root=None, refs=None, state=None):
    from handlers.print_struk import copy_struk as print_copy_struk
    return print_copy_struk(event=event, root=root, refs=refs, state=state)

def buka_laci(event=None, root=None, refs=None, state=None):
    from handlers.print_struk import buka_laci as print_buka_laci
    return print_buka_laci(event=event, root=root, refs=refs, state=state)

def proses_checkout(event, root, refs, state):
    from ui.dialogs import info_kk, tampilkan_kembalian
    from ui.components import buat_dual_shadow_panel
    from handlers.print_struk import cetak_struk, buka_laci as printer_buka_laci
    
    keranjang = state.get("keranjang", [])
    if not keranjang:
        info_kk(root, "Perhatian", "Keranjang kosong!", refs=refs)
        return "break"
        
    subtotal_keranjang = sum([
        (i["harga"] - (i["harga"] * i.get("diskon_pct", 0) / 100.0)) * i["qty"] - i.get("diskon_rp", 0)
        for i in keranjang
    ])
    
    diskon_global_rp = state.get("diskon_global_rp", 0.0)
    diskon_global_persen = state.get("diskon_global_persen", 0.0)
    biaya_tambahan = state.get("biaya_tambahan", 0.0)
    
    total_dasar = subtotal_keranjang - diskon_global_rp - (subtotal_keranjang * diskon_global_persen / 100.0) + biaya_tambahan
    
    has_minus_item = any(i.get("qty", 0) < 0 for i in keranjang)
    is_retur_transaksi = has_minus_item or (total_dasar < 0)
    state["is_retur"] = is_retur_transaksi
    
    _hotkey_list = [
        "<F1>", "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>",
        "<F8>", "<F9>", "<F10>", "<F11>", "<F12>",
        "<plus>", "<KP_Add>", "<minus>", "<KP_Subtract>", 
        "<slash>", "<KP_Divide>", "<asterisk>", "<KP_Multiply>",
        "<Shift-F11>", "<Alt-F11>", "<Control-F11>", 
        "<Alt-F12>", "<Control-F12>", "<Shift-F3>", "<Control-F4>", 
        "<Return>", "<Escape>"
    ]
    
    def _disable_global_hotkeys():
        for key in _hotkey_list:
            try:
                root.unbind(key)
            except Exception:
                pass

    def _enable_global_hotkeys():
        from handlers.pending import set_pending, call_pending, clear_pending
        from handlers.cari_barang import cari_barang_dialog
        from handlers.keranjang import (
            void_item, refund_item, retur_item, open_plu, 
            ubah_harga_transaksi, ubah_satuan, tampilkan_overlay_qty,
            fokus_ke_tree_dari_entry, pindah_ke_atas, pindah_ke_bawah,
            input_barang_barcode, update_footer_preview, batal_overlay_qty
        )
        from handlers.checkout import buka_laci, copy_struk
        from handlers.aksi_lain import (
            info_bantuan, input_nota_manual, hapus_transaksi, set_member,
            biaya_tambahan_func, diskon_global_rp_func, cash_out,
            diskon_per_item, diskon_item_persen
        )

        root.bind("<F1>", lambda e: info_bantuan(e, root, refs, state))
        root.bind("<F2>", lambda e: void_item(e, root, refs, state))
        root.bind("<F3>", lambda e: open_plu(e, root, refs, state))
        root.bind("<F4>", lambda e: ubah_harga_transaksi(e, root, refs, state))
        root.bind("<F5>", lambda e: set_pending(e, root, refs, state))
        root.bind("<F6>", lambda e: call_pending(e, root, refs, state))
        root.bind("<F7>", lambda e: clear_pending(e, root, refs, state))
        root.bind("<F8>", lambda e: diskon_item_persen(e, root, refs, state))
        root.bind("<F9>", lambda e: diskon_per_item(e, root, refs, state))
        root.bind("<F10>", lambda e: cari_barang_dialog(e, root, refs, state))
        root.bind("<F11>", lambda e: buka_laci(e, root, refs, state))
        root.bind("<F12>", lambda e: copy_struk(e, root, refs, state))
        
        def _handle_plus(event):
            if isinstance(root.focus_get(), tk.Entry): return None
            proses_checkout(event, root, refs, state)
            return "break"
        
        def _handle_minus(event):
            if isinstance(root.focus_get(), tk.Entry): return None
            refund_item(event, root, refs, state)
            return "break"
            
        def _handle_slash(event):
            if isinstance(root.focus_get(), tk.Entry): return None
            input_nota_manual(event, root, refs, state)
            return "break"
            
        root.bind("<plus>", _handle_plus)
        root.bind("<KP_Add>", _handle_plus)
        root.bind("<minus>", _handle_minus)
        root.bind("<KP_Subtract>", _handle_minus)
        root.bind("<slash>", _handle_slash)
        root.bind("<KP_Divide>", _handle_slash)
        
        root.bind("<Shift-F11>", lambda e: set_member(e, root, refs, state))
        root.bind("<Alt-F11>", lambda e: biaya_tambahan_func(e, root, refs, state))
        root.bind("<Control-F11>", lambda e: hapus_transaksi(e, root, refs, state))
        root.bind("<Alt-F12>", lambda e: cash_out(e, root, refs, state))
        root.bind("<Control-F12>", lambda e: ubah_satuan(e, root, refs, state))
        root.bind("<Shift-F3>", lambda e: retur_item(e, root, refs, state))
        root.bind("<Control-F4>", lambda e: diskon_global_rp_func(e, root, refs, state))
        
        def escape_global(event):
            if state.get("overlay_qty") and state["overlay_qty"].winfo_exists():
                batal_overlay_qty(event, root, refs, state)
                return "break"
            if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
                refs["entry_barcode"].focus_set()
            return "break"
            
        root.bind("<Escape>", escape_global)

    _disable_global_hotkeys()
    
    shadow_outer, shadow_inner, dlg = buat_dual_shadow_panel(
        root, width=650, height=420, relx=0.5, rely=0.5, anchor="center"
    )
    try:
        dlg.grab_set()
        dlg.focus_force()
    except Exception:
        pass
        
    main_frame = tk.Frame(dlg, bg=BG_PANEL)
    main_frame.pack(fill="both", expand=True, padx=30, pady=20)

    var_total = tk.StringVar(value=f"{total_dasar:,.0f}".replace(",", "."))
    var_diskon_angka = tk.StringVar(value="0")
    var_diskon_persen = tk.StringVar(value="0")
    var_pembayaran = tk.StringVar(value="")
    var_kembali = tk.StringVar(value="0")
    
    mode_diskon = {"tipe": "rp"}
    is_updating = {"status": False}

    def hitung_total_akhir():
        if is_updating["status"]:
            return
        is_updating["status"] = True
        try:
            dasar = total_dasar
            if mode_diskon["tipe"] == "pct":
                persen_str = var_diskon_persen.get().strip().replace(",", ".")
                persen = float(persen_str) if persen_str else 0.0
                nominal_diskon = dasar * (persen / 100.0)
                var_diskon_angka.set(f"{nominal_diskon:.0f}")
            else:
                nominal_str = var_diskon_angka.get().strip().replace(",", ".").replace(".", "")
                nominal_diskon = float(nominal_str) if nominal_str else 0.0
                if dasar > 0:
                    var_diskon_persen.set(f"{(nominal_diskon / dasar) * 100:.2f}".rstrip('0').rstrip('.'))
                else:
                    var_diskon_persen.set("0")
                    
            total_akhir = dasar - nominal_diskon
            var_total.set(f"{total_akhir:,.0f}".replace(",", "."))
            
            bayar_str = var_pembayaran.get().strip().replace(",", ".").replace(".", "")
            bayar = float(bayar_str) if bayar_str else 0.0
            
            if total_akhir < 0:
                bayar = -abs(bayar) if bayar != 0 else 0.0
                
            kembali = bayar - total_akhir
            var_kembali.set(f"{kembali:,.0f}".replace(",", "."))
            
            if kembali < 0:
                lbl_kembali_val.config(fg=FG_MERAH)
            else:
                lbl_kembali_val.config(fg=FG_SUKSES if total_akhir < 0 else FG_KUNING)
        except ValueError:
            pass
        finally:
            is_updating["status"] = False

    def on_edit_angka(*args):
        mode_diskon["tipe"] = "rp"
        hitung_total_akhir()
        
    def on_edit_persen(*args):
        mode_diskon["tipe"] = "pct"
        hitung_total_akhir()
        
    def on_edit_bayar(*args):
        hitung_total_akhir()

    var_diskon_angka.trace_add("write", on_edit_angka)
    var_diskon_persen.trace_add("write", on_edit_persen)
    var_pembayaran.trace_add("write", on_edit_bayar)

    LEBAR_ENTRY = 15
    LEBAR_LABEL = 14

    f1 = tk.Frame(main_frame, bg=BG_PANEL)
    f1.pack(fill="x", pady=3)
    tk.Label(f1, text="Total", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f1, text=":Rp", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    tk.Label(f1, textvariable=var_total, font=FONT_JUDUL, bg=BG_PANEL, fg=FG_KUNING, anchor="e").pack(side="left", padx=10)

    f2 = tk.Frame(main_frame, bg=BG_PANEL)
    f2.pack(fill="x", pady=3)
    
    tk.Label(f2, text="Diskon", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f2, text=":Rp", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    e_diskon_angka = tk.Entry(f2, textvariable=var_diskon_angka, font=FONT_BESAR, width=LEBAR_ENTRY, justify="right", bg=BG_INPUT, fg=FG_AKSEN, insertbackground=FG_AKSEN)
    e_diskon_angka.pack(side="left", padx=5)
    
    tk.Label(f2, text="(F4)", font=FONT_KECIL, bg=BG_PANEL, fg=FG_AKSEN).pack(side="left", padx=(5, 10))
    
    e_diskon_persen = tk.Entry(f2, textvariable=var_diskon_persen, font=FONT_BESAR, width=LEBAR_ENTRY, justify="right", bg=BG_INPUT, fg=FG_AKSEN, insertbackground=FG_AKSEN)
    e_diskon_persen.pack(side="left", padx=5)
    tk.Label(f2, text="(F5)%", font=FONT_KECIL, bg=BG_PANEL, fg=FG_AKSEN).pack(side="left")

    f3 = tk.Frame(main_frame, bg=BG_PANEL)
    f3.pack(fill="x", pady=3)
    tk.Label(f3, text="Card", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f3, text=":Rp", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    e_card = tk.Entry(f3, font=FONT_BESAR, width=LEBAR_ENTRY, justify="right", bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_card.pack(side="left", padx=5)
    
    frame_cash = tk.Frame(f3, bg=BG_PANEL)
    frame_cash.pack(side="left", padx=(25, 0))
    tk.Label(frame_cash, text="Cara Bayar", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left", padx=(0, 10))
    
    # Dropdown/Button Visual CASH dengan border Indigo
    lbl_cash = tk.Label(frame_cash, text="▼ [ CASH ]", font=FONT_BESAR, bg=BG_INPUT, fg=FG_AKSEN, width=10, pady=3, highlightbackground=FG_AKSEN, highlightthickness=2, cursor="hand2")
    lbl_cash.pack(side="left")

    tk.Frame(main_frame, bg=FG_ABU, height=1).pack(fill="x", pady=10)

    f4 = tk.Frame(main_frame, bg=BG_PANEL)
    f4.pack(fill="x", pady=3)
    tk.Label(f4, text="Pembayaran", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f4, text=":Rp", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    
    # Input Pembayaran Lebih Besar
    e_bayar = tk.Entry(f4, textvariable=var_pembayaran, font=FONT_JUDUL, width=LEBAR_ENTRY, justify="right", bg=BG_INPUT, fg=FG_SUKSES, insertbackground=FG_AKSEN, highlightbackground=FG_SUKSES, highlightthickness=1)
    e_bayar.pack(side="left", padx=5, ipady=3)

    f5 = tk.Frame(main_frame, bg=BG_PANEL)
    f5.pack(fill="x", pady=3)
    tk.Label(f5, text="Kembali", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f5, text=":Rp", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    lbl_kembali_val = tk.Label(f5, textvariable=var_kembali, font=FONT_TOTAL, bg=BG_PANEL, fg=FG_KUNING, anchor="e")
    lbl_kembali_val.pack(side="left", padx=10)

    tk.Frame(main_frame, bg=FG_ABU, height=1).pack(fill="x", pady=10)

    f6 = tk.Frame(main_frame, bg=BG_PANEL)
    f6.pack(fill="x", pady=3)
    tk.Label(f6, text="No. Member", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA, width=LEBAR_LABEL, anchor="w").pack(side="left")
    tk.Label(f6, text=":", font=FONT_BESAR, bg=BG_PANEL, fg=FG_UTAMA).pack(side="left")
    e_member = tk.Entry(f6, font=FONT_BESAR, width=LEBAR_ENTRY, bg=BG_INPUT, fg=BG_INPUT_FG, insertbackground=FG_AKSEN)
    e_member.pack(side="left", padx=5)
    if state.get("member_id"):
        e_member.insert(0, state["member_id"])

    tk.Label(main_frame, text="<F4 = Diskon Angka | F5 = Diskon Persen | ENTER = Proses | ESC = Batal>", 
             font=FONT_KECIL, bg=BG_PANEL, fg=FG_ABU).pack(pady=(15, 5))
             
    # Tombol Proses Besar
    btn_proses = tk.Label(main_frame, text="PROSES PEMBAYARAN (ENTER)", font=FONT_BESAR, bg=FG_AKSEN, fg="#FFFFFF", pady=10, cursor="hand2")
    btn_proses.pack(side="right", anchor="e", padx=10)
    
    def fokus_diskon_angka(ev=None):
        e_diskon_angka.focus()
        e_diskon_angka.selection_range(0, tk.END)
        return "break"
        
    def fokus_diskon_persen(ev=None):
        e_diskon_persen.focus()
        e_diskon_persen.selection_range(0, tk.END)
        return "break"

    def _enter_ke_pembayaran(ev=None):
        e_bayar.focus_set()
        return "break"

    def _tab_next(ev=None):
        widget_fokus = dlg.focus_get()
        if widget_fokus == e_diskon_angka: e_diskon_persen.focus_set()
        elif widget_fokus == e_diskon_persen: e_card.focus_set()
        elif widget_fokus == e_card: e_bayar.focus_set()
        elif widget_fokus == e_bayar: e_member.focus_set()
        elif widget_fokus == e_member: e_diskon_angka.focus_set()
        return "break"

    def proses_bayar(ev=None):
        try:
            hitung_total_akhir() # Pastikan sinkron
            
            total_akhir = float(var_total.get().replace(".", "").replace(",", ""))
            bayar_input = float(var_pembayaran.get().replace(".", "").replace(",", "") or 0)
            card_input = float(e_card.get().replace(".", "").replace(",", "") or 0)
            
            if total_akhir < 0:
                bayar = -abs(bayar_input) if bayar_input != 0 else 0.0
                card = -abs(card_input) if card_input != 0 else 0.0
            else:
                bayar = bayar_input
                card = card_input
                
            total_bayar = bayar + card
            kembali = total_bayar - total_akhir
            
            if total_akhir >= 0 and kembali < 0:
                info_kk(dlg, "Error", "Pembayaran kurang!", refs=refs)
                return
                
            if e_member.get().strip():
                state["member_id"] = e_member.get().strip()
                state["member"] = e_member.get().strip()
                
            nominal_diskon_str = var_diskon_angka.get().replace(".", "").replace(",", "")
            diskon_global_rp = int(round(float(nominal_diskon_str))) if nominal_diskon_str else 0
            state["diskon_global_rp"] = diskon_global_rp
            
            tgl = datetime.now().strftime("%Y-%m-%d")
            tgl_jam = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            jam = datetime.now().strftime("%H:%M:%S")
            
            nomor_nota = generate_nomor_nota(tgl)
            state["nomor_nota"] = nomor_nota
            
            shift = state.get("shift", "A")
            nomor_kassa = state.get("nomor_kassa", "001")
            user_aktif = state.get("user_id") or state.get("user_aktif", "1")
            
            header_tuple = (
                nomor_nota, tgl, jam, shift, nomor_kassa, user_aktif,
                total_akhir, total_bayar, kembali, "CASH", state.get("member_id", ""), 0.0, 0.0
            )
            
            try:
                simpan_header_transaksi(header_tuple)
            except Exception as e_db:
                info_kk(dlg, "Error Database", f"Gagal simpan: {e_db}", refs=refs)
                return
                
            no_urut = get_max_no_urut(nomor_nota) + 1
            detail_rows = []
            for idx, itm in enumerate(keranjang):
                hrg = itm["harga"]
                qty_val = itm["qty"]
                dsk_pct = itm.get("diskon_pct", 0.0)
                dsk_rp = itm.get("diskon_rp", 0.0)
                detail_rows.append((
                    shift, nomor_kassa, nomor_nota, no_urut + idx, itm["kode"], itm["nama"],
                    hrg, dsk_pct, dsk_rp, 0.0, diskon_global_rp, 0.0, qty_val,
                    itm.get("satuan", "PC"), hrg, itm["nama"], nomor_nota, tgl, tgl_jam, jam
                ))
                if not itm.get("is_manual", False):
                    update_stok(itm["kode"], qty_val)
                    
            simpan_detail_transaksi(detail_rows)
            
            state["total"] = total_akhir
            state["bayar"] = total_bayar
            state["kembali"] = kembali
            state["nomor_nota"] = generate_nomor_nota()
            
            try:
                cetak_struk(
                    nomor_nota = nomor_nota,
                    keranjang_items = keranjang,
                    total = total_akhir,
                    bayar = total_bayar,
                    kembali = kembali,
                    is_retur = state.get("is_retur", False),
                    user_id = user_aktif,
                    root = root,
                    diskon_global_rp = diskon_global_rp,
                    diskon_global_persen = diskon_global_persen
                )
            except Exception as e_print:
                print(f"[WARN] Print error: {e_print}")
                
            try:
                printer_buka_laci(event=None, root=root, refs=refs, state=state)
            except Exception:
                pass
                
            state["transaksi_terakhir"] = {
                "nomor_nota": nomor_nota,
                "keranjang": list(keranjang),
                "total": total_akhir,
                "bayar": total_bayar,
                "kembali": kembali,
                "is_retur": state.get("is_retur", False),
                "user_id": user_aktif,
                "diskon_global_rp": diskon_global_rp,
                "diskon_global_persen": diskon_global_persen
            }
                
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()
            shadow_outer.destroy()
            shadow_inner.destroy()
            
            _enable_global_hotkeys()
            
            tampilkan_kembalian(root, total_bayar, kembali, total_akhir, refs=refs)
            
            state["keranjang"] = []
            state["diskon_global_rp"] = 0.0
            state["diskon_global_persen"] = 0.0
            state["biaya_tambahan"] = 0.0
            state["member_id"] = ""
            state["member"] = None
            state["is_retur"] = False
            
            tgl_hari_ini = datetime.now().strftime("%d-%m-%Y")
            user_lbl = state.get("user_aktif") or "UMUM"
            shift_lbl = state.get("shift", "A")
            nota_lbl = state.get("nomor_nota", "000001")
            if "lbl_nomor_nota" in refs and refs["lbl_nomor_nota"].winfo_exists():
                refs["lbl_nomor_nota"].config(
                    text=f"📅  {tgl_hari_ini}   ·   Shift {shift_lbl}   ·   {user_lbl.upper()}   ·   NOTA: {nota_lbl}"
                )
                
            perbarui_tampilan_keranjang(root, refs, state)
            
            if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
                root.after(10, lambda: refs["entry_barcode"].focus())
                
        except ValueError:
            info_kk(dlg, "Error", "Masukkan nominal yang valid!", refs=refs)
            
    def batal(ev=None):
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        shadow_outer.destroy()
        shadow_inner.destroy()
        
        _enable_global_hotkeys()
        
        if "entry_barcode" in refs and refs["entry_barcode"].winfo_exists():
            root.after(10, lambda: refs["entry_barcode"].focus())
            
    dlg.bind("<F4>", fokus_diskon_angka)
    e_diskon_angka.bind("<F4>", fokus_diskon_angka)
    e_diskon_persen.bind("<F4>", fokus_diskon_angka)
    e_bayar.bind("<F4>", fokus_diskon_angka)
    
    dlg.bind("<F5>", fokus_diskon_persen)
    e_diskon_angka.bind("<F5>", fokus_diskon_persen)
    e_diskon_persen.bind("<F5>", fokus_diskon_persen)
    e_bayar.bind("<F5>", fokus_diskon_persen)
    
    def _on_esc_checkout(event=None):
        batal()
        return "break"

    def _on_enter_checkout(event=None):
        proses_bayar()
        return "break"

    for w in (e_diskon_angka, e_diskon_persen, e_card, e_bayar, e_member):
        w.bind("<Tab>", _tab_next)
        w.bind("<Escape>", _on_esc_checkout)
        
    e_diskon_angka.bind("<Return>", _enter_ke_pembayaran)
    e_diskon_persen.bind("<Return>", _enter_ke_pembayaran)
    e_card.bind("<Return>", _on_enter_checkout)
    e_member.bind("<Return>", _on_enter_checkout)
    e_bayar.bind("<Return>", _on_enter_checkout)
    
    dlg.bind("<Escape>", _on_esc_checkout)
    dlg.bind("<Return>", _on_enter_checkout)
    
    e_bayar.focus_set()
    return "break"

checkout_dialog = proses_checkout