"""
core/scorer.py — Sistem penilaian skor validasi data kependudukan.
"""

DEDUCTIONS = {
    'nik_invalid':        30,   # NIK tidak valid
    'nik_wali_invalid':   20,   # NIK Wali tidak valid
    'kk_invalid':         20,   # KK tidak valid
    'tgl_tidak_sesuai':   25,   # Tanggal lahir tidak sesuai NIK
    'tempat_tidak_sesuai': 15,  # Tempat lahir tidak sesuai wilayah NIK (Dukcapil)
    'address_kosong':     10,   # Address kosong
    'tempat_kosong':      10,   # Tempat lahir kosong
    'nik_duplikat':       15,   # NIK duplikat
    'kk_duplikat':        10,   # KK duplikat
}


def calculate_score(deductions: dict) -> int:
    """Hitung skor dari dictionary deductions (key → bool)."""
    score = 100
    for key, active in deductions.items():
        if active and key in DEDUCTIONS:
            score -= DEDUCTIONS[key]
    return max(0, score)


def get_tier(score: int) -> str:
    """Kembalikan label tier berdasarkan skor."""
    if score >= 90:
        return 'Valid'
    elif score >= 70:
        return 'Perlu Verifikasi'
    else:
        return 'Bermasalah'
