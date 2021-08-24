import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import sentry_sdk
from redbot.core import __version__ as red_version
from redbot.core import commands
from redbot.core.config import Config
from redbot.core.utils.common_filters import INVITE_URL_RE
from sentry_sdk import Hub

import vexcogutils
from vexcogutils.consts import (
    SENTRY_DSNS,
    SENTRY_MASTER_MSG,
    SENTRY_REMINDER_OFF,
    SENTRY_REMINDER_ON,
    SNOWFLAKE_REGEX,
)

log = logging.getLogger("red.vex-utils.sentry")

# SENTRY IS OPT-IN
#
# When a bot owner installes their first cog of mine, they will recieve a DM asking if they would
# like to start sending basic session data and error reporting, which applies to all of my cogs.
# They will then recieve a DM reminding then of their choice whenever they install one of my cogs.
#
# There are two types of messages sent to owners: "master" and "reminder":
# - The "master" message is the first message to the owner when they first load one of my cogs.
# - A "reminder" message will be sent whenever one of my cogs is loaded for the first time AND a
#   master message was sent previously. If Sentry is enabled, these will be sent every time a new
#   cog of mine is loaded. If Sentry is disabled, these will only be sent once per loading of a new
#   cog of mine IF it is the first cog loaded since last bot restart.
#   This has the added bonus of meaning that when this will be rolled out to all my cogs it will
#   only send 1 DM (or at least that's the plan...)
#
#
# I recommend anyone looking at this also takes a look at the Technical Details section of
# https://cogdocs.vexcodes.com/en/latest/telemetry.html


class SentryHelper:
    def __init__(self) -> None:
        self.sentry_enabled: Optional[bool] = None
        self.send_reminders: Optional[bool] = True
        self.uuid: Optional[str] = None
        self.hubs: Dict[str, Hub] = {}

        self.config: Config = Config.get_conf(
            self, 418078199982063626, force_registration=True, cog_name="Vex-Cog-Utils-Telemetry"
        )
        self.config.register_global(version=1)
        self.config.register_global(sentry_enabled=False)
        self.config.register_global(master_msg_sent=False)
        self.config.register_global(uuid=None)
        self.config.register_global(cogs_notified=[])

        asyncio.create_task(self._async_init())
        asyncio.create_task(self.periodic_session_restart())

        self.dont_send_reminders = False

        self.ready = False

    async def _async_init(self):
        sentry_enabled = await self.config.sentry_enabled()
        self.sentry_enabled = sentry_enabled

        # always set it, really doesn't do much
        uuid = await self.config.uuid()
        if uuid is None:
            uuid = str(uuid4())
            await self.config.uuid.set(uuid)
        self.uuid = uuid

        while vexcogutils.bot is None:
            await asyncio.sleep(0.1)
        vexcogutils.bot.add_cog(VexTelemetry(self))

        self.ready = True

    async def periodic_session_restart(self) -> None:
        # kinda ironic ish that this loop doesn't have sentry... maybe one day
        while True:
            try:
                log.debug("Sleeping 1 hour to next session restart...")
                await asyncio.sleep(60 * 60)  # 1hr
                if self.sentry_enabled is False:
                    log.debug("Telemetry disabled! Nothing to do.")
                else:
                    for cogname, hub in self.hubs.items():
                        hub.end_session()
                        hub.start_session()
                    log.debug("Sessions restarted.")
            except Exception as e:
                log.exception(
                    "Uh on! Something went wrong in the backend of telemetry. This hasn't been "
                    "automatically reported. Please send the below info to Vexed.",
                    e,
                )

    def remove_sensitive_data(self, event: dict, hint: dict) -> dict:
        """Remove sensitive data from the event. This should only be used by the Sentry SDK.

        This has two main parts:
        1) Remove any mentions of the bot's token
        2) Replace all IDs with a 4 digit number which originates from the timestamp of the ID
        3) Remove discord invites

        Parameters
        ----------
        event : dict
            Event data
        hint : dict
            Event hint

        Returns
        -------
        dict
            The event dict with above stated sensitive data removed.
        """

        def regex_stuff(s: str) -> str:
            """Shorten any Discord IDs/snowflakes (basically any number 17-20 characters) to 4 digits
            by locating the timestamp and getting the last 4 digits - the milliseconds and the last
            digit of the second countsecond.

            Parameters
            ----------
            s : str
                String to shorten IDs in

            Returns
            -------
            str
                String with IDs shortened
            """
            s = re.sub(
                SNOWFLAKE_REGEX, lambda m: "SHORTENED-ID-" + str(int(m.group()) >> 22)[-4:], s
            )
            return re.sub(INVITE_URL_RE, "DISCORD-INVITE-LINK", s)

        def recursive_replace(d: Union[Dict[str, Any], List, str], token: str) -> Union[dict, str]:
            """Recursively replace text in keys and values of a dictionary.

            Parameters
            ----------
            d : Union[Dict[str, Any], str]
                Dict or item to replace text in
            token : str
                Token to remove
            username : str
                Username to remove
            machinename : str
                Machine name to remove

            Returns
            -------
            dict
                Safe dict
            """
            if isinstance(d, dict):
                return {
                    regex_stuff(k.replace(token, "BOT-TOKEN"))
                    if isinstance(k, str)
                    else k: recursive_replace(v, token)
                    for k, v in d.items()
                }
            if isinstance(d, list):
                return [
                    regex_stuff(recursive_replace(i, token))  # type:ignore
                    if isinstance(i, str)
                    else recursive_replace(i, token)
                    for i in d
                ]
            return regex_stuff(d.replace(token, "BOT_TOKEN")) if isinstance(d, str) else d

        if vexcogutils.bot is not None:
            token = vexcogutils.bot.http.token
        else:
            token = ""  # this should almost never happen, because Sentry is initiated after this
            # value is set. anyhow, token removal is a "best effort".

        return recursive_replace(event, token)  # type:ignore

    async def enable_sentry(self) -> None:
        """Enable Sentry telemetry and error reporting."""
        await self.config.sentry_enabled.set(True)
        self.sentry_enabled = True
        self.dont_send_reminders = False

    async def disable_sentry(self) -> None:
        """Enable Sentry telemetry and error reporting."""
        await self.config.sentry_enabled.set(False)
        self.sentry_enabled = False
        self.dont_send_reminders = True

        for cogname, hub in self.hubs.items():
            hub.end_session()
            hub.client.close()

    async def get_sentry_hub(self, cogname: str, cogver: str) -> Hub:
        """Get a Sentry Hub and Client for a DSN. Each cog should have it's own project/DNS.

        Returns
        -------
        Hub
            A Sentry Hub with a Client
        """
        while self.ready is False:
            await asyncio.sleep(0.1)
        # not using sentry_sdk.init so other don't interfear with other CCs/cogs/packages
        # from https://github.com/getsentry/sentry-python/issues/610
        hub = sentry_sdk.Hub(
            sentry_sdk.Client(
                dsn=SENTRY_DSNS.get(cogname),
                traces_sample_rate=0.03,
                before_send=self.remove_sensitive_data,
                before_breadcrumb=self.remove_sensitive_data,
                release=f"{cogname}@{cogver}",
                debug=False,
                max_breadcrumbs=25,
            )
        )

        hub.scope.set_tag("utils_release", vexcogutils.__version__)
        hub.scope.set_tag("red_release", red_version)
        hub.scope.set_user({"id": self.uuid})

        self.hubs[cogname] = hub

        hub.start_session()
        return hub

    async def maybe_send_owners(self, cogname: str):
        while self.ready is False:
            await asyncio.sleep(0.1)

        assert vexcogutils.bot is not None

        if not await self.config.master_msg_sent():
            await self.config.master_msg_sent.set(True)
            await vexcogutils.bot.send_to_owners(SENTRY_MASTER_MSG.format(cogname))
            async with self.config.cogs_notified() as c_n:
                c_n.append(cogname)
            self.dont_send_reminders = True
            return

        if cogname in await self.config.cogs_notified():
            return
        if self.dont_send_reminders:
            async with self.config.cogs_notified() as c_n:
                c_n.append(cogname)
            # as it's disbaled, soft reminder ignored for now
            return

        if self.sentry_enabled:
            await vexcogutils.bot.send_to_owners(SENTRY_REMINDER_ON.format(cogname))
        else:
            self.dont_send_reminders = True
            await vexcogutils.bot.send_to_owners(SENTRY_REMINDER_OFF.format(cogname))

        async with self.config.cogs_notified() as c_n:
            c_n.append(cogname)


