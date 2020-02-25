# PYPOC
A Python Discrete Event Simulator for Heterogeneous Wireless Networks

## Configuration File Structure
The configuration file `setup.ini` defines all the specific parameters for the network. The specific writing style as of now is: everything but specific parameters under sections are lower-case.

#### [nodes] section

#### [positions] section
- BASE_STATION_POSITIONING_METHOD: The algorithmic method to determine the positions of base stations.
    - normal
- BASE_STATION_POSITIONS: This allows you to specify by hand the (x, y) coordinate of base stations. This overrides the previous positioning method parameter.
    - x1 y1 x2 y2 x3 y3 ...

#### [ground-physical] section

#### [air-physical] section

#### [space-physical] section

#### [data] section