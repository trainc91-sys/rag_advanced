def format_citation(row):
    """
    Format a clean citation string using metadata fields.
    Format: [Title | Code | Article | Chunk ID]
    """
    title = str(row.get('title', '')).strip() if not pd_isna(row.get('title')) else ""
    code = str(row.get('so_ky_hieu', '')).strip() if not pd_isna(row.get('so_ky_hieu')) else ""
    article = str(row.get('article', '')).strip() if not pd_isna(row.get('article')) else ""
    chunk_id = str(row.get('chunk_id', '')).strip()

    parts = []
    if title:
        parts.append(title)
    if code:
        parts.append(code)
    if article:
        parts.append(article)
    parts.append(chunk_id)

    return " | ".join(parts)

def pd_isna(val):
    if val is None:
        return True
    if isinstance(val, float) and str(val) == 'nan':
        return True
    if str(val).strip().lower() in ['', 'nan', 'none']:
        return True
    return False
