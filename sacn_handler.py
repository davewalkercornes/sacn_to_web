# Standard Library
import atexit
from typing import Callable, Optional

# Third Party Libraries
import sacn  # type: ignore # (no typing supported)

# provide an IP-Address to bind to if you want to send multicast packets from a specific interface
receiver = sacn.sACNreceiver()

UNIVERSE = 3
FIXTURE_COUNT = 12
FIXTURE_LAYOUT = {1: "red", 2: "green", 3: "blue", 4: "gobo"}
addresses_per_fixture = len(FIXTURE_LAYOUT)
address_count = FIXTURE_COUNT * addresses_per_fixture

callback: Optional[Callable] = None


# define a callback function
@receiver.listen_on("universe", universe=UNIVERSE)  # listens on universe 1
def sacn_callback(packet: sacn.DataPacket):  # packet type: sacn.DataPacket
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
    if callback:
        callback(fixtures)


def set_callback(callback_function: Callable):
    global callback
    callback = callback_function


def start():
    receiver.start()
    receiver.join_multicast(UNIVERSE)


@atexit.register
def stop():
    receiver.leave_multicast(UNIVERSE)
    receiver.stop()
