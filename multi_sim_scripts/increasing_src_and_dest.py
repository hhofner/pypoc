from run_sim_with_increasing import MultiSim

data_dir = '/Users/hhofner/Documents/katolab/PyPoc/output_data/'

config = 'config.toml'

var = 'nodes.src-nodes.count'

starting = 13

ending = 27

steps = 1

sim_name = 'testaroo_1234'

test1 = MultiSim(config, var, starting, ending, steps, data_dir, sim_name)

test1.run()
