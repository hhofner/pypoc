# PYPOC
A Simplified Discrete Event Simulator for Heterogeneous Wireless Networks.

## Installation
Clone this repo. Ensure a Python version of 3.6 or higher. One may use PIP to install the necessary libraries by running:
```
pip3 -r requirements.txt 
```

## Usage
To run this simulation, go into the pypoc directory and run the (same name) directory of pypoc:

```
python pypoc
```

When wanting to run a specific network simulation with specific parameters, create and edit a `config.toml` file, which contains the structure explained in the attached `example_config.toml` file. It uses [TOML syntax](https://github.com/toml-lang/toml).

The network simulation uses "Bytes" instead of "bits" (packets instead of streams) and so any bandwidth or packet size parameters should be in Bytes for example:

```toml
downlink_bandwith = 1_000  # equals to 1 Kilo-Byte per second, or 8Kbps
```

The simulation outputs a CSV file containing all the relevant data of the simulation.

## What Can It Do?
TODO

## Configuration File Structure
The configuration file `config.toml` defines all the specific parameters for the network. 

## Code Documentation

The core of the code resides in the PYPOC directory. These files should rarely change once the code base
is stable. Someone who wants to run a simulation will do so only by editing the configuration file named "setup.ini"
and the corresponding simulation results will be put into a directory.


