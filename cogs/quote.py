"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Union

from discord import Webhook, RequestsWebhookAdapter
from discord.channel import TextChannel
from discord.ext.commands.cog import Cog
from discord.member import Member
from discord.message import Message
from discord.user import User
from discord.ext.commands.bot import Bot
from discord.ext.commands.context import Context

from api.cog import PlopCog
from api.decorators import command
from api.utils import get_value, set_value


quote_url = "https://cdn1.iconfinder.com/data/icons/anchor/128/quote.png"
webhook_id = get_value("quotebot", "webhook_id")
webhook_token = get_value("quotebot", "webhook_token")
general_channel_id = get_value("main", "general_channel_id")


def get_random_quote():
    """
    Return a random quote from the quote list.
    """
    quotelist = []
    for quotee, quotes in get_value("quotebot", "quotes").items():
        for quote in quotes:
            quotelist.append({"quote": quote["quote"], "quotee": quotee})
    return random.choice(quotelist)


async def post_message(channel: TextChannel, content: str):
    if channel.id == general_channel_id:
        webhook = Webhook.partial(
            webhook_id, webhook_token, adapter=RequestsWebhookAdapter()
        )
        webhook.send(content, username="quotebot", avatar_url=quote_url)
    else:
        await channel.send(content)


async def post_quote(channel: TextChannel, quote: str, user: Union[Member, User, str]):
    tts = False
    if quote.startswith("/tts"):
        quote = quote[5:]
        tts = True

    user_name = user
    avatar_url = quote_url
    if isinstance(user, Member) or isinstance(user, User):
        avatar_url = user.avatar_url
        user_name = user.display_name

    if channel.id == general_channel_id:
        webhook = Webhook.partial(
            webhook_id, webhook_token, adapter=RequestsWebhookAdapter()
        )
        webhook.send(quote, username=user_name, avatar_url=avatar_url, tts=tts)
    else:
        await channel.send(f"{quote} - {user_name}", tts=tts)


