"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import string
from operator import itemgetter
from typing import Optional, Union
from discord.embeds import Embed

from discord.ext.commands import command
from discord.ext.commands.bot import Bot
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.member import Member
from discord.message import Message
from discord.raw_models import RawReactionActionEvent
from discord.user import User
from tabulate import tabulate

from api.cog import PlopCog
from api.utils import get_value

from .db import (
    delete_plopkoek,
    get_alltime_ranking,
    get_donations_left,
    get_month_ranking,
    get_total_income,
    has_donated_plopkoek,
    init_db,
    get_income,
    insert_plopkoek,
)

general_channel_id = get_value("main", "general_channel_id")
plopkoek_emote = get_value("plopkoek", "emote")
bot_display_name = get_value("plopkoek", "display_name")


def can_donate(donator, receiver):
    if donator == receiver:
        return False

    return get_donations_left(donator) > 0


def filter_ascii_only(data):
    return [
        [d[0], d[1], "".join([c for c in d[2] if c in string.printable])] for d in data
    ]


class PlopkoekCog(PlopCog):
    def __init__(self, bot: Bot):
        super().__init__(bot)
        init_db()

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id == self.bot.user.id:
            return

        if (
            plopkoek_emote in message.content
            and len(message.content.strip().split(" ")) == 2
        ):
            user = message.content.replace(plopkoek_emote, "").strip()
            if user.startswith("<@") and user.endswith(">"):
                donator = message.author
                receiver = await self.get_user(user.strip("<@!>"))
                if receiver is None:
                    await donator.send(
                        "Kon geen plopkoek geven aan onbekende gebruiker. Geen zorgen de plopkoek is veilig terug in je kluis gestoken."
                    )
                else:
                    await self.add_plopkoek(receiver, donator, message)

    @Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        if str(reaction.emoji.id) in plopkoek_emote:
            channel = await self.bot.fetch_channel(reaction.channel_id)
            message: Message = await channel.fetch_message(reaction.message_id)
            receiver = message.author
            donator = reaction.member

            bot_id = get_value("main", "bot_id")

            if receiver.id == bot_id or message.webhook_id == get_value(
                "quotebot", "webhook_id"
            ):
                quote_content = message.content
                if receiver.display_name == bot_display_name and " -" in quote_content:
                    quote_content = "-".join(quote_content.split(" -")[:-1])
                found = False
                for quotee, quotes in get_value("quotebot", "quotes").items():
                    for quote in quotes:
                        if quote["quote"] == quote_content:
                            receiver = await self.get_user(quotee) or receiver
                            found = True
                if not found:
                    receiver = await self.get_user(str(bot_id))

            await self.add_plopkoek(receiver, donator, message)

    @Cog.listener()
    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent):
        if str(reaction.emoji.id) in plopkoek_emote:
            channel = await self.bot.fetch_channel(reaction.channel_id)
            message: Message = await channel.fetch_message(reaction.message_id)
            receiver = message.author
            donator = await self.get_user(str(reaction.user_id))

            bot_id = get_value("main", "bot_id")

            if receiver.id == bot_id or message.webhook_id == get_value(
                "quotebot", "webhook_id"
            ):
                quote_content = message.content
                if receiver.display_name == bot_display_name and " -" in quote_content:
                    quote_content = "-".join(quote_content.split(" -")[:-1])
                found = False
                for quotee, quotes in get_value("quotebot", "quotes").items():
                    for quote in quotes:
                        if quote["quote"] == quote_content:
                            receiver = await self.get_user(quotee) or receiver
                            found = True
                if not found:
                    receiver = await self.get_user(str(bot_id))

            await self.remove_plopkoek(receiver, donator, message)

    @command(name="total")
    async def show_total(self, ctx: Context, user: Optional[Union[Member, User]]):
        """
        Show the total number of plopkoeks acquired this month.
        If no user is provided the message sender is used instead.
        """
        if user is None:
            user = ctx.author
        user_id = user
        user_name = user
        if isinstance(user, Member) or isinstance(user, User):
            user_id = str(user.id)
            user_name = user.display_name

        message = f"{user_name} has so far earned {get_income(user_id, '%Y-%m')} plopkoeks this month."
        await ctx.channel.send(message)

    @command(name="grandtotal")
    async def show_grandtotal(self, ctx: Context, user: Optional[Union[Member, User]]):
        """
        Show the total number of plopkoeks acquired all time.
        If no user is provided the message sender is used instead.
        """
        if user is None:
            user = ctx.author
        user_id = user
        user_name = user
        if isinstance(user, Member) or isinstance(user, User):
            user_id = str(user.id)
            user_name = user.display_name

        message = f"{user_name} has so far earned {get_total_income(user_id)} plopkoeks in total!."
        await ctx.channel.send(message)

    @command(name="leaders")
    async def show_leaders(
        self, ctx: Context, month: Optional[str], year: Optional[str]
    ):
        """
        Get the leaderboard for the current or chosen month.
        """
        data = await self.process_ranking_data(*get_month_ranking(month, year))
        if not data:
            await ctx.channel.send("No data for the given period :(")
        while data:
            table_data = filter_ascii_only(data[:10])
            message = tabulate(
                table_data,
                headers=["received", "donated", "user"],
                tablefmt="fancy_grid",
            )
            await ctx.channel.send(f"```{message}```")
            data = data[10:]

    @command(name="grandleaders")
    async def show_grandleaders(self, ctx: Context):
        """
        Get the all-time leaderboard.
        """
        data = await self.process_ranking_data(*get_alltime_ranking())
        if not data:
            await ctx.channel.send("No data for the given period :(")
        while data:
            table_data = filter_ascii_only(data[:10])
            message = tabulate(
                table_data,
                headers=["received", "donated", "user"],
                tablefmt="fancy_grid",
            )
            await ctx.channel.send(f"```{message}```")
            data = data[10:]

    async def add_plopkoek(
        self,
        receiver: User,
        donator: User,
        message: Message,
    ):
        if not can_donate(donator.id, receiver.id):
            return

        insert_plopkoek(donator.id, receiver.id, message.channel.id, message.id)

        embed = Embed(description=message.content)
        embed.set_author(name=receiver.display_name, icon_url=receiver.avatar_url)

        try:
            content = f"Je hebt een plopkoek van {donator.display_name} gekregen!  Je hebt er nu {get_income(receiver.id, '%Y-%m')} deze maand verzameld. Goe bezig!"
            await receiver.send(content, embed=embed)
        except AttributeError:
            pass

        donations_left = get_donations_left(donator.id)
        if donations_left == 0:
            content = f"Je hebt een plopkoek aan {receiver.display_name} gegeven.  Da was uwe laatste plopkoek van vandaag, geefde gij ook zo gemakkelijk geld uit?"
        else:
            content = f"Je hebt een plopkoek aan {receiver.display_name} gegeven.  Je kan er vandaag nog {donations_left} uitgeven. Spenden die handel!"
        await donator.send(content, embed=embed)

    async def remove_plopkoek(
        self,
        receiver: User,
        donator: User,
        message: Message,
    ):
        if has_donated_plopkoek(
            donator.id, receiver.id, message.channel.id, message.id
        ):
            delete_plopkoek(donator.id, receiver.id, message.channel.id, message.id)

            try:
                content = f"{donator.display_name} heeft een plopkoek afgepakt :O  Je hebt er nu nog {get_income(receiver.id, '%Y-%m')} deze maand over."
                await receiver.send(content=content)
            except AttributeError:
                pass

            content = (
                f"Je hebt een plopkoek die je aan {receiver.display_name} hebt gegeven teruggenomen. (Gij se evil bastard!) "
                f"Je kan er vandaag nog {get_donations_left(donator.id)} uitgeven."
            )
            await donator.send(content=content)

    async def process_ranking_data(self, received_data, donated_data):
        dict_data = {}
        for row in received_data:
            uid = row["user_to_id"]
            username = await self.get_user_name(uid)
            dict_data[uid] = {
                "received": row["received"],
                "user": username,
                "donated": 0,
            }
        for row in donated_data:
            uid = row["user_from_id"]
            if uid not in dict_data:
                username = await self.get_user_name(uid)
                dict_data[uid] = {"user": username, "received": 0}
            dict_data[uid]["donated"] = row["donated"]
        list_data = []
        for dd in sorted(
            list(dict_data.values()), key=itemgetter("received"), reverse=True
        ):
            list_data.append([dd["received"], dd["donated"], dd["user"]])
        return list_data


def setup(bot: Bot):
    bot.add_cog(PlopkoekCog(bot))
