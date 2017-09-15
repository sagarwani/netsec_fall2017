from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,INT, BOOL, UINT32, ListFieldType
import asyncio
from io import StringIO
import playground
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
from playground.common import logging as p_logging

#Call Start Message
class startcall(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.start"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ('flag', BOOL)]

#Call Response Packet Class Definition
class response(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.response"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("name", STRING),
               ("available", BOOL),
               ("location", STRING),
               ("ip", STRING),
               ("port", UINT32),
               ("xccpv", INT),
               ("codec", ListFieldType(STRING)),
               ]
#BYE Message to disconnect the call
class bye(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.bye"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("flag", BOOL)
               ]

#Calling INVITE Packet Class Definition
class invite(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.invite"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("name", STRING),
               ('available', BOOL),
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

class busy(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.busy"
    DEFINITION_VERSION = "1.0"
    FIELDS = [  ]

class EchoServerProtocol(asyncio.Protocol):
    name='test'; location='test'; xccpv='1'; ip='test'; port=23; codec=['testlist']; ip1='test'; ip2='test'; port1=0; port2=0;available=1
    payload = {'G711u':64, 'G729':8, 'G711a':64, 'G722':84, 'OPUS': 124}
    output1 = StringIO
    output2 = StringIO
    lst1 = []
    state=0
    cod=0
    def invite(self, name, location, available, xccpv, ip, port, codec):
        self.name = name
        self.location = location
        self.available = available
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
        self.invite('Bob', 'California', 1, 1, '10.0.0.1', 65001, ['G711u', 'G729', 'G722', 'OPUS', 'G711a'])
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("\nEchoServer is now Connected to a Client\n")
        self.transport = transport

    def data_received(self, data):
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            if(packet.DEFINITION_IDENTIFIER == "lab1b.calling.start") and (self.available==1) and self.state==0:
                print('CLIENT -> SERVER: Call start request')
                print('\t\t\t\t ', packet)
                self.state +=1
                inv = invite()
                inv.name = self.name; inv.location = self.location; inv.xccpv = self.xccpv; inv.ip = self.ip; inv.port = self.port; inv.codec = self.codec; inv.available = self.available
                self.output1 = inv.ip
                self.output2 = inv.port
                self.lst1 = inv.codec
                pkbytes = inv.__serialize__()
                self.transport.write(pkbytes)
            elif(packet.DEFINITION_IDENTIFIER == "lab1b.calling.start") and (self.available==0) and self.state==0:
                bus = busy()
                pkbytes = bus.__serialize__()
                self.transport.write(pkbytes)
            elif(packet.DEFINITION_IDENTIFIER=='lab1b.calling.response') and self.state==1:
                print('CLIENT -> SERVER: Call response from {}'.format(packet.name))
                print('\t\t\t\t ', packet)
                self.state +=1
                ses = session()
                ses.callingip=self.output1; ses.calledip=packet.ip; ses.callingport = self.output2; ses.calledport = packet.port
                for codec in list(self.lst1):
                    for codec1 in list(packet.codec):
                        if codec==codec1:
                            ses.codec=codec
                            self.cod += 1
                if self.cod==0:
                    print('\nClient does not have supported codecs. Connection will now terminate.')
                else:
                    ses.payload = int(self.payload[ses.codec])
                    pkbytes = ses.__serialize__()
                    self.transport.write(pkbytes)
            elif(packet.DEFINITION_IDENTIFIER=='lab1b.calling.bye') and self.state==2:
                print('CLIENT -> SERVER: Call disconnect request from Alice.')
                print('\t\t\t\t ', packet)
                self.transport.close()
            else:
                print('Incorrect packet received. Please check the protocol on server side.')
                self.transport.close()

if __name__ == "__main__":

    #p_logging.EnablePresetLogging(p_logging.PRESET_TEST)
    loop = asyncio.get_event_loop()
    #loop.set_debug(enabled=True)
    #lux = EchoServerProtocol()
    #lux.invite('Bob', 'California', 1, 1, '10.0.0.1', 65001, ['G711u', 'G729', 'G722', 'OPUS', 'G711a'])
    coro = playground.getConnector().create_playground_server(lambda: EchoServerProtocol(), 8888)
    #conn = loop.create_server(lambda: EchoServerProtocol(), port=8000)
    loop.run_until_complete(coro)
    #print('\nListening on {}:'.format(server.sockets[0].getsockname()))
    #print('\nPress Ctrl+C to terminate the process')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
