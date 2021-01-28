import functools

from discord.ext import commands
from discord.ext.commands.context import Context

from .cog import PlopCog


def noop():
    pass


def command(name: str):
    def func_wrapper(func):
        @functools.wraps(func)
        async def wrapper(cls: PlopCog, ctx: Context, *args, **kwargs):
            if cls.prefixes:
                if not any(
                    ctx.message.content[1:].startswith(prefix)
                    for prefix in cls.prefixes
                ):
                    return noop()
            return await func(cls, ctx, *args, **kwargs)

        return commands.command(name=name)(wrapper)

    return func_wrapper