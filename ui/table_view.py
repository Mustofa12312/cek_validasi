"""
ui/table_view.py — Tabel hasil validasi dengan warna baris (hijau/kuning/merah).
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import Optional

DISPLAY_COLUMNS = [
    'FIRST_NAME', 'LAST_NAME', 'PARENT_ID', 'NIK', 'KK', 'ADDRESS', 'BORN_IN',
    'BORN_AT', 'STATUS', 'SKOR', 'TINGKAT_KESESUAIAN', 'SARAN_PERBAIKAN'
]

COL_WIDTHS = {
    'FIRST_NAME': 130, 'LAST_NAME': 130,
    'PARENT_ID': 130, 'NIK': 130, 'KK': 130,
    'ADDRESS': 200, 'BORN_IN': 110, 'BORN_AT': 110,
    'STATUS': 260, 'SKOR': 55, 'TINGKAT_KESESUAIAN': 120, 'SARAN_PERBAIKAN': 260,
}


class TableView(ctk.CTkFrame):
    """Wrapper CustomTkinter yang menampung ttk.Treeview berwarna."""

    def __init__(self, master, on_edit=None, **kwargs):
        super().__init__(master, fg_color='#0d1117', corner_radius=10, **kwargs)
        self._full_df: Optional[pd.DataFrame] = None
        self._on_edit = on_edit
        self._build()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Treeview',
            background='#161b22',
            foreground='#e6edf3',
            rowheight=28,
            fieldbackground='#161b22',
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure('Treeview.Heading',
            background='#1e2a45',
            foreground='#93c5fd',
            relief='flat',
            font=('Segoe UI', 10, 'bold')
        )
        style.map('Treeview',
            background=[('selected', '#2563eb')],
            foreground=[('selected', '#ffffff')]
        )
        style.map('Treeview.Heading',
            background=[('active', '#253b5e')]
        )

        # Treeview
        self.tree = ttk.Treeview(
            self,
            columns=DISPLAY_COLUMNS,
            show='headings',
            selectmode='browse',
            style='Treeview'
        )

        for col in DISPLAY_COLUMNS:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=COL_WIDTHS.get(col, 100), minwidth=60, anchor='w')

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Row color tags
        self.tree.tag_configure('valid',   background='#0f2d1a', foreground='#86efac')
        self.tree.tag_configure('warn',    background='#2d2200', foreground='#fde68a')
        self.tree.tag_configure('bad',     background='#2d0d0d', foreground='#fca5a5')

        # Double click to edit
        self.tree.bind('<Double-1>', self._on_double_click)

        self._sort_col = None
        self._sort_rev = False

    # ─── Public API ───────────────────────────────────────────────────────────

    def load_data(self, df: pd.DataFrame) -> None:
        self._full_df = df
        self._render(df)

    def filter_data(self, df: pd.DataFrame) -> None:
        self._render(df)

    def clear(self) -> None:
        self.tree.delete(*self.tree.get_children())

    # ─── Internal ────────────────────────────────────────────────────────────

    def _render(self, df: pd.DataFrame) -> None:
        self.clear()
        for _, row in df.iterrows():
            tier = row.get('TINGKAT_KESESUAIAN', '')
            tag = 'valid' if tier == 'Valid' else ('warn' if tier == 'Perlu Verifikasi' else 'bad')
            values = [str(row.get(c, '')) for c in DISPLAY_COLUMNS]
            self.tree.insert('', 'end', values=values, tags=(tag,))

    def _sort(self, col: str) -> None:
        if self._full_df is None:
            return
        self._sort_rev = not self._sort_rev if self._sort_col == col else False
        self._sort_col = col
        df_sorted = self._full_df.copy()
        try:
            df_sorted[col] = pd.to_numeric(df_sorted[col], errors='ignore')
        except Exception:
            pass
        df_sorted = df_sorted.sort_values(col, ascending=not self._sort_rev)
        self._render(df_sorted)

    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id or self._full_df is None:
            return

        values = self.tree.item(item_id, 'values')
        if not values:
            return
            
        # Get actual original index (using NIK and Name as composite key or just index from _full_df if possible)
        # Since we just rendered, it's better to find the row from the selected values.
        # Let's match by NIK, KK, and Name
        nik_val = values[DISPLAY_COLUMNS.index('NIK')]
        mask = (self._full_df['NIK'].astype(str) == str(nik_val))
        if mask.sum() == 0:
            return
        
        idx = self._full_df[mask].index[0]
        row_data = self._full_df.loc[idx]

        self._open_edit_dialog(idx, row_data)

    def _open_edit_dialog(self, df_idx: int, row_data: pd.Series):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Data Santri")
        dialog.geometry("400x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Edit Data (Perbaikan)", font=("Arial", 14, "bold")).pack(pady=10)

        entries = {}
        frame = ctk.CTkScrollableFrame(dialog)
        frame.pack(fill='both', expand=True, padx=10, pady=5)

        editable_cols = ['FIRST_NAME', 'LAST_NAME', 'PARENT_ID', 'NIK', 'KK', 'ADDRESS', 'BORN_IN', 'BORN_AT']
        
        for col in editable_cols:
            lbl = ctk.CTkLabel(frame, text=col)
            lbl.pack(anchor='w', pady=(5, 0))
            ent = ctk.CTkEntry(frame, width=300)
            ent.insert(0, str(row_data.get(col, '')))
            ent.pack(pady=(0, 5))
            entries[col] = ent

        def save_changes():
            for col, ent in entries.items():
                self._full_df.at[df_idx, col] = ent.get()
            dialog.destroy()
            if self._on_edit:
                self._on_edit(self._full_df)

        btn = ctk.CTkButton(dialog, text="Simpan & Validasi Ulang", command=save_changes)
        btn.pack(pady=15)