class VexTelemetry(commands.Cog):
    """
    Choose whether or not to send telemetry data and error logs to the Cog Author (Vexed),
    applying to all cogs in the Vex-Cogs repository (https://github.com/Vexed01/Vex-Cogs).

    **This helps me** (Vexed) **fix errors sooner and work out where to focus my time.** You should
    have received some information in a DM or wherever you have owner notifications configured to
    go. You can also take a look at the link below.

    To check whether it's enabled at the moment, run `[p]vextelemetry settings`.

    This data is handled through a service called Sentry.

    All commands here are, understandably, bot owner only.

    For more information, visit https://cogdocs.vexcodes.com/en/latest/telemetry.html
    """

    def __init__(self, sentryhelper: SentryHelper):
        self.sentryhelper = sentryhelper

    @commands.is_owner()
    @commands.group(invoke_without_command=True)
    async def vextelemetry(self, ctx: commands.Context):
        """
        Manage sending telemetry data and error logs to the Cog Author (Vexed),
        applying to all cogs in the Vex-Cogs repository (https://github.com/Vexed01/Vex-Cogs).

        This helps me (Vexed) fix errors sooner and work out where to focus my time.
        You should have received some information in a DM or wherever you have
        owner notifications configured to go.

        You can also take a look at the link below.

        A service called Sentry is used to handle this data.

        For more information, visit https://cogdocs.vexcodes.com/en/latest/telemetry.html
        """
        await ctx.send_help()
        thing = "enabled" if self.sentryhelper.sentry_enabled else "not enabled"
        await ctx.send(f"Telemetry is currently **{thing}**.")

    @vextelemetry.command()
    async def enable(self, ctx: commands.Context):
        """Enable telementry and error reporting."""
        await self.sentryhelper.enable_sentry()
        await ctx.send(
            "Telemetry and error reporting has been enabled. Thanks for helping improve my cogs!"
            "\n\nThis will take effect when you reload my cogs or restart your bot.\n\n"
            f"You can disable it at any time with `{ctx.clean_prefix}vextelemetry disable`."
        )

    @vextelemetry.command()
    async def disable(self, ctx: commands.Context):
        """Disable telementry and error reporting."""
        await self.sentryhelper.disable_sentry()
        await ctx.send(
            "Telemetry and error reporting has been disabled.\n\n**You will need to reload all my "
            "cogs or restart your bot for these changes to take effect.**\n\n"
            f"You can enabled it at any time with `{ctx.clean_prefix}vextelemetry enable`."
        )

    @vextelemetry.command()
    async def settings(self, ctx: commands.Context):
        """Check if telemetry is currently enabled or not."""
        thing = "enabled" if self.sentryhelper.sentry_enabled else "not enabled"
        await ctx.send(f"Telemetry is currently **{thing}**.")
