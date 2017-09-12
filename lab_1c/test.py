from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,INT, BOOL, UINT32, ListFieldType
import asyncio
from io import StringIO
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
from playground.common import logging as p_logging

#Call Start Message
class startcall(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.start"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ('flag', STRING)]


#Calling INVITE Packet Class Definition
class invite(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.invite"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("name", STRING),
               ("location", STRING),
               ("ip", STRING),
               ("port", UINT32),
               ("xccpv", INT),
               ("codec", ListFieldType(STRING)),
               ]

#Call Response Packet Class Definition
class response(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.response"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("name", STRING),
               ("location", STRING),
               ("ip", STRING),
               ("port", UINT32),
               ("xccpv", INT),
               ("codec", ListFieldType(STRING)),
               ]

#Session Start Packet Class Definition
class session(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.session"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("callingip", STRING),
               ("callingport", UINT32),
               ("calledip", STRING),
               ("calledport", UINT32),
               ("codec", STRING),
               ("payload", INT)]

#BYE Message to disconnect the call
class bye(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.bye"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("flag", STRING)
               ]

class EchoClientProtocol(asyncio.Protocol):

    name='test'
    location='test'
    xccpv='1'
    ip='test'
    port=23
    codec=['testlist']

    pkx = startcall()
    pkx.flag = 'test'

    def response(self, name, location, xccpv, ip, port, codec):
        self.name = name
        self.location = location
        self.xccpv = xccpv
        self.ip = ip
        self.port = port
        self.codec = codec

    def __init__(self, loop):
        self.transport = None
        self.loop = loop
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("EchoClient is now Connected to the Server")
        self.transport = transport

        pkx1 = self.pkx.__serialize__()
        self.transport.write(pkx1)

    def data_received(self, data):
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if(pkt.DEFINITION_IDENTIFIER=='lab1b.calling.invite'):
                print('CLIENT RECEIVED: Call Invite from Bob')
                print(pkt)
                res = response()
                res.name = self.name; res.location = self.location; res.xccpv = self.xccpv; res.ip = self.ip; res.port = self.port; res.codec = self.codec
                pky = res.__serialize__()
                self.transport.write(pky)

            elif(pkt.DEFINITION_IDENTIFIER=='lab1b.calling.session'):
                print('CLIENT RECEIVED: Call session start from Bob')
                print(pkt)
                byepkt = bye()
                byepkt.flag = 'test'
                byep = byepkt.__serialize__()
                self.transport.write(byep)

    def connection_lost(self, exc):
        self.transport = None
        print("EchoClient Connection was Lost with Server because {}".format(exc))
        self.loop.stop()

class EchoServerProtocol(asyncio.Protocol):
    name='test'; location='test'; xccpv='1'; ip='test'; port=23; codec=['testlist']; ip1='test'; ip2='test'; port1=0; port2=0
    payload = {'G711u':64, 'G729':8, 'G711a':64, 'G722':84, 'OPUS': 124}

    def invite(self, name, location, xccpv, ip, port, codec):
        self.name = name
        self.location = location
        self.xccpv = xccpv
        self.ip = ip
        self.port = port
        self.codec = codec

    def session(self, ip1, port1, ip2, port2, codec, payload):
        self.ip1 = ip1
        self.port1 = port1
        self.ip2 = ip2
        self.port2 = port2
        self.codec = codec
        self.payload = payload

    def __init__(self):
        self.transport = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("\nEchoServer is now Connected to a Client")
        self.transport = transport

    def data_received(self, data):
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            if(packet.DEFINITION_IDENTIFIER == "lab1b.calling.start"):
                print('SERVER RECEIVED: Call start request from Alice.')
                print(packet)
                inv = invite()
                inv.name = self.name; inv.location = self.location; inv.xccpv = self.xccpv; inv.ip = self.ip; inv.port = self.port; inv.codec = self.codec
                pkbytes = inv.__serialize__()
                self.transport.write(pkbytes)

            elif(packet.DEFINITION_IDENTIFIER=='lab1b.calling.response'):
                print('SERVER RECEIVED: Call response from Alice.')
                print(packet)
                ses = session()
                ses.ip1=inv.ip; ses.ip2=packet.ip; ses.port1 = inv.port; ses.port2 = packet.port
                ses.codec = 'G711'
                ses.payload = 8
                '''for codec in list(inv.codec):
                    for codec1 in list(packet.codec):
                        if codec==codec1:
                            ses.codec=codec
                    ses.payload = int(self.payload[ses.codec])'''
                pkbytes = ses.__serialize__()
                self.transport.write(pkbytes)
            elif(packet.DEFINITION_IDENTIFIER=='lab1b.calling.bye'):
                print('SERVER RECEIVED: Call disconnect request Alice.')
                print(packet)

def basicUnitTest():

    loop = asyncio.get_event_loop()
    server = EchoServerProtocol()
    server.invite('Alice','California',1,'10.0.0.1',65001, ['G711u', 'G729', 'G722', 'OPUS', 'G711a'])
    client = EchoClientProtocol(loop)
    client.response('Bob', 'WashingtonDC', 1, '10.0.0.2', 65002, ["G729", "G722a"])
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)
    loop.close()

if __name__=="__main__":
    basicUnitTest()
