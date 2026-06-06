"""
core/validator.py — Logika validasi data kependudukan.

Validasi yang dilakukan:
  1. NIK  : 16 digit, numerik, tidak kosong
  2. KK   : 16 digit, numerik, tidak kosong
  3. Nama : tidak kosong
  4. Tempat Lahir : tidak kosong
  5. Tanggal Lahir : format valid
  6. Tanggal Lahir vs NIK : cocok dengan digit 7-12 NIK
  7. Tempat Lahir vs NIK  : cocok dengan kode wilayah digit 1-4 NIK (referensi Dukcapil)
  8. NIK Duplikat
  9. KK Duplikat
"""

import re
import pandas as pd
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional, Tuple, List

from data.wilayah import KODE_WILAYAH, KODE_PROVINSI, ALIAS_WILAYAH


REQUIRED_COLUMNS = ['PARENT_ID', 'NIK', 'KK', 'ADDRESS', 'BORN_IN', 'BORN_AT']

# ─── Normalisasi ─────────────────────────────────────────────────────────────

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).upper().strip() for c in df.columns]
    return df


def check_required_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def _normalize_id(val) -> Optional[str]:
    """Normalisasi NIK/KK ke string 16 digit; None jika tidak valid."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        s = str(int(float(str(val).strip())))
    except Exception:
        s = re.sub(r'\D', '', str(val).strip())
    return s if (s.isdigit() and len(s) == 16) else None


def _clean_str(val) -> str:
    """Bersihkan nilai menjadi string strip."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ''
    return str(val).strip()


# ─── Validasi NIK ─────────────────────────────────────────────────────────────

def validate_nik(val) -> Tuple[bool, str]:
    s = _clean_str(val)
    if not s:
        return False, 'NIK Kosong'
    digits = re.sub(r'\D', '', s)
    if not digits:
        return False, 'NIK Tidak Numerik'
    if len(digits) != 16:
        return False, f'NIK Tidak 16 Digit ({len(digits)} digit)'
    prov = digits[:2]
    if prov not in KODE_PROVINSI:
        return False, 'NIK Kode Provinsi Tidak Valid'
    return True, ''


def validate_kk(val) -> Tuple[bool, str]:
    s = _clean_str(val)
    if not s:
        return False, 'KK Kosong'
    digits = re.sub(r'\D', '', s)
    if not digits:
        return False, 'KK Tidak Numerik'
    if len(digits) != 16:
        return False, f'KK Tidak 16 Digit ({len(digits)} digit)'
    return True, ''


def validate_address(val) -> Tuple[bool, str]:
    s = _clean_str(val)
    if not s:
        return False, 'Address Kosong'
    return True, ''


def validate_tempat_lahir(val) -> Tuple[bool, str]:
    s = _clean_str(val)
    if not s:
        return False, 'Tempat Lahir Kosong'
    return True, ''


def validate_tanggal_lahir(val) -> Tuple[bool, str]:
    s = _clean_str(val)
    if not s:
        return False, 'Tanggal Lahir Kosong'
    try:
        parsed = pd.to_datetime(s, format='mixed', dayfirst=True, errors='coerce')
        if pd.isna(parsed):
            return False, 'Format Tanggal Tidak Valid'
        return True, ''
    except Exception:
        return False, 'Format Tanggal Tidak Valid'


# ─── Validasi Tanggal Lahir vs NIK ───────────────────────────────────────────

