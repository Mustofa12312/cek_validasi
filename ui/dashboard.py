"""
ui/dashboard.py — Panel statistik 7 kartu di bagian atas.
"""

import customtkinter as ctk

# Warna kartu (fg_color)
CARD_COLORS = {
    'TOTAL DATA':       '#1e3a5f',
    'DATA VALID':       '#14532d',
    'TIDAK VALID':      '#7f1d1d',
    'NIK DUPLIKAT':     '#7c2d12',
    'KK DUPLIKAT':      '#4a1d96',
    'TGL TIDAK COCOK':  '#713f12',
    '% VALIDASI':       '#164e63',
}

CARD_TEXT_COLORS = {
    'TOTAL DATA':       '#93c5fd',
    'DATA VALID':       '#86efac',
    'TIDAK VALID':      '#fca5a5',
    'NIK DUPLIKAT':     '#fdba74',
    'KK DUPLIKAT':      '#c4b5fd',
    'TGL TIDAK COCOK':  '#fde68a',
    '% VALIDASI':       '#67e8f9',
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
    """Panel 7 kartu statistik."""

    KEYS = [
        'TOTAL DATA', 'DATA VALID', 'TIDAK VALID',
        'NIK DUPLIKAT', 'KK DUPLIKAT', 'TGL TIDAK COCOK', '% VALIDASI',
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self._cards = {}

        for i, key in enumerate(self.KEYS):
            self.columnconfigure(i, weight=1)
            card = StatCard(self, key=key)
            card.grid(row=0, column=i, padx=4, pady=4, sticky='ew')
            self._cards[key] = card

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

    def reset(self) -> None:
        for card in self._cards.values():
            card.reset()
