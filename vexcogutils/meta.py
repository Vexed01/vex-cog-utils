from typing import Dict, List, Tuple, Union

import aiohttp
from packaging import version  # required by setuptools which is required by red
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


async def format_info(
    qualified_name: str, cog_version: str, extras: Dict[str, bool] = {}, loops: List[VexLoop] = []
) -> str:
    """Generate simple info text about the cog. **Not** currently for use outside my cogs.

    Parameters
    ----------
    qualified_name : str
        The name you want to show, eg "BetterUptime"
    cog_version : str
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
    try:
        latest_cog, latest_utils = _get_latest_ver(qualified_name.lower())
        cog_updated = CHECK if version.parse(cog_version) >= version.parse(latest_cog) else CROSS
        utils_updated = (
            CHECK if version.parse(__version__) >= version.parse(latest_utils) else CROSS
        )
    except Exception:  # anything and everything
        cog_updated = "Unknown"
        utils_updated = "Unknown"
    start = f"{qualified_name} by Vexed.\n<https://github.com/Vexed01/Vex-Cogs>\n\n"
    end = (
        f"Cog Version: `{cog_version}`, up to date: `{cog_updated}`\n"
        f"Utils Version: `{__version__}`, up to date: `{utils_updated}`"
    )

    extra = "".join(
        f"{loop.friendly_name}: `{CHECK if loop.integrity else CROSS}`\n" for loop in loops
    )

    for key, value in extras.items():
        extra += f"{key}: `{CHECK if value else CROSS}`\n"

    return f"{start}{extra}{end}"


async def _get_latest_ver(cog_name: str) -> Tuple[str, str]:
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            "https://vexed01.github.io/Vex-Cogs/api/v1/versions.json", timeout=3  # impatient :aha:
        )
        as_dict: dict = await resp.json()
        session.close()

    latest_cog = as_dict.get("cogs", {}).get(cog_name, "Unknown")
    latest_utils = as_dict.get("utils", "Unknown")
    return latest_cog, latest_utils
