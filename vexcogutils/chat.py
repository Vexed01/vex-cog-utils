from typing import Sequence, Union

from redbot.core.utils.chat_formatting import humanize_list, humanize_number, inline


def _hum(num: Union[int, float], unit: str, ndigits: int) -> str:
    """Round a number, then humanize."""
    return humanize_number(round(num, ndigits)) + f" {unit}"


def humanize_bytes(bytes: Union[int, float], ndigits: int = 0) -> str:
    """Humanize a number of bytes, rounding to ndigits. Only supports up to GB.

    This assumes 1GB = 1000MB, 1MB = 1000KB, 1KB = 1000B"""
    if bytes > 10000000000:  # 10GB
        gb = bytes / 1000000000
        return _hum(gb, "GB", ndigits)
    if bytes > 10000000:  # 10MB
        mb = bytes / 1000000
        return _hum(mb, "MB", ndigits)
    if bytes > 10000:  # 10KB
        kb = bytes / 1000
        return _hum(kb, "KB", ndigits)
    return _hum(bytes, "B", ndigits)


# maybe think about adding to core
def inline_hum_list(items: Sequence[str], *, style: str = "standard") -> str:
    """Similar to core's humanize_list, but all items are in inline code blocks. **Can** be used
    outside my cogs.

    Strips leading and trailing whitespace.

    Does not support locale.

    Does support style (see core's docs for available styles)

    Parameters
    ----------
    items : Sequence[str]
        The items to humanize
    style : str, optional
        The style. See core's docs, by default "standard"

    Returns
    -------
    str
        Humanized inline list.
    """
    inline_list = [inline(i.strip()) for i in items]
    return humanize_list(inline_list, style=style)
