"""
ui/dashboard.py — Panel statistik kartu di bagian atas dan grafik pie chart.
"""

import customtkinter as ctk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Warna kartu (fg_color)
CARD_COLORS = {
    'TOTAL DATA':       '#1e3a5f',
    'DATA VALID':       '#14532d',
    'TIDAK VALID':      '#7f1d1d',
    '% VALIDASI':       '#164e63',
    'NIK DUPLIKAT':     '#7c2d12',
    'KK DUPLIKAT':      '#4a1d96',
    'TGL TIDAK COCOK':  '#713f12',
}

CARD_TEXT_COLORS = {
    'TOTAL DATA':       '#93c5fd',
    'DATA VALID':       '#86efac',
    'TIDAK VALID':      '#fca5a5',
    '% VALIDASI':       '#67e8f9',
    'NIK DUPLIKAT':     '#fdba74',
    'KK DUPLIKAT':      '#c4b5fd',
    'TGL TIDAK COCOK':  '#fde68a',
}


class StatCard(ctk.CTkFrame):
    """Kartu statistik individual."""

    def __init__(self, master, key: str, **kwargs):
        bg = CARD_COLORS.get(key, '#1e293b')
        super().__init__(master, corner_radius=12, fg_color=bg, **kwargs)
        self._key = key
        tc = CARD_TEXT_COLORS.get(key, '#94a3b8')

        self._label = ctk.CTkLabel(
            self, text=key,
            font=ctk.CTkFont(size=10, weight='bold'),
            text_color='#94a3b8'
        )
        self._label.pack(pady=(12, 0), padx=10)

        self._value = ctk.CTkLabel(
            self, text='—',
            font=ctk.CTkFont(size=26, weight='bold'),
            text_color=tc
        )
        self._value.pack(pady=(2, 12), padx=10)

    def set_value(self, val, suffix=''):
        self._value.configure(text=f'{val}{suffix}')

    def reset(self):
        self._value.configure(text='—')


class DashboardPanel(ctk.CTkFrame):
    """Panel kartu statistik dan grafik Pie."""

    KEYS = [
        'TOTAL DATA', 'DATA VALID', 'TIDAK VALID', '% VALIDASI',
        'NIK DUPLIKAT', 'KK DUPLIKAT', 'TGL TIDAK COCOK'
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.columnconfigure(0, weight=3) # Cards
        self.columnconfigure(1, weight=1) # Pie chart

        # --- Cards Frame ---
        self.cards_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.cards_frame.grid(row=0, column=0, sticky='nsew')
        
        for i in range(4):
            self.cards_frame.columnconfigure(i, weight=1)

        self._cards = {}
        for i, key in enumerate(self.KEYS):
            r = i // 4
            c = i % 4
            card = StatCard(self.cards_frame, key=key)
            card.grid(row=r, column=c, padx=4, pady=4, sticky='ew')
            self._cards[key] = card

        # --- Chart Frame ---
        self.chart_frame = ctk.CTkFrame(self, fg_color='#111827', corner_radius=12)
        self.chart_frame.grid(row=0, column=1, padx=(8, 4), pady=4, sticky='nsew')
        self.chart_frame.pack_propagate(False)

        self.figure = Figure(figsize=(2, 2), dpi=90, facecolor='#111827')
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        self._draw_pie([1], ['Data Kosong'], ['#334155'])

    def _draw_pie(self, sizes, labels, colors):
        self.ax.clear()
        self.ax.pie(
            sizes, labels=labels, colors=colors, 
            autopct='%1.1f%%', startangle=90, 
            textprops={'color': '#e2e8f0', 'fontsize': 9, 'weight': 'bold'}
        )
        self.ax.axis('equal')
        self.figure.tight_layout(pad=0)
        self.canvas.draw()

    def update_stats(self, df, nik_dup_set: set, kk_dup_set: set) -> None:
        total   = len(df)
        valid   = int((df['TINGKAT_KESESUAIAN'] == 'Valid').sum())
        invalid = total - valid
        nik_dup = int(df['STATUS'].str.contains('NIK Duplikat', na=False).sum())
        kk_dup  = int(df['STATUS'].str.contains('KK Duplikat', na=False).sum())
        tgl_err = int(df['STATUS'].str.contains('Tidak Sesuai NIK', na=False).sum())
        persen  = round(valid / total * 100, 1) if total else 0.0

        self._cards['TOTAL DATA'].set_value(f'{total:,}')
        self._cards['DATA VALID'].set_value(f'{valid:,}')
        self._cards['TIDAK VALID'].set_value(f'{invalid:,}')
        self._cards['NIK DUPLIKAT'].set_value(f'{nik_dup:,}')
        self._cards['KK DUPLIKAT'].set_value(f'{kk_dup:,}')
        self._cards['TGL TIDAK COCOK'].set_value(f'{tgl_err:,}')
        self._cards['% VALIDASI'].set_value(persen, '%')

        if total > 0:
            if valid == total:
                self._draw_pie([valid], ['Valid'], ['#22c55e'])
            elif valid == 0:
                self._draw_pie([invalid], ['Tdk Valid'], ['#ef4444'])
            else:
                self._draw_pie([valid, invalid], ['Valid', 'Tdk Valid'], ['#22c55e', '#ef4444'])

    def reset(self) -> None:
        for card in self._cards.values():
            card.reset()
        self._draw_pie([1], ['Data Kosong'], ['#334155'])
