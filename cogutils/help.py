from typing import Dict, Optional

from discord.ext.tasks import Loop
from redbot.core import commands

from .consts import CHECK, CROSS, DOCS_BASE


def format_help(self: commands.Cog, ctx: commands.Context) -> str:
    """Wrapper for format_help_for_context. **Not** for use outside my cogs.

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

    return f"{pre_processed}\n\nAuthor: **`{self.__author__}`**\nCog Version: **`{self.__version__}`**\n{docs}"
    # adding docs link here so doesn't show up in auto generated docs


def format_info(qualified_name: str, version: str, loops: Optional[Dict[str, Loop]] = {}) -> str:
    """Generate simple info text about the cog. **Can** be used outside my cogs.

    Parameters
    ----------
    qualified_name : str
        The name you want to show, eg "BetterUptime"
    version : str
        The version of the cog
    loops : Dict[str, Loop], optional
        Dict with name as the key and the discord.py loop as the value, by default {}

    Returns
    -------
    str
        Simple info text.
    """
    start = f"{qualified_name} by Vexed.\n<https://github.com/Vexed01/Vex-Cogs>\n\n"
    end = f"Version: `{version}`"

    extra = ""
    for name, loop in loops.items():
        extra += f"{name}: `{CHECK if loop.is_running() else CROSS}`\n"

    return f"{start}{loops}{end}"
