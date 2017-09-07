from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,INT, BOOL, UINT32

#Calling INVITE Packet Class Definition
class invite(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.invite"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("name", STRING),
               ("location", STRING),
               ("ip", STRING),
               ("port", UINT32),
               ("xccpv", INT),
               ("codec", STRING),
               ("payload", INT)]

#Call Response Packet Class Definition
class response(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.calling.response"
    DEFINITION_VERSION = "1.0"
    FIELDS = [ ("availability", BOOL),
               ("name", STRING),
               ("location", STRING),
               ("ip", STRING),
               ("port", UINT32),
               ("xccpv", INT),
               ("codec", STRING),
               ("payload", INT)]

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

#Basic unit test to test functionality
def basicUnitTest():

#INVITE packet details
    packet1 = invite()
    packet1.name = "Alice"
    packet1.location = "California"
    packet1.xccpv = 1
    packet1.ip = "10.0.0.1"
    packet1.port = 65001
    packet1.codec = "G711"
    packet1.payload = 64

#Response packet details
    packet2 = response()
    packet2.availability = True
    packet2.name = "Bob"
    packet2.location = "WashingtonDC"
    packet2.xccpv = 1
    packet2.ip = "10.0.0.2"
    packet2.port = 65002
    packet2.codec = "G729"
    packet2.payload = 8

#Start Session packet details
    packet3 = session()
    packet3.callingip = packet1.ip
    packet3.callingport = packet1.port
    packet3.calledip = packet2.ip
    packet3.calledport = packet2.port

    if (packet2.payload < packet1.payload):
        packet3.payload = packet2.payload
    else:
        packet3.payload = packet1.apyload

    if (packet3.payload == 64):
        packet3.codec = "G711"
    else:
        packet3.codec = "G729"

#Serialize and Deserializing the packets

    pktBytes = packet1.__serialize__() + packet2.__serialize__() + packet3.__serialize__()
    print("\nPackets are serialized now of", format(len(pktBytes)), "bytes and ready to be sent.\n")

    deserializer = PacketType.Deserializer()
    print("Packets are received. Starting with", format(len(pktBytes)), "bytes of data to deserialize.\n")
    while len(pktBytes) > 0:
        chunk, pktBytes = pktBytes[:10], pktBytes[10:]
        deserializer.update(chunk)
        print("Another 10 bytes loaded into deserializer. Number of bytes to process yet =", format(len(pktBytes)))
    print("\n")
    for packet in deserializer.nextPackets():
        print("Yay! Got a packet!")
        if packet == packet1: print("Found packet 1")
        elif packet == packet2: print("Found packet 2")
        elif packet == packet3: print("Found packet 3\n\n")

# Session Start Details to be printed
    print("Call session will now start with below characteristics:")
    print("Caller IP:", packet3.callingip)
    print("Caller Port", packet3.callingport)
    print("Called user IP:", packet3.calledip)
    print("Called user Port", packet3.calledport)
    print("Codec elected:", packet3.codec)
    print("Payload Size:", packet3.payload, " Kb's per second")

if __name__=="__main__":
    basicUnitTest()
