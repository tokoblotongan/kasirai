import tkinter as tk
from config.settings import NAMA_TOKO
from config.theme import (
    BG_UTAMA,
    BG_PANEL,
    BG_PANEL_SOFT,
    BG_SHADOW,
    BG_INPUT,
    BG_INPUT_FG,
    BORDER_GLASS,
    FG_AKSEN,
    FG_AKSEN_HOVER,
    FG_UTAMA,
    FONT_HEADER,
    FONT_BESAR
)
from database.queries import cek_login


def tampilkan_login(root, state=None, refs=None, on_login_sukses=None, on_success=None):
    """
    Menampilkan window login sebagai Tk() TERPISAH (bukan Toplevel).
    Kompatibel Windows 7.
    BLOCKING: fungsi ini return hanya setelah login sukses atau ESC.
    """
    print("[DEBUG-1] tampilkan_login() DIPANGGIL", flush=True)
    
    callback_sukses = on_success or on_login_sukses
    print(f"[DEBUG-2] callback_sukses = {callback_sukses}", flush=True)
    
    hasil_login = {"user_id": None, "nama_user": None, "sukses": False}
    status = {"sedang_proses": False}
    
    # ═══ BUAT WINDOW LOGIN SEBAGAI Tk() BARU ═══
    print("[DEBUG-3] Akan buat Tk() baru untuk login...", flush=True)
    login_win = tk.Tk()
    login_win.title(f"Login - {NAMA_TOKO}")
    login_win.geometry("500x420") # [FIX] Tinggikan window
    login_win.configure(bg=BG_UTAMA)
    print("[DEBUG-4] Tk() login BERHASIL dibuat", flush=True)
    
    # Center window
    login_win.update_idletasks()
    lebar_layar = login_win.winfo_screenwidth()
    tinggi_layar = login_win.winfo_screenheight()
    x = (lebar_layar // 2) - (500 // 2)
    y = (tinggi_layar // 2) - (420 // 2)
    login_win.geometry(f"500x420+{x}+{y}")
    
    # Dual shadow
    shadow_outer = tk.Frame(login_win, bg=BG_SHADOW)
    shadow_outer.place(relx=0.5, rely=0.5, anchor="center", width=436, height=356)
    shadow_inner = tk.Frame(login_win, bg="#151620")
    shadow_inner.place(relx=0.5, rely=0.5, anchor="center", width=433, height=353)
    
    card = tk.Frame(login_win, bg=BG_PANEL, highlightthickness=0)
    card.place(relx=0.5, rely=0.5, anchor="center", width=430, height=350) # [FIX] Perbesar card
    
    tk.Label(card, text="◉  LOGIN KASIR", font=FONT_HEADER,
             bg=BG_PANEL, fg=FG_AKSEN).pack(pady=(30, 25))
    
    frame = tk.Frame(card, bg=BG_PANEL)
    frame.pack(pady=5)
    
    # Font label dan entry diperbesar untuk visual modern
    tk.Label(frame, text="USER ID", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA).grid(row=0, column=0, sticky="w", pady=12)
    entry_userid = tk.Entry(frame, font=FONT_BESAR, width=22,
                            bg=BG_INPUT, fg=BG_INPUT_FG,
                            insertbackground=FG_AKSEN,
                            relief="flat", bd=8,
                            highlightbackground=BORDER_GLASS,
                            highlightthickness=2)
    entry_userid.grid(row=0, column=1, pady=12, padx=(15, 0), ipady=4)
    
    tk.Label(frame, text="PASSWORD", font=FONT_BESAR,
             bg=BG_PANEL, fg=FG_UTAMA).grid(row=1, column=0, sticky="w", pady=12)
    entry_pass = tk.Entry(frame, font=FONT_BESAR, width=22, show="*",
                          bg=BG_INPUT, fg=BG_INPUT_FG,
                          insertbackground=FG_AKSEN,
                          relief="flat", bd=8,
                          highlightbackground=BORDER_GLASS,
                          highlightthickness=2)
    entry_pass.grid(row=1, column=1, pady=12, padx=(15, 0), ipady=4)
    
    # [FIX] Kembali ke tk.Button murni karena ruang sudah cukup
    btn_login = tk.Button(card, text="LOGIN", font=FONT_BESAR,
                          bg=FG_AKSEN, fg="#FFFFFF",
                          activebackground=FG_AKSEN_HOVER, activeforeground="#FFFFFF",
                          relief="flat", bd=0, cursor="hand2", padx=50, pady=10)
    btn_login.pack(pady=(20, 10))
    print("[DEBUG-6] Widget login selesai dibuat", flush=True)
    
    # ═══ FUNGSI UNTUK MENUTUP WINDOW DENGAN BERSIH ═══
    def tutup_login_win():
        """Quit mainloop dulu, baru destroy. Aman untuk Windows 7."""
        try:
            login_win.quit()
        except Exception as e:
            print(f"[DEBUG] quit error: {e}", flush=True)
        try:
            login_win.destroy()
        except Exception as e:
            print(f"[DEBUG] destroy error: {e}", flush=True)
    
    # ═══ FUNGSI PROSES LOGIN (dengan GUARD) ═══
    def proses_login_internal(event=None):
        if status["sedang_proses"]:
            print("[DEBUG-PL-GUARD] Sudah sedang proses, abaikan", flush=True)
            return
        status["sedang_proses"] = True
        
        print("[DEBUG-PL-1] proses_login() DIPANGGIL", flush=True)
        uid = entry_userid.get().strip()
        pwd = entry_pass.get().strip()
        print(f"[DEBUG-PL-2] uid='{uid}'", flush=True)
        
        if not uid or not pwd:
            from ui.dialogs import info_kk
            info_kk(login_win, "Error", "User ID dan Password harus diisi!", refs=refs)
            status["sedang_proses"] = False
            return
        
        try:
            print("[DEBUG-PL-4] Akan cek_login ke DB...", flush=True)
            row = cek_login(uid, pwd)
            print(f"[DEBUG-PL-5] Hasil cek_login: {row}", flush=True)
            
            if row:
                hasil_login["user_id"] = row[0]
                hasil_login["nama_user"] = row[1]
                hasil_login["sukses"] = True
                print("[DEBUG-PL-6] Login SUKSES, jadwalkan tutup 100ms", flush=True)
                login_win.after(100, tutup_login_win)
            else:
                from ui.dialogs import info_kk
                print("[DEBUG-PL-9] Login GAGAL — password salah", flush=True)
                info_kk(login_win, "Error", "User ID atau Password salah!", refs=refs)
                entry_userid.delete(0, tk.END)
                entry_pass.delete(0, tk.END)
                entry_userid.focus_set()
                status["sedang_proses"] = False
        except Exception as e:
            print(f"[DEBUG-PL-ERR] EXCEPTION: {e}", flush=True)
            import traceback
            traceback.print_exc()
            from ui.dialogs import info_kk
            info_kk(login_win, "Error", f"Gagal login: {e}", refs=refs)
            status["sedang_proses"] = False
    
    # ═══ BINDING ═══
    btn_login.bind("<Button-1>", proses_login_internal)
    entry_userid.bind("<Return>", lambda e: entry_pass.focus())
    entry_pass.bind("<Return>", proses_login_internal)
    
    def on_escape(event=None):
        print("[DEBUG] ESC ditekan — keluar aplikasi", flush=True)
        hasil_login["sukses"] = False
        login_win.after(100, tutup_login_win)
    login_win.bind("<Escape>", on_escape)
    
    entry_userid.focus_set()
    print("[DEBUG-8] Window login siap ditampilkan", flush=True)
    
    # ═══ MAINLOOP ═══
    print("[DEBUG-9] AKAN mainloop — tunggu login...", flush=True)
    login_win.mainloop()
    print("[DEBUG-10] mainloop SELESAI — window login ditutup", flush=True)
    
    if hasil_login["sukses"] and callback_sukses:
        print(f"[DEBUG-11] Memanggil callback: user={hasil_login['user_id']}", flush=True)
        try:
            callback_sukses(hasil_login["user_id"], hasil_login["nama_user"])
            print("[DEBUG-12] Callback BERHASIL dijalankan", flush=True)
        except Exception as e:
            print(f"[DEBUG-ERR] Callback error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    elif not hasil_login["sukses"]:
        print("[DEBUG-13] Login tidak sukses / ESC — keluar program", flush=True)
        try:
            root.destroy()
        except Exception:
            pass
    
    return login_win