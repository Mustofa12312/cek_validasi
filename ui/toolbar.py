"""
ui/toolbar.py — Search real-time + filter dropdown + tombol export.
"""

import customtkinter as ctk
import pandas as pd


FILTER_OPTIONS = [
    'Semua Data',
    'Valid',
    'Tidak Valid',
    'NIK Duplikat',
    'KK Duplikat',
    'Tempat Tidak Sesuai',
    'Tanggal Tidak Sesuai',
]


class Toolbar(ctk.CTkFrame):
    """Baris toolbar: search + filter + export."""

    def __init__(self, master, on_search, on_filter, on_export_excel, on_export_csv, **kwargs):
        super().__init__(master, fg_color='#1e2a45', corner_radius=10, **kwargs)
        self._on_search = on_search
        self._on_filter = on_filter
        self._on_export_excel = on_export_excel
        self._on_export_csv = on_export_csv

        self.columnconfigure(1, weight=1)
        self._build()

    def _build(self):
        # 🔍 Search
        search_icon = ctk.CTkLabel(self, text='🔍', font=ctk.CTkFont(size=16))
        search_icon.grid(row=0, column=0, padx=(14, 4), pady=12)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add('write', self._trigger_search)

        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text='Cari Nama, NIK, KK, atau Alamat…',
            height=36,
            corner_radius=8,
            border_color='#334155',
            fg_color='#0d1117',
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 12), pady=12, sticky='ew')

        # Filter dropdown
        filter_label = ctk.CTkLabel(
            self, text='Filter:',
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color='#94a3b8'
        )
        filter_label.grid(row=0, column=2, padx=(0, 6), pady=12)

        self.filter_var = ctk.StringVar(value='Semua Data')
        self.filter_menu = ctk.CTkOptionMenu(
            self,
            variable=self.filter_var,
            values=FILTER_OPTIONS,
            width=150,
            height=36,
            corner_radius=8,
            fg_color='#0d1117',
            button_color='#2563eb',
            button_hover_color='#1d4ed8',
            font=ctk.CTkFont(size=13),
            command=self._trigger_filter
        )
        self.filter_menu.grid(row=0, column=3, padx=(0, 16), pady=12)

        # Export buttons
        self.btn_export_excel = ctk.CTkButton(
            self,
            text='⬇ Excel',
            width=110,
            height=36,
            corner_radius=8,
            fg_color='#15803d',
            hover_color='#166534',
            font=ctk.CTkFont(size=13, weight='bold'),
            state='disabled',
            command=self._on_export_excel
        )
        self.btn_export_excel.grid(row=0, column=4, padx=(0, 8), pady=12)

        self.btn_export_csv = ctk.CTkButton(
            self,
            text='⬇ CSV',
            width=100,
            height=36,
            corner_radius=8,
            fg_color='#0891b2',
            hover_color='#0e7490',
            font=ctk.CTkFont(size=13, weight='bold'),
            state='disabled',
            command=self._on_export_csv
        )
        self.btn_export_csv.grid(row=0, column=5, padx=(0, 14), pady=12)

    # ─── API ─────────────────────────────────────────────────────────────────

    def set_export_enabled(self, enabled: bool) -> None:
        state = 'normal' if enabled else 'disabled'
        self.btn_export_excel.configure(state=state)
        self.btn_export_csv.configure(state=state)

    def get_search_text(self) -> str:
        return self.search_var.get().strip().lower()

    def get_filter(self) -> str:
        return self.filter_var.get()

    # ─── Triggers ─────────────────────────────────────────────────────────────

    def _trigger_search(self, *_):
        self._on_search()

    def _trigger_filter(self, *_):
        self._on_filter()
