"""
ui/app.py — Root window utama aplikasi Validasi Data Kependudukan.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
import threading
from typing import Optional

from core.validator import validate_dataframe, check_required_columns
from core.exporter import export_excel, export_csv
from ui.dashboard import DashboardPanel
from ui.upload_panel import UploadPanel
from ui.table_view import TableView
from ui.toolbar import Toolbar


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('light')
        ctk.set_default_color_theme('blue')

        self.title('Validasi Data Kependudukan — v1.0')
        self.geometry('1350x820')
        self.minsize(1100, 680)

        # State
        self._validated_df: Optional[pd.DataFrame] = None
        self._filtered_df: Optional[pd.DataFrame] = None
        self._nik_dup: set = set()
        self._kk_dup: set = set()

        self.configure(fg_color=('#f1f5f9', '#0d1117'))
        self._build_ui()

    # ─── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # table row expands

        # ── Header
        self._build_header()

        # ── Upload panel
        self.upload_panel = UploadPanel(self, on_file_loaded=self._on_file_loaded)
        self.upload_panel.grid(row=1, column=0, sticky='ew', padx=14, pady=(0, 8))

        # ── Dashboard
        self.dashboard = DashboardPanel(self)
        self.dashboard.grid(row=2, column=0, sticky='ew', padx=14, pady=(0, 8))

        # ── Toolbar
        self.toolbar = Toolbar(
            self,
            on_search=self._apply_search_filter,
            on_filter=self._apply_search_filter,
            on_export_excel=self._do_export_excel,
            on_export_csv=self._do_export_csv,
        )
        self.toolbar.grid(row=3, column=0, sticky='ew', padx=14, pady=(0, 8))

        # ── Table
        self.table = TableView(self, on_edit=self._on_row_edited)
        self.table.grid(row=4, column=0, sticky='nsew', padx=14, pady=(0, 8))
        self.grid_rowconfigure(4, weight=1)

        # ── Status bar
        self._build_statusbar()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, height=58, corner_radius=0, fg_color=('#ffffff', '#111827'))
        hdr.grid(row=0, column=0, sticky='ew')
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(
            hdr,
            text='🔍  Validasi Data Kependudukan',
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=('#1d4ed8', '#60a5fa')
        ).grid(row=0, column=0, padx=20, pady=0, sticky='w')

        ctk.CTkLabel(
            hdr,
            text='NIK Santri & Wali • KK • Alamat • Tempat & Tanggal Lahir',
            font=ctk.CTkFont(size=11),
            text_color=('#475569', '#94a3b8')
        ).grid(row=0, column=1, padx=10, pady=0, sticky='w')

        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            hdr, text='☀️', width=30, height=30, fg_color='transparent', hover_color=('#e2e8f0', '#1e293b'),
            text_color=('#1e293b', '#f8fafc'), command=self._toggle_theme
        )
        self.theme_btn.grid(row=0, column=2, padx=(0, 10), pady=0, sticky='e')

        ctk.CTkLabel(
            hdr, text='v1.0',
            font=ctk.CTkFont(size=11),
            text_color=('#94a3b8', '#334155')
        ).grid(row=0, column=3, padx=20, pady=0, sticky='e')

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=('#ffffff', '#111827'))
        bar.grid(row=5, column=0, sticky='ew')
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(1, weight=0)
        bar.grid_columnconfigure(2, weight=0)
        bar.grid_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            bar,
            text='Siap. Upload file Excel atau CSV untuk memulai validasi.',
            font=ctk.CTkFont(size=11),
            text_color=('#64748b', '#94a3b8'),
            anchor='w'
        )
        self._status_lbl.grid(row=0, column=0, padx=14, pady=0, sticky='w')

        self.progress_var = ctk.DoubleVar(value=0)
        self.progressbar = ctk.CTkProgressBar(bar, variable=self.progress_var, width=150, height=8)
        self.progressbar.grid(row=0, column=1, padx=14, pady=0, sticky='e')
        self.progressbar.set(0)

        self._rows_lbl = ctk.CTkLabel(
            bar, text='',
            font=ctk.CTkFont(size=11),
            text_color=('#64748b', '#94a3b8'),
            anchor='e'
        )
        self._rows_lbl.grid(row=0, column=2, padx=14, pady=0, sticky='e')

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _set_status(self, text: str, color: str = None):
        if color is None:
            color = ('#64748b', '#94a3b8')
        self._status_lbl.configure(text=text, text_color=color)

    def _set_row_count(self, shown: int, total: int):
        self._rows_lbl.configure(text=f'Menampilkan {shown:,} / {total:,} baris')
        
    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text='☀️')
            self.table.update_theme("light")
            self.dashboard.update_theme("light")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text='🌙')
            self.table.update_theme("dark")
            self.dashboard.update_theme("dark")

    # ─── Callbacks ───────────────────────────────────────────────────────────

    def _on_file_loaded(self, df: pd.DataFrame, filename: str):
        self._set_status(f'Memvalidasi {filename}…', '#60a5fa')
        self.update()

        def worker():
            try:
                # Check required columns
                df_check = df.copy()
                df_check.columns = [str(c).upper().strip() for c in df_check.columns]
                missing = check_required_columns(df_check)
                if missing:
                    self.after(0, lambda: messagebox.showerror(
                        'Kolom Tidak Lengkap',
                        f'Kolom berikut tidak ditemukan:\n  {", ".join(missing)}\n\n'
                        f'Kolom wajib: PARENT_ID, NIK, KK, ADDRESS, BORN_IN, BORN_AT'
                    ))
                    self.after(0, lambda: self._set_status('Gagal: kolom tidak lengkap.', '#ef4444'))
                    return

                def progress_cb(current, total):
                    if total > 0:
                        self.after(0, self.progress_var.set, current / total)

                validated, nik_dup, kk_dup = validate_dataframe(df, progress_callback=progress_cb)
                self.after(0, lambda: self._on_validation_done(validated, nik_dup, kk_dup, filename))

            except Exception as exc:
                self.after(0, lambda: messagebox.showerror('Error Validasi', str(exc)))
                self.after(0, lambda: self._set_status(f'Error: {exc}', '#ef4444'))

        threading.Thread(target=worker, daemon=True).start()

    def _on_validation_done(self, df, nik_dup, kk_dup, filename):
        self._validated_df = df
        self._filtered_df = df
        self._nik_dup = nik_dup
        self._kk_dup = kk_dup

        self.dashboard.update_stats(df, nik_dup, kk_dup)
        self.table.load_data(df)
        self.toolbar.set_export_enabled(True)

        total  = len(df)
        valid  = int((df['TINGKAT_KESESUAIAN'] == 'Valid').sum())
        persen = round(valid / total * 100, 1) if total else 0
        self._set_status(f'✅  Selesai: {filename} — {total:,} baris, {persen}% valid', '#22c55e')
        self._set_row_count(total, total)
        self.progressbar.set(1)

    def _on_row_edited(self, edited_df: pd.DataFrame):
        self._set_status('Memvalidasi ulang data…', '#60a5fa')
        self.progressbar.set(0)
        self.update()
        
        def worker():
            try:
                def progress_cb(current, total):
                    if total > 0:
                        self.after(0, self.progress_var.set, current / total)
                        
                validated, nik_dup, kk_dup = validate_dataframe(edited_df, progress_callback=progress_cb)
                self.after(0, lambda: self._on_validation_done(validated, nik_dup, kk_dup, "Data Edit"))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror('Error Validasi', str(exc)))
                self.after(0, lambda: self._set_status(f'Error: {exc}', '#ef4444'))
                
        threading.Thread(target=worker, daemon=True).start()

    def _apply_search_filter(self):
        if self._validated_df is None:
            return

        query  = self.toolbar.get_search_text()
        filt   = self.toolbar.get_filter()
        df     = self._validated_df.copy()

        # Filter kategori
        if filt == 'Valid':
            df = df[df['TINGKAT_KESESUAIAN'] == 'Valid']
        elif filt == 'Tidak Valid':
            df = df[df['TINGKAT_KESESUAIAN'] != 'Valid']
        elif filt == 'NIK Duplikat':
            df = df[df['STATUS'].str.contains('NIK Duplikat', na=False)]
        elif filt == 'KK Duplikat':
            df = df[df['STATUS'].str.contains('KK Duplikat', na=False)]
        elif filt == 'Tempat Tidak Sesuai':
            df = df[df['STATUS'].str.contains('Tempat Lahir Tidak Sesuai', na=False)]
        elif filt == 'Tanggal Tidak Sesuai':
            df = df[df['STATUS'].str.contains('Tanggal Lahir Tidak Sesuai', na=False)]

        # Search
        if query:
            mask = (
                df.get('FIRST_NAME', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False) |
                df.get('LAST_NAME', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False) |
                df.get('PARENT_ID', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False) |
                df.get('NIK', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False) |
                df.get('KK', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False) |
                df.get('ADDRESS', pd.Series(dtype=str)).astype(str).str.lower().str.contains(query, na=False)
            )
            df = df[mask]

        self._filtered_df = df
        self.table.filter_data(df)
        self._set_row_count(len(df), len(self._validated_df))

    # ─── Export ───────────────────────────────────────────────────────────────

    def _do_export_excel(self):
        if self._validated_df is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel Files', '*.xlsx')],
            title='Simpan sebagai Excel'
        )
        if not path:
            return
        try:
            export_excel(self._validated_df, path)
            messagebox.showinfo('Export Berhasil', f'File disimpan:\n{path}')
            self._set_status(f'Export Excel: {path}', '#22c55e')
        except Exception as e:
            messagebox.showerror('Gagal Export', str(e))

    def _do_export_csv(self):
        if self._validated_df is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv')],
            title='Simpan sebagai CSV'
        )
        if not path:
            return
        try:
            export_csv(self._validated_df, path)
            messagebox.showinfo('Export Berhasil', f'File disimpan:\n{path}')
            self._set_status(f'Export CSV: {path}', '#22c55e')
        except Exception as e:
            messagebox.showerror('Gagal Export', str(e))
