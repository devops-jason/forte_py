import nats
import socket
import time
import asyncio
from forte.message import ForteMessage
import uuid

class ForteClient():
    def __init__(self):
        self.nats_address = '127.0.0.1'
        self._nc = None
        self._subs = {}
        self.msg_timeout = 2.0

    def set_msg_timeout(self, timeout=2.0):
        if timeout >= 0.1:
            self.msg_timeout = timeout
        else:
            self.msg_timeout = 2.0

    async def connect(self, nats_address = None):
        if nats_address:
            self.nats_address = nats_address
        else:
            print("No nat servers provided defaulting to localhost.")

        self._nc = await nats.connect(self.nats_address)
        if self._nc.is_connected:
            print("Connected to nats_server " + nats_address + ".")

    async def subscribe(self, subject = 'forte.*'):
        self._subs[subject] = await self._nc.subscribe(subject)

    async def get_msg(self, subject = 'forte.*'):
        try:
            msg = await self._subs[subject].next_msg(timeout=self.msg_timeout)
        except:
            msg = None

        return msg
    
    async def request(self):
        if self._nc.is_closed:
            print('Must connect to nats-server first.')
            exit(1)

        forte_inbox = self._nc.new_inbox()

        await self.subscribe(forte_inbox)

        forte_msg = ForteMessage()

        forte_msg.set_forte_command('ping')
        await self._nc.publish('forte.ping',forte_msg.dump_yaml().encode(), reply=forte_inbox)
        await self._nc.flush()
        print('Published message to subject forte.ping reply inbox is' + forte_inbox + '.')

        self.set_msg_timeout(2.5)
        while forte_reply_msg := await self.get_msg(forte_inbox):
            reply_msg = ForteMessage()
            try:
                reply_msg.load_yaml(forte_reply_msg.data.decode())
            except:
                print("Unable to read data from message in yaml.")
                next

            print(reply_msg.dump_yaml())

        forte_msg.set_forte_command('ps')
        await self._nc.publish('forte.command',forte_msg.dump_yaml().encode(), reply=forte_inbox)
        await self._nc.flush()

        print('Published message to subject forte.ping reply inbox is' + forte_inbox + '.')

        self.set_msg_timeout(2.5)
        while forte_reply_msg := await self.get_msg(forte_inbox):
            reply_msg = ForteMessage()
            try:
                reply_msg.load_yaml(forte_reply_msg.data.decode())
            except:
                print("Unable to read data from message in yaml.")
                next

            print(reply_msg.dump_yaml())

        await self._nc.close()