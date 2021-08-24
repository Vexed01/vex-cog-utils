DOCS_BASE = (
    "This cog has docs! Check them out at\nhttps://cogdocs.vexcodes.com/en/latest/cogs/{}.html"
)

CHECK = "\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16}"
CROSS = "\N{CROSS MARK}"

SNOWFLAKE_REGEX = r"\b\d{17,20}\b"

SENTRY_MASTER_MSG = (
    "Hey there! This looks like the first time you're using this cog (or you just updated to a "
    "version which supports this). To help make this cog, and all my others, as good "
    "and bug-free as possible, I have **opt-in** telemetry and error reporting __which affects "
    "all of my (github.com/Vexed01's) cogs__ on the Vex-Cogs repository, using Sentry. The "
    "telemetry consists of data on the cog release and performance data of backgroup tasks and "
    "loops (if applicable), and error reporting means that if something goes wrong the error and "
    "some associated data will be automatically sent to me so I can fix it quickly.\n\nA best "
    "effort is made to ensure no sensitive data is transmitted. For more information, including "
    "some technical details, visit <https://cogdocs.vexcodes.com/en/latest/telemetry.html>\n\n"
    "**If you would like to opt-in to telemetry and error reporting, and help me develop my cogs, "
    "run the command `[p]vextelemetry enable`. `[p]` is your prefix.**\nNo data is collected "
    "relating to command usage."
)

SENTRY_REMINDER_ON = (
    "Hey there! You just installed Vexed's {} cog. This is a reminder that you previously enabled "
    "telemetry and error reporting, which applies to all of my cogs, and this one is no "
    "different.\n\nI would like to emphasise again that a best effort it made to remove sensitive "
    "data. You can see <https://cogdocs.vexcodes.com/en/latest/telemetry.html> for more details "
    "and change your choice at any time with the `[p]vextelemetry` command, applying to all my "
    "cogs."
)

SENTRY_REMINDER_OFF = (
    "Hey there! You just installed Vexed's {} cog. This is a reminder that you previously chose "
    "not to enable telemetry and error reporting, which is also available in this cog. I hope you "
    "don't mind this reminder.\n\nI would like to emphasise again that a best effort it made to "
    "remove sensitive data. You can see <https://cogdocs.vexcodes.com/en/latest/telemetry.html> "
    "for more details and change your choice at any time with the `[p]vextelemetry` command, "
    "applying to all my cogs."
)

SENTRY_DSNS = {
    "wol": "https://ea2483bae296429797b23786fbf25980@o966432.ingest.sentry.io/5917446",
    "timechannel": "https://ae04709f0943421194b0d2c5f1467c85@o966432.ingest.sentry.io/5918790",
    "system": "https://0a9b0fa955ab4d2fb00b971ad823a3bf@o966432.ingest.sentry.io/5918773",
    "status": "https://f9eb2159800b4662b9dc266d7ee51c56@o966432.ingest.sentry.io/5918791",
    "stattrack": "https://dd7066711599488da627c8cc7de6ece3@o966432.ingest.sentry.io/5918793",
    "madtranslate": "https://405236d907214e6a9449e29ef1946535@o966432.ingest.sentry.io/5918774",
    "github": "https://9885bb05846f4adf966f746b0ebcc953@o966432.ingest.sentry.io/5918777",
    "ghissues": "https://7ecdcfcc80c04d08969b53c8e97df91c@o966432.ingest.sentry.io/5918779",
    "cmdlog": "https://4b39703d4d0041ceabc92bc554ddbc6e@o966432.ingest.sentry.io/5918794",
    "betteruptime": "https://5e84069469a24224ac03e290e51ea01e@o966432.ingest.sentry.io/5918797",
    "beautify": "https://52bcb80b8ecd485989ad105cdce1f1d4@o966432.ingest.sentry.io/5918798",
    "anotherpingcog": "https://8bef92be13f84d7dbdbb4e4ded63ad4c@o966432.ingest.sentry.io/5918803",
    "aliases": "https://0eda8fb326df45f58415975386a704c8@o966432.ingest.sentry.io/5918805",
}
