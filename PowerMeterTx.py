import sys
import hashlib
from ant.core import message, node
from ant.core.constants import *
from ant.core.exceptions import ChannelError
from subprocess import check_output

CHANNEL_PERIOD = 8182
POWER_DEVICE_TYPE = 0x0B

# ANT+ network key
NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Get the serial number of CPU
def getserial():
    try:
        # Extract serial from wmic command
        cpuserial = check_output('wmic cpu get ProcessorId').decode().split('\n')[1].strip()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

# ANT+ ID of the virtual power sensor
# The expression below will choose a fixed ID based on the CPU's serial number
POWER_SENSOR_ID = int(int(hashlib.md5(getserial().encode()).hexdigest(), 16) & 0xfffe) + 1

# Transmitter for Bicycle Power ANT+ sensor
class PowerMeterTx(object):
    class PowerData:
        def __init__(self):
            self.eventCount = 0
            self.eventTime = 0
            self.cumulativePower = 0
            self.instantaneousPower = 0

    def __init__(self, antnode, sensor_id):
        self.antnode = antnode

        # Get the channel
        self.channel = antnode.getFreeChannel()
        try:
            self.channel.name = 'C:POWER'
            network = node.Network(NETKEY, 'N:ANT+')
            self.channel.assign(network, CHANNEL_TYPE_TWOWAY_TRANSMIT)
            self.channel.setID(POWER_DEVICE_TYPE, sensor_id, 0)
            self.channel.period = CHANNEL_PERIOD
            self.channel.frequency = 57
        except ChannelError as e:
            print("Channel config error: " + repr(e))
        self.powerData = PowerMeterTx.PowerData()

    def open(self):
        self.channel.open()

    def close(self):
        self.channel.close()

    def unassign(self):
        self.channel.unassign()

    # Power was updated, so send out an ANT+ message
    def update(self, power, cadence=None):
        self.powerData.eventCount = (self.powerData.eventCount + 1) & 0xff
        self.powerData.cumulativePower = (self.powerData.cumulativePower + int(power)) & 0xffff
        self.powerData.instantaneousPower = int(power)

        payload = bytearray(b'\x10')  # standard power-only message
        payload.append(self.powerData.eventCount)
        payload.append(0xFF)  # Pedal power not used
        if cadence is None: cadence = 0xFF
        payload.append(int(cadence) & 0xff)
        payload.append(self.powerData.cumulativePower & 0xff)
        payload.append(self.powerData.cumulativePower >> 8)
        payload.append(self.powerData.instantaneousPower & 0xff)
        payload.append(self.powerData.instantaneousPower >> 8)

        ant_msg = message.ChannelBroadcastDataMessage(self.channel.number, data=payload)
        self.antnode.send(ant_msg)
