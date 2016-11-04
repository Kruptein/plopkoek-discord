"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging
import random
from collections import Counter
from datetime import datetime

from api.decorators import command
from api.gateway import Bot
from api.utils import get_value, set_value, get_logger
from api.web import Channel, Webhook, User

quote_url = u"https://cdn1.iconfinder.com/data/icons/anchor/128/quote.png"
webhook_id = get_value("quotebot", "webhook_id")
webhook_token = get_value("quotebot", "webhook_token")
general_channel_id = get_value("main", "general_channel_id")


def get_random_quote():
    """
    Return a random quote from the quote list.
    """
    quotes = get_value('quotebot', 'quotes')
    quotelist = []
    for quotee in quotes:
        for quote in quotes[quotee]:
            quotelist.append({"quote": quote['quote'], "quotee": quotee})
    return random.choice(quotelist)


def get_username(quotee):
    """
    Return the username of the given quotee.
    If quotee is a non formatted string, this function will simply return that string.
    If quotee is a <@ID> formatted string, ths function will retrieve the username for given user id.
    """
    if quotee.startswith("<@") and quotee.endswith(">"):
        try:
            return User.get_user(quotee[2:-1])['username']
        except KeyError:
            get_logger("QuoteBot").exception("Failed to get username for {}".format(quotee))
    return quotee


def post_message(channel_id, content):
    if channel_id == general_channel_id:
        Webhook.execute_content(webhook_id, webhook_token, content, "quotebot", avatar_url=quote_url)
    else:
        Channel.create_message(channel_id, content)


def post_quote(channel_id, quote, quotee):
    if channel_id == general_channel_id:
        avatar_url = quote_url
        if quotee.startswith("<@") and quotee.endswith(">"):
            user = User.get_user(quotee[2:-1])
            avatar_url = User.get_avatar_url(user)
            quotee = user['username']
        Webhook.execute_content(webhook_id, webhook_token, quote, quotee, avatar_url=avatar_url)
    else:
        Channel.create_message(channel_id, "{} - {}".format(quote, get_username(quotee)))


class QuoteBot(Bot):
    """
    A bot providing quotes which can be added, queried and more by users.
    Will post a random quote every 30 messages.
    Also provides a lenny gimmick.
    """

    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("quotebot", stream_log_level=stream_log_level, file_log_level=file_log_level)
        self.message_count = 0

    @command('add', 'append')
    def add_quote(self, event):
        """
        Add a quote to the database.
        This is triggered by a `!quotebot add <username> <quote>` command.
        """
        quotee = event.content.split(" ")[2]
        quote = ' '.join(event.content.split(" ")[3:])
        quotes = get_value('quotebot', 'quotes')
        quote_dict = {'quote': quote, 'added_by': event.author['username'], 'added_on': str(datetime.now())}
        quotes.setdefault(quotee, []).append(quote_dict)
        set_value('quotebot', 'quotes', quotes)
        post_message(channel_id=event.channel_id, content='Quote added!')

    @command('random')
    def send_random_quote(self, event):
        """
        Send a random quote.
        This is triggered by a `!quotebot random [username]` command.
        """
        components = event.content.split(" ")
        quotes = get_value('quotebot', 'quotes')
        try:
            # a username was provided
            if len(components) == 3:
                quotee = components[2]
                if quotee in quotes:
                    quote = random.choice([q['quote'] for q in quotes[quotee]])
                    post_quote(event.channel_id, quote, quotee)
                else:
                    msg = "BEEP BOOP, 404 {} not found!".format(quotee)
                    post_message(event.channel_id, msg)
            else:
                q = get_random_quote()
                post_quote(event.channel_id, q['quote'], q['quotee'])
        except IndexError:
            post_message(event.channel_id, "No quotes..")

    @command('list')
    def list_quotes(self, event):
        """
        List all quotes for a given user.
        This is triggered by a `!quotebot list <username>` command.
        """
        components = event.content.split(" ")
        quotes = get_value('quotebot', 'quotes')
        if len(components) != 3:
            msg = "Incorrect command usage.\nUse `!quotebot help list` for more information."
        elif components[2] in quotes.keys():
            msg = "{}'s quotes are: ".format(components[2])
            msg += " | ".join([q['quote'] for q in quotes[components[2]]])
        else:
            msg = "Could not find {} in the pokedex :(\nUse `!quotebot quotees` to list all users with a quote.".format(
                components[2])
        post_message(event.channel_id, msg)

    @command('quotees')
    def list_quotees(self, event):
        """
        List all users with a quote in the database.
        This is triggered by a `!quotebot quotees` command.
        """
        quotes = get_value('quotebot', 'quotes')
        if len(event.content.split(" ")) != 2:
            msg = "Incorrect command usage.\nUse `!quotebot help quotees` for more information."
        else:
            msg = " | ".join(sorted(quotes.keys()))
        post_message(event.channel_id, msg)

    @command('find')
    def find_quote(self, event):
        """
        Find quotes containing a given pattern.
        This is triggered by a `!quotebot find <username> <keyword>` command.
        """
        quotes = get_value('quotebot', 'quotes')
        components = event.content.split(" ")
        quotee = components[2] if len(components) > 1 else ""
        if len(components) < 4:
            msg = "Incorrect command usage.\nUse `!quotebot help find` for more information."
        elif quotee not in quotes:
            msg = "Could not find {} in the pokedex :c".format(quotee)
        else:
            sentence = " ".join(components[3:])
            found = []
            for quote in quotes[quotee]:
                if sentence.lower() in quote['quote'].lower():
                    found.append(quote['quote'])
            if len(found) == 0:
                msg = "Could not find {} saying {} in the pokedex :c".format(quotee, sentence)
            else:
                if len(found) == 1:
                    Channel.create_message(event.channel_id, "{} - {}".format(found[0], quotee))
                    return
                msg = "Found these quotes for {} containing {}: ".format(quotee, sentence)
                msg += " | ".join(found)
        post_message(event.channel_id, msg)

    @command('stats')
    def show_stats(self, event):
        """
        Display some stats, i.e. show the total quote count and a top 3 of users with most quotes
        """
        quotes = get_value("quotebot", "quotes")
        counter = Counter({quotee: len(quotes[quotee]) for quotee in quotes})
        post_message(event.channel_id, "Total quote count: {}".format(sum(counter.values())))
        post_message(event.channel_id, "Quote top3: {}".format(
            " ".join("{}({})".format(get_username(quotee), num) for quotee, num in counter.most_common(3))))

    def execute_event(self, event):
        super().execute_event(event)
        if event.of_t("MESSAGE_CREATE"):
            self.message_count += 1
            if self.message_count == 30:
                q = get_random_quote()
                post_quote(event.channel_id, q["quote"], q["quotee"])
                self.message_count = 0


if __name__ == "__main__":
    QuoteBot().run(False)
