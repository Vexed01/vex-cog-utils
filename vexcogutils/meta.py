from logging import getLogger
from typing import Dict, List, NamedTuple, Union

import aiohttp
import tabulate
from redbot.core import VersionInfo, commands
from redbot.core import version_info as red_version
from redbot.core.utils.chat_formatting import box

from vexcogutils.loop import VexLoop

from .consts import CHECK, CROSS, DOCS_BASE
from .version import __version__ as utils_version

log = getLogger("red.vex-utils")


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


# TODO: get utils version directly from pypi and stop using red internal util


async def format_info(
    qualified_name: str,
    cog_version: str,
    extras: Dict[str, Union[str, bool]] = {},
    loops: List[VexLoop] = [],
) -> str:
    """Generate simple info text about the cog. **Not** currently for use outside my cogs.

    Parameters
    ----------
    qualified_name : str
        The name you want to show, eg "BetterUptime"
    cog_version : str
        The version of the cog
    extras : Dict[str, Union[str, bool]], optional
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
        latest = await _get_latest_vers(qualified_name.lower())

        cog_updated = CHECK if VersionInfo.from_str(cog_version) >= latest.cog else CROSS
        utils_updated = CHECK if VersionInfo.from_str(utils_version) >= latest.utils else CROSS
        red_updated = CHECK if red_version >= latest.red else CROSS
    except Exception:  # anything and everything, eg aiohttp error or version parsing error
        log.warning("Unable to parse versions.", exc_info=True)
        cog_updated = "Unknown"
        utils_updated = "Unknown"
        red_updated = "Unknown"

    start = f"{qualified_name} by Vexed.\n<https://github.com/Vexed01/Vex-Cogs>\n\n"
    versions = [
        ["Cog", cog_version, cog_updated],
        ["Utils", utils_version, utils_updated],
        ["Red", str(red_version), red_updated],
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
        boxed += box(tabulate.tabulate(data, tablefmt="plain"))

    return f"{start}{boxed}"


async def out_of_date_check(cogname: str, currentver: str) -> None:
    """Send a log at warning level if the cog is out of date."""
    try:
        vers = await _get_latest_vers(cogname)
    except Exception as e:
        log.warning(f"Something went wrong checking if {cogname} cog is up to date. See below.")
        return
    if VersionInfo.from_str(currentver) < vers.cog:
        log.warning(
            f"Your {cogname} cog, from Vex, is out of date. You can update your cogs with the "
            "'cog update' command in Discord."
        )
    else:
        log.debug(f"{cogname} cog is up to date")


class Vers(NamedTuple):
    cog: VersionInfo
    utils: VersionInfo
    red: VersionInfo


async def _get_latest_vers(cog_name: str) -> Vers:
    data: dict
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://static.vexcodes.com/v1/versions.json", timeout=3  # ik its called static :)
        ) as r:
            data = await r.json()
            latest_cog = VersionInfo.from_str(data.get("cogs", {}).get(cog_name, "0.0.0"))
        async with session.get("https://pypi.org/pypi/Red-DiscordBot/json", timeout=3) as r:
            data = await r.json()
            latest_red = VersionInfo.from_str(data.get("info", {}).get("version", "0.0.0"))
        async with session.get("https://pypi.org/pypi/vex-cog-utils/json", timeout=3) as r:
            data = await r.json()
            latest_utils = VersionInfo.from_str(data.get("info", {}).get("version", "0.0.0"))

    return Vers(latest_cog, latest_utils, latest_red)
