import math
import numpy as np

from scipy.constants import speed_of_light
import matplotlib.pyplot as plt

def FSPL(Distance, D_transmit=1, D_receive=1, Wavelength=None, Frequency=None, in_decibels=False):
    '''
    Simple Free Space Path Loss model method. If no directivity of the antennas 
    are specified, then the assumption is that the antennas are isotropic and 
    have no directivity.

    :param Distance: Distance between antennas in METERS (!!).
    :param D_transmit: Directivity of transmitting antenna. Optional.
    :param D_receive: Directivity of receiving antenna. Optional.
    :param Wavelength: Signal wavelength. Not needed if Frequency is provided.
    :param Frequency: Signal frequency in KiloHertz(!!). Not needed if Wavelength is provided.
    :param in_decibels: Return the path loss in decibles with the assumption that the antenna is isotropic.
    :return: Float, loss value. Multiply by transmitted power to get your received power value.
             If in_decibels is True, then the returned value is in dB.
    '''
    if Frequency is None:
        Frequency = speed_of_light / Wavelength
        Frequency = Frequency / 1000  #convert to KHz
    
    if Wavelength is None:
        Frequency = Frequency * 1000 # convert to Hz from KHz
        Wavelength = speed_of_light / Frequency

    if in_decibels:
        # Free-space path loss in decibels based on formula provided in Wikipedia: https://en.wikipedia.org/wiki/Free-space_path_loss
        return (20 * math.log10(Distance)) + (20 * math.log10(Frequency)) - 147.55
    else:
        return D_transmit * D_receive * (Wavelength / (4 * math.pi * Distance))**2

def channel_capacity(Bandwidth, SINR):
    '''
    Calculate the Channel Capacity based on the Shannon-Hartley Theorem.

    :param Bandwidth: Bandwidth value in Hertz (Hz)
    :param SINR: SINR value in ratio, not dB (!!). Use dB_to_watt method if needed.
    :return: bits per second value.
    '''
    return Bandwidth * math.log2(1 + SINR)

def dBm_to_watt(dBm_value):
    return (10**(dBm_value/10)/1000)

def dB_to_watt(dB_value):
    return 10**(dB_value/10)

def watt_to_dBm(watt_value):
    return 10 * math.log10(watt_value) + 30

if __name__ == '__main__':
    loss = FSPL(Distance=1, Frequency=15e3, in_decibels=True)
    print(f'Loss: {loss}')
    print(f'')
    SINR = dBm_to_watt(43)/dBm_to_watt(5)
    # SINR = dB_to_watt(15)
    print(SINR)
    print(channel_capacity(Bandwidth=30e3, SINR=SINR))

    loss_vals = []
    bandwidths = []
    distances = np.arange(1, 10, 0.2)
    for d in distances:
        watt_ratio = dB_to_watt(FSPL(Distance=d, Frequency=15e3, in_decibels=True))
        loss_vals.append(watt_ratio)
        SINR = dBm_to_watt(22) / (dBm_to_watt(5) * watt_ratio)
        cap = channel_capacity(Bandwidth=30e3, SINR=SINR)
        print(f'Capacity: {cap}\n\tRatio Loss = {watt_ratio}\n\tSINR: {SINR}')
        bandwidths.append(cap)

    # plt.plot(distances, loss_vals, label='Wattage Loss')
    plt.plot(distances, bandwidths, color='green', label='Channel Capacity')
    plt.title("Channel Capacity in bps by Distance")
    plt.show()