from typing import Optional
from discord.errors import NotFound
from discord.ext.commands.bot import Bot
from discord.ext.commands.cog import Cog
from discord.user import User


class PlopCog(Cog):
    def __init__(self, bot: Bot, prefixes: Optional[str] = None) -> None:
        self.bot = bot
        self.prefixes = prefixes

    @Cog.listener()
    async def on_ready(self):
        print(f"Loaded cog {self.__class__.__name__}")

    async def get_user(self, user_target: str) -> Optional[User]:
        """
        Attempts to convert a potential user_id to a User.
        If this fails returns None
        """
        if len(user_target) >= 17:
            try:
                user_id = int(user_target)
            except ValueError:
                pass
            else:
                user: User = self.bot.get_user(user_id)
                if user is None:
                    try:
                        user = await self.bot.fetch_user(user_id)
                    except NotFound:
                        return None
                return user
        return None

    async def get_user_name(self, user_target: str) -> str:
        """
        Attempts to convert a potential user id string to a username.
        If the string is not 18 chars long or not parseable as an int,
        the original string will be returned.

        This will first attempt to use the local user cache before calling the API.
        """
        user = await self.get_user(user_target=user_target)
        if user is None:
            return user_target
        return user.display_name
