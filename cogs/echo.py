"""
A dummy bot that echoes.
Good test subject.
"""

from api.cog import PlopCog
from discord.channel import TextChannel
from discord.ext.commands.bot import Bot
from discord.ext.commands.cog import Cog
from discord.message import Message


class EchoCog(PlopCog):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id == self.bot.user.id:
            return

        channel: TextChannel = message.channel
        await channel.send(message.content)


def setup(bot: Bot):
    bot.add_cog(EchoCog(bot))