def _extract_birthdate_from_nik(nik16: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Kembalikan (day, month, year) dari NIK 16 digit. Perempuan: day>40."""
    try:
        day   = int(nik16[6:8])
        month = int(nik16[8:10])
        yr2   = int(nik16[10:12])
        if day > 40:
            day -= 40          # perempuan
        curr2 = datetime.now().year % 100
        year  = 2000 + yr2 if yr2 <= curr2 else 1900 + yr2
        if not (1 <= day <= 31 and 1 <= month <= 12):
            return None, None, None
        return day, month, year
    except Exception:
        return None, None, None


def validate_tgl_vs_nik(nik_val, tgl_val) -> Tuple[bool, str]:
    nik16 = _normalize_id(nik_val)
    if not nik16:
        return True, ''           # NIK tidak valid, skip
    tgl_ok, _ = validate_tanggal_lahir(tgl_val)
    if not tgl_ok:
        return True, ''           # Tanggal tidak valid, skip
    day_n, month_n, year_n = _extract_birthdate_from_nik(nik16)
    if day_n is None:
        return True, ''
    try:
        actual = pd.to_datetime(_clean_str(tgl_val), format='mixed', dayfirst=True, errors='coerce')
        if pd.isna(actual):
            return True, ''
        if actual.day == day_n and actual.month == month_n and actual.year == year_n:
            return True, ''
        return False, f'Tanggal Lahir Tidak Sesuai NIK (NIK: {day_n:02d}-{month_n:02d}-{year_n})'
    except Exception:
        return True, ''


# ─── Validasi Tempat Lahir vs Wilayah NIK (referensi Dukcapil) ───────────────

def _normalize_wilayah(s: str) -> str:
    """Normalisasi nama wilayah: uppercase, hapus prefix."""
    s = s.upper().strip()
    for prefix in ['KABUPATEN ', 'KAB. ', 'KAB ', 'KOTA ADMINISTRASI ',
                   'KOTA ', 'KEPULAUAN ', 'KP. ']:
        s = s.replace(prefix, '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _wilayah_match(tempat: str, wilayah_ref: str) -> bool:
    """Cocokkan tempat lahir dengan nama wilayah referensi (fuzzy)."""
    t = _normalize_wilayah(tempat)
    w = _normalize_wilayah(wilayah_ref)
    if not t or not w:
        return False
    # Exact / substring match
    if t == w or t in w or w in t:
        return True
    # Rasio kemiripan ≥ 0.78
    ratio = SequenceMatcher(None, t, w).ratio()
    return ratio >= 0.78


def _expand_aliases(tempat: str) -> List[str]:
    """Kembalikan daftar kemungkinan nama wilayah dari alias."""
    t = tempat.upper().strip()
    result = [t]
    for alias, targets in ALIAS_WILAYAH.items():
        if alias in t:
            result.extend(targets)
    return result


def validate_tempat_vs_nik(nik_val, tempat_val) -> Tuple[bool, str]:
    """
    Validasi tempat lahir berdasarkan kode wilayah di NIK.
    Menggunakan referensi database wilayah Kemendagri (proxy Dukcapil).
    """
    nik16 = _normalize_id(nik_val)
    tempat = _clean_str(tempat_val)

    if not nik16 or not tempat:
        return True, ''   # Tidak bisa dibandingkan

    kode4 = nik16[:4]   # Kode kabupaten/kota
    kode2 = nik16[:2]   # Kode provinsi

    # Cari nama wilayah dari database
    wilayah_kab  = KODE_WILAYAH.get(kode4)
    wilayah_prov = KODE_PROVINSI.get(kode2)

    if wilayah_kab is None and wilayah_prov is None:
        return True, ''   # Kode tidak ada di database, skip

    # Kumpulkan semua referensi yang mungkin cocok
    candidates = []
    if wilayah_kab:
        candidates.append(wilayah_kab)
    if wilayah_prov:
        candidates.append(wilayah_prov)

    # Expand alias tempat lahir
    tempat_candidates = _expand_aliases(tempat)

    for tp in tempat_candidates:
        for ref in candidates:
            if _wilayah_match(tp, ref):
                return True, ''

    # Jika wilayah kab ditemukan tapi tidak cocok
    if wilayah_kab:
        ref_code = kode4
        ref_name = wilayah_kab
    else:
        ref_code = kode2
        ref_name = wilayah_prov
    return False, f'Tempat Lahir Tidak Sesuai Wilayah NIK (Seharusnya: kode {ref_code} {ref_name})'


# ─── Deteksi Duplikat ─────────────────────────────────────────────────────────

def detect_duplicates(df: pd.DataFrame):
    nik_norm = [_normalize_id(v) for v in df['NIK']]
    kk_norm  = [_normalize_id(v) for v in df['KK']]
    nik_dup  = {k for k, c in Counter(v for v in nik_norm if v).items() if c > 1}
    kk_dup   = {k for k, c in Counter(v for v in kk_norm  if v).items() if c > 1}
    return nik_dup, kk_dup, nik_norm, kk_norm


# ─── Validasi DataFrame Utama ─────────────────────────────────────────────────

def validate_dataframe(df: pd.DataFrame):
    """
    Validasi seluruh DataFrame.
    Returns: (df_result, nik_dup_set, kk_dup_set)
    """
    from core.scorer import calculate_score, get_tier

    df = normalize_columns(df)
    df = df.reset_index(drop=True)

    nik_dup_set, kk_dup_set, nik_norm, kk_norm = detect_duplicates(df)

    statuses, scores, tiers = [], [], []

    for idx in range(len(df)):
        row = df.iloc[idx]
        errors = []
        ded    = {}

        parent_id_val = row.get('PARENT_ID', '')
        nik_val    = row.get('NIK', '')
        kk_val     = row.get('KK', '')
        address_val   = row.get('ADDRESS', '')
        tempat_val = row.get('BORN_IN', '')
        tgl_val    = row.get('BORN_AT', '')

        # 1. NIK
        nik_ok, e = validate_nik(nik_val)
        if not nik_ok:
            errors.append(e); ded['nik_invalid'] = True

        # NIK Wali
        parent_ok, e = validate_nik(parent_id_val)
        if not parent_ok:
            errors.append(f"Wali: {e}"); ded['nik_wali_invalid'] = True

        # 2. KK
        kk_ok, e = validate_kk(kk_val)
        if not kk_ok:
            errors.append(e); ded['kk_invalid'] = True

        # 3. Address
        address_ok, e = validate_address(address_val)
        if not address_ok:
            errors.append(e); ded['address_kosong'] = True

        # 4. Tempat Lahir (tidak kosong)
        tempat_ok, e = validate_tempat_lahir(tempat_val)
        if not tempat_ok:
            errors.append(e); ded['tempat_kosong'] = True

        # 5. Tanggal Lahir
        tgl_ok, e = validate_tanggal_lahir(tgl_val)
        if not tgl_ok:
            errors.append(e)

        # 6. Tanggal vs NIK
        if nik_ok and tgl_ok:
            ok, e = validate_tgl_vs_nik(nik_val, tgl_val)
            if not ok:
                errors.append(e); ded['tgl_tidak_sesuai'] = True

        # 7. Tempat Lahir vs Wilayah NIK (Dukcapil)
        if nik_ok and tempat_ok:
            ok, e = validate_tempat_vs_nik(nik_val, tempat_val)
            if not ok:
                errors.append(e); ded['tempat_tidak_sesuai'] = True

        # 8. NIK Duplikat
        if nik_norm[idx] in nik_dup_set:
            errors.append('NIK Duplikat'); ded['nik_duplikat'] = True

        # 9. KK Duplikat
        if kk_norm[idx] in kk_dup_set:
            errors.append('KK Duplikat'); ded['kk_duplikat'] = True

        score  = calculate_score(ded)
        tier   = get_tier(score)
        status = 'VALID' if not errors else ' | '.join(errors)

        statuses.append(status)
        scores.append(score)
        tiers.append(tier)

    df = df.copy()
    df['STATUS']             = statuses
    df['SKOR']               = scores
    df['TINGKAT_KESESUAIAN'] = tiers

    return df, nik_dup_set, kk_dup_set
