"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging
import random
from datetime import datetime

from api.decorators import command
from api.gateway import Bot
from api.web import Channel
from utils import get_value, set_value


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
        Channel.create_message(channel_id=event.channel_id, content='Quote added!')

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
                    Channel.create_message(event.channel_id, "{} - {}".format(quote, quotee))
                else:
                    msg = "BEEP BOOP, 404 {} not found!".format(quotee)
                    Channel.create_message(event.channel_id, msg)
            else:
                q = get_random_quote()
                Channel.create_message(event.channel_id, "{} - {}".format(q["quote"], q["quotee"]))
        except IndexError:
            Channel.create_message(event.channel_id, "No quotes..")

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
        Channel.create_message(event.channel_id, msg)

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
        Channel.create_message(event.channel_id, msg)

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
        Channel.create_message(event.channel_id, msg)

    def execute_event(self, event):
        super().execute_event(event)
        if event.of_t("MESSAGE_CREATE"):
            self.message_count += 1
            if self.message_count == 30:
                q = get_random_quote()
                Channel.create_message(event.channel_id, "{} - {}".format(q["quote"], q["quotee"]))
                self.message_count = 0

if __name__ == "__main__":
    QuoteBot().run(False)
