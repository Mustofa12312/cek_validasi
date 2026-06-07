"""
ui/upload_panel.py — Panel upload file Excel / CSV.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import threading


class UploadPanel(ctk.CTkFrame):
    """Panel dengan tombol upload Excel/CSV dan status file."""

    def __init__(self, master, on_file_loaded, **kwargs):
        super().__init__(master, corner_radius=10, fg_color=('#ffffff', '#1e2a45'), **kwargs)
        self._callback = on_file_loaded

        self.columnconfigure(2, weight=1)

        # Icon + judul
        icon = ctk.CTkLabel(self, text='📂', font=ctk.CTkFont(size=22))
        icon.grid(row=0, column=0, padx=(16, 6), pady=14)

        title = ctk.CTkLabel(
            self, text='Upload Data',
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=('#1e293b', '#e2e8f0')
        )
        title.grid(row=0, column=1, padx=(0, 16), pady=14, sticky='w')

        # Status file
        self.file_label = ctk.CTkLabel(
            self, text='Belum ada file dipilih.',
            font=ctk.CTkFont(size=12),
            text_color=('#64748b', '#94a3b8')
        )
        self.file_label.grid(row=0, column=2, padx=8, pady=14, sticky='w')

        # Progress bar (hidden by default)
        self.progress = ctk.CTkProgressBar(self, width=180, height=8, mode='indeterminate')

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.grid(row=0, column=3, padx=16, pady=10, sticky='e')

        self.btn_excel = ctk.CTkButton(
            btn_frame,
            text='📊  Upload Excel',
            width=145,
            height=36,
            corner_radius=8,
            fg_color='#2563eb',
            hover_color='#1d4ed8',
            font=ctk.CTkFont(size=13, weight='bold'),
            command=self._upload_excel
        )
        self.btn_excel.pack(side='left', padx=(0, 8))

        self.btn_csv = ctk.CTkButton(
            btn_frame,
            text='📄  Upload CSV',
            width=135,
            height=36,
            corner_radius=8,
            fg_color='#0891b2',
            hover_color='#0e7490',
            font=ctk.CTkFont(size=13, weight='bold'),
            command=self._upload_csv
        )
        self.btn_csv.pack(side='left')

    # ─── Internal ────────────────────────────────────────────────────────────

    def _set_loading(self, loading: bool, filename: str = ''):
        if loading:
            self.btn_excel.configure(state='disabled')
            self.btn_csv.configure(state='disabled')
            self.file_label.configure(text=f'Memuat: {filename}…', text_color='#60a5fa')
            self.progress.grid(row=0, column=2, padx=8, pady=14, sticky='w')
            self.progress.start()
        else:
            self.btn_excel.configure(state='normal')
            self.btn_csv.configure(state='normal')
            self.progress.stop()
            self.progress.grid_forget()

    def _load_file(self, path: str, kind: str) -> None:
        filename = path.split('/')[-1]
        self._set_loading(True, filename)

        def worker():
            try:
                if kind == 'excel':
                    df = pd.read_excel(path, dtype=str)
                else:
                    # Coba beberapa separator
                    for sep in [',', ';', '\t']:
                        try:
                            df = pd.read_csv(path, dtype=str, sep=sep, encoding='utf-8-sig')
                            if df.shape[1] > 1:
                                break
                        except Exception:
                            continue

                self.after(0, lambda: self._set_loading(False))
                self.after(0, lambda: self.file_label.configure(
                    text=f'✅  {filename}  ({len(df):,} baris)',
                    text_color='#22c55e'
                ))
                self.after(0, lambda: self._callback(df, filename))

            except Exception as exc:
                self.after(0, lambda: self._set_loading(False))
                self.after(0, lambda: self.file_label.configure(
                    text=f'❌  Gagal membaca file.', text_color='#ef4444'
                ))
                self.after(0, lambda: messagebox.showerror(
                    'Gagal Membaca File', str(exc)
                ))

        threading.Thread(target=worker, daemon=True).start()

    def _upload_excel(self):
        path = filedialog.askopenfilename(
            title='Pilih File Excel',
            filetypes=[('Excel Files', '*.xlsx *.xls'), ('All Files', '*.*')]
        )
        if path:
            self._load_file(path, 'excel')

    def _upload_csv(self):
        path = filedialog.askopenfilename(
            title='Pilih File CSV',
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        if path:
            self._load_file(path, 'csv')
