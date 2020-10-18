# PYPOC
A Simplified Discrete Event Simulator for Heterogeneous Wireless Networks.

## Installation Steps
1. Clone this repo. 
2. Ensure a Python version of 3.6 or higher.
3. Install conda (mini-conda) and pip.
4. Create a new conda env with:
```bash
conda env create -f environment.yml
```

NOTE: PyPoc assumes a unix environment (usage of '/' slashes, no smart path creation is used)

## Usage
To run the simulation:
1. Edit the configuration files: `config.toml` and `config.py` if running a Deep Q-Learning Network
2. Run this script from the PyPoc directory:

```bash
python -m pypoc --run --output_dir full/path/to/output/dir
```

to run the simulation with a different config file, use the `--config` flag:

```bash
python -m pypoc --run --config your/config.toml --output_dir full/path/to/output/dir
```

PyPoc will make a copy of your configuration into the specified output directory, as well as
put the generated data file in that directory (.csv).

## Configuration

The simulation parameters are contained in the `config.toml` file. Copy the `template_config.toml` file and edit it to fit your simulation:
```bash
cp template_config.toml config.toml
```

Copy the `config.py` file if you plan to use the Q-Node (Q-Learning Based Node):
```bash
cp template_config.py config.py
```

The network simulation uses "Bytes" instead of "bits" (packets instead of streams) and so any bandwidth or packet size parameters should be in Bytes for example:

```toml
downlink_bandwith = 1_000  # equals to 1 Kilo-Byte per second, or 8Kbps
```

The simulation outputs a CSV file containing all the relevant data of the simulation in the directory of `output_data/`.

## Plotting
In the `/plot` directory you can find a list of scripts to help you plot things.

## Running Simulations with Changing Parameters
The simulation only runs for the specified amount of minutes with no changing parameters (although this was implemented at some time, 
lack of motivation has led to its destruction).

So, to run simulations with changing parameters, utilize the scripts in `multi_sim_scripts/`. This
directory contains a collection of scripts that run multiple simulations with changing parameters.

## Directory Structure
```
├── README.md
├── config.py
├── environment.yml
├── multi_sim_scripts
│   ├── multiple200.py
│   ├── multiple300.py
│   ├── run_baseline_increasing.py
│   ├── run_multiple_simulations.py
│   └── run_qoffloading_increasing.py
├── output_data
├── plot
│   ├── __init__.py
│   ├── plot_average_delay.py
│   ├── plot_bar.py
│   ├── plot_increasing_drop_rate.py
│   ├── plot_increasing_throughput.py
│   ├── plot_loss.py
│   ├── plot_queue_sizes.py
│   ├── plot_reward.py
│   ├── plot_reward_progress.py
│   ├── plot_throughput.py
│   ├── plot_topology.py
│   └── plot_visual_topologies.py
├── pypoc
│   ├── __init__.py
│   ├── __main__.py : entrance script, creates output data file to write to
│   ├── config.py
│   ├── edgehandler.py : class that is responsible for "edges" in the network
│   ├── mobility.py : class 
│   ├── models.py
│   ├── network.py : class that contains all nodes, represents the network
│   ├── node.py : defines the node class
│   ├── plot_topology.py
│   ├── plotter.py
│   ├── qnode.py
│   ├── signal_tools.py
│   └── topology.py
├── template_config.py
└── tools
    ├── gif_images
    ├── make_gif.py
    ├── outputName.gif
    ├── run_multiple_dynamic_UAV.py
    └── run_multitple_static_simulations.py
```
