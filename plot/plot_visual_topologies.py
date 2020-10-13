import argparse

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
seed = 772723
# seed = 5842005
np.random.seed(seed)

class TopData:
    def __init__(self):
        self.data = None
        self.metadata = None
        self.color = None
        self.marker = None
        self.size = 150

def distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a-b)

def calculate_base_station_locations(avg_value, x, y):
    ''' Normal distribution of base stations based on avg_value 
        with 500 meter distance between BS.
    '''
    avg_number_of_base_stations = x * y * avg_value
    number_of_base_stations = int(max(avg_number_of_base_stations, 
                                  np.random.normal(avg_number_of_base_stations)))

    x_data = []
    y_data = []
    for base_station in range(number_of_base_stations):
        # Keep at least 500m distance between BS's
        distances_ok = False
        while not distances_ok:
            x1 = x * np.random.rand(1)
            y1 = y * np.random.rand(1)
            if not x_data:
                break
            for x2, y2 in zip(x_data, y_data): 
                if distance((x2, y2), (x1, y1)) < 0.5:
                    distances_ok = False
                    break
                distances_ok = True
                
        x_data.append(x1)
        y_data.append(y1)
    
    BaseStationData = TopData()
    BaseStationData.data = (x_data, y_data)
    BaseStationData.color = 'red'
    BaseStationData.marker = '^'

    return BaseStationData

def calculate_uav_locations(uav_count, BaseStation, x, y):
    '''TODO: Documentation, Z-coord calculations
    '''
    existing_bs_x, existing_bs_y = BaseStation.data
    uav_x_coord = []
    uav_y_coord = []
    uav_z_coord = []
    for _ in range(uav_count):
        # Keep at least 300m distance between BS's
        distances_ok = False
        while not distances_ok:
            uav_x = x * np.random.rand(1)
            uav_y = y * np.random.rand(1)
            for bs_x, bs_y in zip(existing_bs_x, existing_bs_y):
                if distance((bs_x, bs_y), (uav_x, uav_y)) < 0.3:
                    distances_ok = False
                    break
                distances_ok = True
                
        uav_x_coord.append(uav_x)
        uav_y_coord.append(uav_y)
    
    UAVBaseStationData = TopData()
    UAVBaseStationData.data = (uav_x_coord, uav_y_coord, uav_z_coord)    
    UAVBaseStationData.color = 'green'


if __name__ == "__main__":
    sns.set()
    sns.set_style('whitegrid')
    
    '''Base Stations'''
    BaseStations = calculate_base_station_locations(0.8386, 3.5, 3.5)
    x, y = BaseStations.data
    plt.scatter(x, y, color=BaseStations.color, 
                      marker=BaseStations.marker, s=BaseStations.size)
    
    '''UAV Base Stations'''
    # UAVBaseStations = calculate_uav_locations(5, )

    '''Satellites'''

    '''Cell Circles (or Hexagons)'''


    plt.xlabel('km')
    plt.ylabel('km')
    plt.title(f'Normal Distributed Macro Base Station Locations\nrandom seed: {seed}')
    plt.show()