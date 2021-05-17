from typing import Dict, List, Mapping, Optional, Tuple

import aiohttp
import tabulate
from packaging import version  # required by setuptools which is required by red
from redbot.core import commands
from redbot.core.utils.chat_formatting import box

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
    qualified_name: str,
    cog_version: str,
    extras: Dict[str, Mapping[str, bool]] = {},
    loops: List[VexLoop] = [],
) -> str:
    """Generate simple info text about the cog. **Not** currently for use outside my cogs.

    Parameters
    ----------
    qualified_name : str
        The name you want to show, eg "BetterUptime"
    cog_version : str
        The version of the cog
    extras : Dict[str, Mapping[str, bool]], optional
        Dict which is foramtted as key: value\\n. Bools as a value will be replaced with
        check/cross emojis, by default {}
    loops : List[VexLoop], optional
        List of VexLoops you want to show, by default []

    Returns
    -------
    str
        Simple info text.
    """
    try:
        latest_cog, latest_utils = await _get_latest_ver(qualified_name.lower())
        if latest_cog is None:
            cog_updated = "Unknown"
        else:
            cog_updated = (
                CHECK if version.parse(cog_version) >= version.parse(latest_cog) else CROSS
            )

        if latest_utils is None:
            utils_updated = "Unknown"
        else:
            utils_updated = (
                CHECK if version.parse(__version__) >= version.parse(latest_utils) else CROSS
            )
    except Exception:  # anything and everything
        cog_updated = "Unknown"
        utils_updated = "Unknown"
    start = f"{qualified_name} by Vexed.\n<https://github.com/Vexed01/Vex-Cogs>\n\n"
    versions = [
        ["Cog", cog_version, cog_updated],
        ["Utils", __version__, utils_updated],
    ]

    data = []
    if loops:
        for loop in loops:
            data.append([loop.friendly_name, CHECK if loop.integrity else CROSS])

    if extras:
        if data:
            data.append([])
        for key, value in extras.items():
            if isinstance(value, bool):
                str_value = CHECK if value else CROSS
            else:
                assert isinstance(value, str)
                str_value = value
            data.append([key, str_value])

    boxed = box(tabulate.tabulate(versions, headers=["", "Version", "Up to date?"]))
    if data:
        boxed += box(tabulate.tabulate(data, tablefmt="simple"))

    return f"{start}{boxed}"


async def _get_latest_ver(cog_name: str) -> Tuple[Optional[str], Optional[str]]:
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            "https://vexed01.github.io/Vex-Cogs/api/v1/versions.json", timeout=3  # impatient :aha:
        )
        as_dict: dict = await resp.json()
        await session.close()

    latest_cog = as_dict.get("cogs", {}).get(cog_name)
    latest_utils = as_dict.get("utils")
    return latest_cog, latest_utils