class QuoteCog(PlopCog):
    """
    A bot providing quotes which can be added, queried and more by users.
    Will post a random quote every 30 messages.
    Also provides a lenny gimmick.
    """

    def __init__(self, bot: Bot):
        super().__init__(bot, ("qb", "quotebot"))
        self.message_count: Dict[str, int] = defaultdict(int)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id == self.bot.user.id:
            return

        self.message_count[message.channel.id] += 1
        if self.message_count[message.channel.id] == 31:
            q = get_random_quote()
            user = await self.get_user(q["quotee"])
            await post_quote(message.channel, q["quote"], user)
            self.message_count[message.channel.id] = 0

    @command("add")
    async def add_quote(
        self, ctx: Context, user: Union[Member, User, str], *quote: str
    ):
        """
        Add a quote to the database.
        This is triggered by a `!quotebot add <username> <quote>` command.
        """
        user_id = user
        if isinstance(user, User) or isinstance(user, Member):
            user_id = str(user.id)

        quotes = get_value("quotebot", "quotes")
        quote_dict = {
            "quote": " ".join(quote),
            "added_by": ctx.author.id,
            "added_on": str(datetime.now()),
        }
        quotes.setdefault(user_id, []).append(quote_dict)
        set_value("quotebot", "quotes", quotes)
        await post_message(ctx.channel, content="Quote added!")

    @command("random")
    async def send_random_quote(
        self, ctx: Context, user: Optional[Union[Member, User, str]]
    ):
        """
        Send a "random" quote.
        This is triggered by a `!quotebot random [username]` command.
        """
        user_id = user
        user_name = user
        if isinstance(user, Member) or isinstance(user, User):
            user_id = str(user.id)
            user_name = user.display_name

        quotes = get_value("quotebot", "quotes")
        try:
            if user_id:
                if user_id in quotes:
                    quote = random.choice([q["quote"] for q in quotes[user_id]])
                    await post_quote(ctx.channel, quote, user)
                else:
                    msg = "BEEP BOOP, 404 {} not found!".format(user_name)
                    await post_message(ctx.channel, msg)
            else:
                q = get_random_quote()
                user = await self.get_user(q["quotee"])
                await post_quote(ctx.channel, q["quote"], user)
        except IndexError:
            post_message(ctx.channel, "No quotes..")

    @command("list")
    async def list_quotes(self, ctx: Context, user: Union[Member, User, str]):
        """
        List all quotes for a given user.
        This is triggered by a `!quotebot list <username>` command.
        """
        user_id = user
        user_name = user
        if isinstance(user, Member) or isinstance(user, User):
            user_id = str(user.id)
            user_name = user.display_name

        quotes = get_value("quotebot", "quotes")

        if user_id in quotes:
            msg = f"{user_name}'s quotes are: "
            msg += " | ".join([q["quote"] for q in quotes[user_id]])
        else:
            msg = f"Could not find {user_name} :(\nUse `!quotebot quotees` to list all users with a quote)"
        await post_message(ctx.channel, msg)

    @command("quotees")
    async def list_quotees(self, ctx: Context):
        """
        List all users with a quote in the database.
        This is triggered by a `!quotebot quotees` command.
        """
        quotes = get_value("quotebot", "quotes")
        names = [await self.get_user_name(user) for user in quotes.keys()]
        msg = " | ".join(sorted(names))
        await post_message(ctx.channel, msg)

    @command("find")
    async def find_quote(
        self, ctx: Context, user: Union[Member, User, str], *keywords: str
    ):
        """
        Find quotes containing a given pattern.
        This is triggered by a `!quotebot find <username> <keyword>` command.
        Pass * as the username to search through all quotes.
        """
        search_all_users = user == "*"
        user_id = user
        user_name = user
        if isinstance(user, Member) or isinstance(user, User):
            user_id = str(user.id)
            user_name = user.display_name

        all_quotes = get_value("quotebot", "quotes")

        messages: List[str] = []

        if not search_all_users and user_id not in all_quotes:
            messages.append(f"Could not find {user_name}")
        else:
            sentence = " ".join(keywords)
            found: Dict[str, List[str]] = defaultdict(list)
            for quotee, quotes in all_quotes.items():
                if not search_all_users and quotee != user_id:
                    continue
                for quote in quotes:
                    if sentence.lower() in quote["quote"].lower():
                        found[quotee].append(quote["quote"])
            if len(found) == 0:
                if search_all_users:
                    messages.append(f"Could not find any occurence of '{sentence}'")
                else:
                    messages.append(f"Could not find {user_name} saying '{sentence}'")
            else:
                found_length = sum(len(v) for v in found.values())
                if found_length == 1:
                    user = next(iter(found.keys()))
                    await post_quote(
                        ctx.channel,
                        next(iter(found.values()))[0],
                        await self.get_user(user) or user,
                    )
                    return
                elif found_length > 25:
                    messages.append(
                        f"Found more than 25 quotes matching '{sentence}'. Skipping output."
                    )
                else:
                    messages.append(f"Found these quotes containing '{sentence}':\n")
                    for quotee, quotes in found.items():
                        user_name = await self.get_user_name(quotee)
                        messages.append(f"{user_name}: {' | '.join(quotes)}\n")
        for message in messages:
            await post_message(ctx.channel, message)

    @command("stats")
    async def show_stats(self, ctx: Context):
        """
        Show the total quote count and a top 5 of users with most quotes
        """
        quotes = get_value("quotebot", "quotes")
        counter = Counter({quotee: len(quotes[quotee]) for quotee in quotes})
        await post_message(ctx.channel, f"Total quote count: {sum(counter.values())}")
        msg = "Quote top 5:\n"
        for quotee, num in counter.most_common(5):
            msg += f"    {num}: {await self.get_user_name(quotee)}\n"
        await post_message(ctx.channel, msg)


def setup(bot: Bot):
    bot.add_cog(QuoteCog(bot))
