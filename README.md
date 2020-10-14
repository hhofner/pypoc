# PYPOC
A Simplified Discrete Event Simulator for Heterogeneous Wireless Networks.

## Installation Steps
1. Clone this repo. 
2. Ensure a Python version of 3.6 or higher.
3. Install conda and pip.
4. Create a new conda env with:
```
pip3 -r requirements.txt 
```

## Usage
To run the simulation:
1. Edit the configuration files: `config.toml` and `config.py`
2. Run:

```
python -m pypoc
```

## Configuration

The simulation parameters are contained in the `config.toml` file. Copy the `template_config.toml` file and edit it to fit your simulation:
```
cp template_config.toml config.toml
```

TOML is a file format for config files. JSON is trash.

The network simulation uses "Bytes" instead of "bits" (packets instead of streams) and so any bandwidth or packet size parameters should be in Bytes for example:

```toml
downlink_bandwith = 1_000  # equals to 1 Kilo-Byte per second, or 8Kbps
```

The simulation outputs a CSV file containing all the relevant data of the simulation.

## Plotting
In the `/plot` directory you can find a list of scripts to help you plot things.

## Configuration File Structure
The configuration file `config.toml` defines all the specific parameters for the network. 

