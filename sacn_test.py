# Standard Library
import time

# Third Party Libraries
import sacn  # type: ignore # (no typing supported)

# provide an IP-Address to bind to if you want to send multicast packets from a specific interface
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

FIXTURE_COUNT = 3
FIXTURE_LAYOUT = {1: "red", 2: "green", 3: "blue"}
addresses_per_fixture = len(FIXTURE_LAYOUT)
address_count = FIXTURE_COUNT * addresses_per_fixture


# define a callback function
@receiver.listen_on("universe", universe=1)  # listens on universe 1
def callback(packet: sacn.DataPacket):  # packet type: sacn.DataPacket
    if packet.dmxStartCode > 0:
        return

    dmx_data = packet.dmxData[0:address_count]

    fixtures = {
        key: {
            FIXTURE_LAYOUT[address + 1]: fixture[address]
            for address in range(0, addresses_per_fixture)
        }
        for key, fixture in dict(
            enumerate(
                [
                    dmx_data[i : i + addresses_per_fixture]
                    for i in range(0, len(dmx_data), addresses_per_fixture)
                ]
            )
        ).items()
    }
    print(fixtures)


# optional: if multicast is desired, join with the universe number as parameter
receiver.join_multicast(1)

time.sleep(10)  # receive for 10 seconds

# optional: if multicast was previously joined
receiver.leave_multicast(1)

receiver.stop()
