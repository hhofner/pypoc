# PYPOC
A Python Discrete Event Simulator for Heterogeneous Wireless Networks. 

To run this simulation, go into the pypoc directory and run the (same name) directory of pypoc:

```
python pypoc
```

When wanting to run a specific network simulation with specific parameteres, edit the `setup.ini` file, which the structure of that config file is explained below.

The network simulation uses "Bytes" instead of "bits" (packets instead of streams) and so any bandwidth or packet size parameters should be in Bytes for example:

```python
bandwith=1e3  # equals to 1 Kilo-Byte per second, or 8Kbps
```



## Configuration File Structure
The configuration file `setup.ini` defines all the specific parameters for the network. The specific writing style as of now is: everything but specific parameters under sections are lower-case.

#### [network]

#### [nodes]

#### [positions]
- BASE_STATION_POSITIONING_METHOD: The algorithmic method to determine the positions of base stations.
    - normal
- BASE_STATION_POSITIONS: This allows you to specify by hand the (x, y) coordinate of base stations. This overrides the previous positioning method parameter.
    - x1 y1 x2 y2 x3 y3 ...

#### [ground-physical]
- THRESHOLD_CAPACITY : This option is used for when decididing whether a UE is far away enough for the link not to be valid. It compares the calculated bandwidth (with signal tools) to this threshold.
    - {integer number}

#### [air-physical]

#### [space-physical]

#### [data]

## Developer Notes
Parameters will be passed down by **kwargs.