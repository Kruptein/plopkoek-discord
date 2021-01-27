import sys
from typing import List

from discord.ext.commands import Bot

from api.utils import get_value

prefixes = ("!quotebot ", "!plopkoekbot ", "!qb ", "!pk ")
if get_value("main", "test_env"):
    prefixes = tuple(f"~{prefix[1:]}" for prefix in prefixes)


def start_cogs(cogs: List[str]):
    bot = Bot(command_prefix=prefixes)

    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")

    bot.run(get_value("main", "discord_token"))


if __name__ == "__main__":
    start_cogs(cogs=sys.argv[1:])
