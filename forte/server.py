import nats
import socket
import time
import asyncio
from forte.message import ForteMessage
import subprocess
import os

class ForteServer():
    def __init__(self):
        self.nats_address = '127.0.0.1'
        self._nc = None
        self._subs = {}

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
            msg = await self._subs[subject].next_msg(timeout=1.0)
        except:
            msg = None

        return msg
        
    async def run(self):
        if self._nc.is_closed:
            print('Must connect to nats-server first.')
            exit(1)
        
        await self.subscribe('forte.*')
        print('Subscribing to forte.*')

        while True:
            msg = await self.get_msg('forte.*')
        
            forte_msg = ForteMessage()
            forte_reply = ForteMessage()

            if msg != None:
                print('Subject:', msg.subject)
                print('Reply: ', msg.reply)
                print('Data: ', str(msg.data.decode()))
                print('Headers: ', msg.header)

                try:
                    forte_msg.load_yaml(msg.data.decode())
                except:
                    print("Unable to load message to ForteMessage format.")
                    next
                
                if msg.subject == 'forte.ping':
                    if forte_msg.get_forte_command() == 'ping':
                        print('responding to ping')
                        forte_reply.set_reply_uuid(forte_msg.get_forte_uuid())
                        forte_reply.set_reply_data(socket.gethostname() + ': pong')
                        await self._nc.publish(msg.reply, forte_reply.dump_yaml().encode())
                        print('published pong response')

                if msg.subject == 'forte.command':
                    if forte_msg.get_forte_command() == 'ps':
                        print('responding to ps command.')
                        ps = subprocess.check_output('ps -ef', shell=True)
                        forte_reply.set_reply_uuid(forte_msg.get_forte_uuid())
                        forte_reply.set_reply_data(ps.decode('utf-8'))
                        await self._nc.publish(msg.reply, forte_reply.dump_yaml().encode())
                        print('published ps response')


        await self._nc.close()
    


        