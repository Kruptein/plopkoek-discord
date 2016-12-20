"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging

from collections import Counter
from datetime import datetime

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

            self.add_plopkoek(user.strip('<@!>'), donator=event.author['id'], message_id=event.id)
                
    def donate_plopkoek_reaction(self, event):
        if not event.emoji['id']:
            return
        if event.emoji['id'] in plopkoek_emote:
            message = Channel.get_message(event.channel_id, event.message_id)
            receiver = message['author']['id']
            donator = event.user_id

            self.add_plopkoek(receiver, donator, event.message_id)

    def remove_plopkoek_reaction(self, event):
        if not event.emoji['id']:
            return
        if event.emoji['id'] in plopkoek_emote:
            message = Channel.get_message(event.channel_id, event.message_id)
            receiver = message['author']['id']
            donator = event.user_id

            self.remove_plopkoek(receiver, donator, event.message_id)

    def get_income(self, user_id):
        today = datetime.utcnow()
        return sum(1 for day_data in self.get_year_data().get(str(today.month), {}).values() for d in day_data if d['to'] == user_id)

    def get_year_data(self):
        today = datetime.utcnow()
        
        try:
            year_data = get_value("plopkoekbot", str(today.year))
        except KeyError:
            year_data = {}

        return year_data

    def get_day_data(self):
        today = datetime.utcnow()
        year_data = self.get_year_data()
        return year_data.get(str(today.month), {}).get(str(today.day), [])

    def get_donations_left(self, donator):
        return 5 - sum(1 for data in self.get_day_data() if data['from'] == donator)

    def can_donate(self, donator, receiver):
        if donator == receiver:
            return False

        return self.get_donations_left(donator) > 0 

        #day_data = self.get_day_data()
        #donator_data = [data for data in self.get_day_data() if data['from'] == donator]
        #if len(donator_data) > 5:
        #    return False
        #return Counter(data["to"] for data in donator_data)[receiver] <= 4

    def add_plopkoek(self, user_id, donator, message_id):
        if not self.can_donate(donator=donator, receiver=user_id):
            return
        year_data = self.get_year_data()
        today = datetime.utcnow()
        
        if str(today.month) not in year_data:
            year_data[str(today.month)] = {}
        if str(today.day) not in year_data[str(today.month)]:
            year_data[str(today.month)][str(today.day)] = []

        year_data[str(today.month)][str(today.day)].append({
            'from': donator,
            'to': user_id,
            'message_id': message_id,
        })

        set_value("plopkoekbot", str(today.year), year_data)

        dm = User.create_dm(recipient_id=user_id)
        content = 'Je hebt een plopkoek van <@{}> gekregen!  Je hebt er nu {} deze maand verzameld.'.format(donator, self.get_income(user_id))
        Channel.create_message(channel_id=dm.json()['id'], content=content)

        dm = User.create_dm(recipient_id=donator)
        content = 'Je hebt een plopkoek aan <@{}> gegeven.  Je kan er vandaag nog {} uitgeven.'.format(user_id, self.get_donations_left(donator))
        Channel.create_message(channel_id=dm.json()['id'], content=content)

    def remove_plopkoek(self, receiver, donator, message_id):
        year_data = self.get_year_data()

        found = False

        if receiver == donator:
            return

        for month in year_data:
            for day in year_data[month]:
                for data in year_data[month][day]:
                    if data['from'] == donator and data['to'] == receiver and data['message_id'] == message_id:

                        year_data[month][day].remove(data)
                        found = True

        if found:
            set_value("plopkoekbot", str(datetime.utcnow().year), year_data)

            dm = User.create_dm(recipient_id=receiver)
            content = '<@{}> heeft een plopkoek afgepakt :O  Je hebt er nu nog {} deze maand over.'.format(donator, self.get_income(receiver))
            Channel.create_message(channel_id=dm.json()['id'], content=content)

            dm = User.create_dm(recipient_id=donator)
            content = 'Je hebt een plopkoek die je aan <@{}> hebt gegeven teruggenomen.  Je kan er vandaag nog {} uitgeven.'.format(receiver, self.get_donations_left(donator))
            Channel.create_message(channel_id=dm.json()['id'], content=content)

    def execute_event(self, event):
        super().execute_event(event)
        if event.of_t('MESSAGE_CREATE'):
            self.donate_plopkoek(event)
        elif event.of_t('MESSAGE_REACTION_ADD'):
            self.donate_plopkoek_reaction(event)
        elif event.of_t('MESSAGE_REACTION_REMOVE'):
            self.remove_plopkoek_reaction(event)
        self.logger.critical(event._t)

