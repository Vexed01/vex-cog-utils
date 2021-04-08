from typing import Sequence

from redbot.core.utils.chat_formatting import humanize_list, inline


def inline_hum_list(items: Sequence[str], *, style: str = "standard") -> str:
    """Similar to core's humanize_list, but all items are in inline code blocks.

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
