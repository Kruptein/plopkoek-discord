"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging
import sched
import threading
from datetime import datetime

from api.decorators import command
from api.gateway import Bot
from api.utils import get_value, set_value, get_logger
from api.web import Channel, Webhook, User

general_channel_id = get_value("main", "general_channel_id")


class VoteBot(Bot):
    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("vote", stream_log_level=stream_log_level, file_log_level=file_log_level)
        self.message_count = 0
        self.scheduler = sched.scheduler()

    @command('start')
    def add_vote(self, event):
        content = event.content.split(" ")
        subject = content[2]
        timer = 60
        if len(content) == 4:
            try:
                timer = int(content[3])
            except ValueError:
                pass
        vote_dict = {'subject': subject, 'added_by': event.author['username'], 'added_on': str(datetime.now()), 'timer': timer, 'channel_id': event.channel_id}
        set_value('votebot', subject, vote_dict)
        self.scheduler.enter(timer, 1, self.finalize_vote, argument=(subject,))
        t = threading.Thread(target=self.scheduler.run)
        t.start()
        Channel.create_message(channel_id=event.channel_id, content='Vote {} started, ends in {} seconds'.format(subject, timer))

    def finalize_vote(self, subject):
        vote = get_value("votebot", subject)
        Channel.create_message(vote['channel_id'], "Vote {} ended".format(subject))
                    
if __name__ == "__main__":
    VoteBot().run(False)
