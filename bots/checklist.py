"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging

from tabulate import tabulate

from api.decorators import command
from api.gateway import Bot
from api.utils import get_value, set_value, pop_value, append_value, update_value
from api.web import Channel, User


def get_username(name):
    try:
        return User.get_user(name.strip('<@!>'))['username']
    except:
        return name


class ChecklistBot(Bot):
    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("checklist", stream_log_level=stream_log_level, file_log_level=file_log_level)

    @command('additem')
    def add_item(self, event, args):
        item = " ".join(event.content.strip().split(" ")[2:])
        append_value("checklist", "items", {"item": item, "users": [], "status":"NOT DONE"})
        Channel.create_message(channel_id=event.channel_id, content="Item #{}: {} added to the list!".format(self.get_item_index(item), item))

    @command('adduser', fmt="item user")
    def add_user(self, event, args):
        items = get_value("checklist", "items")
        try:
            item = int(args.item.strip('#'))
        except ValueError:
            Channel.create_message(channel_id=event.channel_id, content="{} is not a number!".format(args.item))
            return
        if 0 <= item < len(items):
            items[item]["users"].append(args.user)
            set_value("checklist", "items", items)
            Channel.create_message(channel_id=event.channel_id, content="Added {} to item #{}".format(args.user, item))
        else:
            Channel.create_message(channel_id=event.channel_id, content="That's not a valid item index")

    @command('show')
    def show(self, event, args):
        items = get_value("checklist", "items")
        data = []
        for i, item in enumerate(items):
            data.append([i, item['item'], item['status'], ",".join(get_username(name) for name in item['users'])])
        while len(data) > 0:
            message = '```' + tabulate(data[:10], headers=['#', 'item', 'status', 'relevant users'], tablefmt='fancy_grid') + '```'
            Channel.create_message(event.channel_id, message)
            data = data[10:]

    @command('update', fmt="item status>")
    def update(self, event, args):
        items = get_value("checklist", "items")
        try:
            item = int(args.item.strip('#'))
        except ValueError:
            Channel.create_message(channel_id=event.channel_id, content="{} is not a number!".format(args.item))
            return
        if 0 <= item <= len(items):
            items[item]['status'] = args.status
            set_value("checklist", "items", items)
            Channel.create_message(channel_id=event.channel_id, content="Updated status of item #{}".format(item))
        else:
            Channel.create_message(channel_id=event.channel_id, content="That's not a valid item index")

    def get_item_index(self, item):
        for i, obj in enumerate(get_value("checklist", "items")):
            if obj["item"] == item:
                return i
        return -1
