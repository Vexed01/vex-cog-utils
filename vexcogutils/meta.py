from typing import Dict, List

from redbot.core import commands

from vexcogutils.loop import VexLoop

from .consts import CHECK, CROSS, DOCS_BASE
from .version import __version__


def format_help(self: commands.Cog, ctx: commands.Context) -> str:
    """Wrapper for format_help_for_context. **Not** currently for use outside my cogs.

    Thanks Sinbad.

    Parameters
    ----------
    self : commands.Cog
        The Cog class
    context : commands.Context
        Context

    Returns
    -------
    str
        Formatted help
    """
    docs = DOCS_BASE.format(self.qualified_name.lower())
    pre_processed = super(type(self), self).format_help_for_context(ctx)

    return (
        f"{pre_processed}\n\nAuthor: **`{self.__author__}`**\nCog Version: "
        f"**`{self.__version__}`**\n{docs}"
    )
    # adding docs link here so doesn't show up in auto generated docs


def format_info(
    qualified_name: str, version: str, extras: Dict[str, bool] = {}, loops: List[VexLoop] = []
) -> str:
    """Generate simple info text about the cog. **Not** currently for use outside my cogs.

    Parameters
    ----------
    qualified_name : str
        The name you want to show, eg "BetterUptime"
    version : str
        The version of the cog
    extras : Dict[str, bool], optional
        Dict with name as the key a bool as the value, by default {}
    loops : List[VexLoop], optional
        List of VexLoops you want to show

    Returns
    -------
    str
        Simple info text.
    """
    start = f"{qualified_name} by Vexed.\n<https://github.com/Vexed01/Vex-Cogs>\n\n"
    end = f"Cog Version: `{version}`\nUtils Version: `{__version__}`"

    extra = ""
    for loop in loops:
        extra += f"{loop.friendly_name}: `{CHECK if loop.integrity else CROSS}`\n"
    for key, value in extras.items():
        extra += f"{key}: `{CHECK if value else CROSS}`\n"

    return f"{start}{extra}{end}"
