"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging

from api import cache
from api.decorators import command
from api.gateway import Bot
from api.utils import get_value, set_value, get_logger
from api.web import Channel, Webhook, User

general_channel_id = get_value("main", "general_channel_id")
plopkoek_emote = "<:plop:236155120067411968>"
#plopkoek_emote = "<:lock:259731815651082251>"


class PlopkoekBot(Bot):

    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("plopkoekbot", stream_log_level=stream_log_level, file_log_level=file_log_level)

    def donate_plopkoek(self, event):
        if plopkoek_emote in event.content and len(event.content.strip().split(" ")) == 2:
            user = event.content.replace(plopkoek_emote, '').strip()
            if self.can_donate(event.author['id']):
                new_income = self.add_plopkoek(user.strip('<@!>'), donator=event.author['id'])
                dm = User.create_dm(recipient_id=user.strip('<@!>'))
                Channel.create_message(channel_id=dm.json()['id'], content='Je hebt een plopkoek van <@{}> gekregen!  Je hebt er nu {} deze maand verzameld.'.format(event.author['id'], new_income))
    
    def can_donate(self, user_id):
        plopkoeks = get_value("plopkoekbot", "plopkoeks")
        if user_id not in plopkoeks:
            return True
        return plopkoeks[user_id]['day_limit'] > 0

    def add_plopkoek(self, user_id, donator):
        plopkoeks = get_value("plopkoekbot", "plopkoeks")
        
        empty_data = {'month_income': 0, 'day_limit': 5, 'day_given_to': [], 'total': 0}

        if user_id not in plopkoeks:
            plopkoeks[user_id] = empty_data
        if donator not in plopkoeks:
            plopkoeks[donator] = empty_data
        plopkoeks[user_id]['month_income'] += 1
        plopkoeks[donator]['day_limit'] -= 1

        set_value("plopkoekbot", "plopkoeks", plopkoeks)

        return plopkoeks[user_id]['month_income']

    def execute_event(self, event):
        super().execute_event(event)
        if event.of_t('MESSAGE_CREATE'):
            self.donate_plopkoek(event)

