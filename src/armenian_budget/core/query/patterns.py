from __future__ import annotations

from typing import Iterable, List, Tuple
import re
import unicodedata


_NON_ALNUM_RE = re.compile(r"[^\w]+", flags=re.UNICODE)


def normalize_armenian_text(text: str) -> str:
    """Lightweight normalizer for Armenian text.

    - Unicode NFKC normalization
    - Lowercase
    - Remove combining marks
    - Collapse non-alphanumeric runs to a single space
    - Trim spaces

    Note: This is intentionally conservative and language-agnostic. It keeps
    Armenian letters, Latin, digits. It does not attempt transliteration.
    """
    if text is None:
        return ""
    # Normalize and lowercase
    t = unicodedata.normalize("NFKC", str(text)).lower()
    # Drop combining marks
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    # Replace runs of non-alphanumerics with single space
    t = _NON_ALNUM_RE.sub(" ", t)
    # Collapse spaces
    t = " ".join(t.split())
    return t


def _tokenize(text: str) -> List[str]:
    nt = normalize_armenian_text(text)
    return nt.split() if nt else []


def _match_strict(value_tokens: List[str], pattern_tokens: List[str]) -> bool:
    """Strict matching: require any pattern token to match a whole token exactly."""
    if not value_tokens or not pattern_tokens:
        return False
    vs = set(value_tokens)
    for pt in pattern_tokens:
        if pt in vs:
            return True
    return False


def _match_balanced(value_tokens: List[str], pattern_tokens: List[str]) -> bool:
    """Balanced matching:
    - Exact token match OR
    - Token startswith pattern with a minimum pattern length (>=4) OR
    - Token contains pattern when pattern length is reasonably specific (>=6)
    This heuristic aims to avoid spurious substring hits like short stems.
    """
    if not value_tokens or not pattern_tokens:
        return False
    vs = set(value_tokens)
    for pt in pattern_tokens:
        if pt in vs:
            return True
        if len(pt) >= 4:
            for vt in value_tokens:
                if vt.startswith(pt):
                    return True
        if len(pt) >= 6:
            for vt in value_tokens:
                if pt in vt:
                    return True
    return False


def _match_permissive(value_norm: str, patterns_norm: List[str]) -> bool:
    """Permissive: any normalized pattern appears anywhere in normalized value."""
    if not value_norm or not patterns_norm:
        return False
    for p in patterns_norm:
        if p and p in value_norm:
            return True
    return False


def build_pattern_candidates(
    values: Iterable[str],
    patterns: Iterable[str],
    *,
    mode: str = "balanced",
    exclude: Iterable[str] | None = None,
) -> Tuple[List[str], List[str]]:
    """Return (include_values, exclude_suggestions) based on simple Armenian-aware matching.

    - values: universe of field values to consider (distinct values from the dataset)
    - patterns: user-provided pattern strings
    - mode: 'strict' | 'balanced' | 'permissive' (aliases supported: 'whole_word', 'normalized', 'contains')
    - exclude: explicit values to exclude from the include set

    The implementation is intentionally heuristic and fast; it can be refined
    later with better linguistic handling and fuzzy scoring.
    """
    vals_list = [v for v in values if v is not None]
    pats_list = [p for p in patterns if p is not None]

    # Normalize once
    vals_norm = [normalize_armenian_text(v) for v in vals_list]
    pats_norm = [normalize_armenian_text(p) for p in pats_list]

    # Tokenize for token-based modes
    vals_tokens = [_tokenize(v) for v in vals_list]
    pats_tokens = [_tokenize(p) for p in pats_list]

    mode_l = (mode or "balanced").strip().lower()
    if mode_l in {"whole_word"}:
        mode_l = "strict"
    if mode_l in {"normalized"}:
        mode_l = "balanced"
    if mode_l in {"contains"}:
        mode_l = "permissive"

    include: List[str] = []

    for i, original_value in enumerate(vals_list):
        if not original_value:
            continue
        vtoks = vals_tokens[i]
        vnorm = vals_norm[i]

        match = False
        if mode_l == "strict":
            for ptoks in pats_tokens:
                if _match_strict(vtoks, ptoks):
                    match = True
                    break
        elif mode_l == "permissive":
            if _match_permissive(vnorm, pats_norm):
                match = True
        else:  # balanced
            for ptoks in pats_tokens:
                if _match_balanced(vtoks, ptoks):
                    match = True
                    break

        if match:
            include.append(original_value)

    # Apply explicit exclusions by normalized equality
    exc_list = list(exclude or [])
    exc_norm = {normalize_armenian_text(x) for x in exc_list}
    if exc_norm:
        filtered: List[str] = []
        for i, v in enumerate(include):
            if normalize_armenian_text(v) in exc_norm:
                continue
            filtered.append(v)
        include = filtered

    # No strong heuristics for exclude suggestions yet; return empty list placeholder
    return include, []

