import tkinter as tk
from config.theme import (
    BG_PANEL,
    BG_PANEL_SOFT,
    BG_SHADOW,
    BG_INPUT,
    FG_AKSEN,
    FG_UTAMA,
    FONT_BESAR
)

def buat_glass_panel(parent, bg=BG_PANEL, highlightthickness=0, **kwargs):
    """
    Membuat frame panel dengan style glass/flat tanpa border kasar.
    """
    return tk.Frame(parent, bg=bg, highlightthickness=highlightthickness, **kwargs)

def taruh_glass_panel(panel, relx=0.5, rely=0.5, anchor="center", width=None, height=None, **kwargs):
    """
    Menempatkan panel di tengah atau koordinat relatif dengan opsi ukuran eksplisit.
    """
    place_kwargs = {"relx": relx, "rely": rely, "anchor": anchor, **kwargs}
    if width is not None:
        place_kwargs["width"] = width
    if height is not None:
        place_kwargs["height"] = height
    panel.place(**place_kwargs)
    return panel

def buat_dual_shadow_panel(parent, width, height, relx=0.5, rely=0.5, anchor="center",
                           panel_bg=BG_PANEL, shadow_outer_bg="#050710", shadow_inner_bg=BG_SHADOW):
    """
    Membuat panel mengambang dengan efek bayangan ganda (dual soft shadow) di tengah parent.
    Return: (shadow_outer, shadow_inner, container)
    """
    shadow_outer = tk.Frame(parent, bg=shadow_outer_bg)
    shadow_outer.place(relx=relx, rely=rely, anchor=anchor, width=width + 6, height=height + 6)
    
    shadow_inner = tk.Frame(parent, bg=shadow_inner_bg)
    shadow_inner.place(relx=relx, rely=rely, anchor=anchor, width=width + 3, height=height + 3)
    
    container = tk.Frame(parent, bg=panel_bg, highlightthickness=0)
    container.place(relx=relx, rely=rely, anchor=anchor, width=width, height=height)
    container.lift()
    return shadow_outer, shadow_inner, container

def buat_tombol_soft(parent, text, command=None, bg=BG_PANEL_SOFT, fg=FG_AKSEN,
                     font=FONT_BESAR, padx=20, pady=8, highlightthickness=1,
                     highlightbackground=FG_AKSEN, width=None):
    """
    Membuat tombol bergaya soft (Label Tkinter interaktif dengan border aksen tipis).
    """
    lbl_kwargs = {
        "text": text,
        "font": font,
        "bg": bg,
        "fg": fg,
        "padx": padx,
        "pady": pady,
        "highlightthickness": highlightthickness,
        "highlightbackground": highlightbackground,
        "cursor": "hand2"
    }
    if width is not None:
        lbl_kwargs["width"] = width
    btn = tk.Label(parent, **lbl_kwargs)
    if command:
        btn.bind("<Button-1>", lambda e: command())
    return btn
