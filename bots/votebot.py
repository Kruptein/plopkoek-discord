"""
Provides a quotebot allowing users to add and traverse quotes.
"""

import logging
import sched
import threading
from datetime import datetime, timedelta

from api.decorators import command
from api.gateway import Bot
from api.utils import get_value, set_value, pop_value, append_value, update_value
from api.web import Channel


class VoteBot(Bot):
    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("vote", stream_log_level=stream_log_level, file_log_level=file_log_level)
        self.scheduler = sched.scheduler()

        self.start_timers()

    def start_timers(self):
        votes = get_value("votebot", "active")
        for vote in votes:
            v = votes[vote]
            added = datetime.strptime(v['added_on'], "%Y-%m-%d %H:%M:%S.%f")
            timeleft = (added + timedelta(0, v['timer']) - datetime.now()).total_seconds()
            if timeleft <= 0:
                self.finalize_vote(vote)
            else:
                self.scheduler.enter(timeleft, 1, self.finalize_vote, argument=(vote,))
        t = threading.Thread(target=self.scheduler.run, daemon=True)
        t.start()

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

        vote_dict = {'subject': subject, 'added_by': event.author['username'], 'added_on': str(datetime.now()),
                     'timer': timer, 'channel_id': event.channel_id, 'votes': {}}

        update_value('votebot', 'active', subject, vote_dict)

        self.scheduler.enter(timer, 1, self.finalize_vote, argument=(subject,))
        t = threading.Thread(target=self.scheduler.run, daemon=True)
        t.start()
        Channel.create_message(channel_id=event.channel_id,
                               content='Vote {} started, ends in {} seconds'.format(subject, timer))

    @command("*")
    def vote(self, event):
        pass

    def finalize_vote(self, subject):
        vote = pop_value('votebot', 'active', subject)
        append_value('votebot', 'history', vote)
        Channel.create_message(vote['channel_id'], "Vote {} ended".format(subject))
