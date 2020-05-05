import pypoc
import toml
import os
import time
import argparse

NUMBER_OF_SOURCE_NODES = list(range(50, 250))

def run_changing_src_nodes(config_file, title):
    config = toml.load(config_file)
    for count in NUMBER_OF_SOURCE_NODES:
        print(f"Editing Source Count from {config['nodes']['src-nodes']['count']} -- to --> {count}")
        config["title"] = f'{title}_{count}'
        config["nodes"]["src-nodes"]["count"] = count
        f=open(config_file, mode='w')
        toml.dump(config, f)
        f.close()
        print("~~~~ Saved to file! ~~~~")
        time.sleep(0.5)  # IDK why
        print("...Now running...")
        try:
            os.system(f"python pypoc --run --config {config_file}")
        except:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default="nsfuvnutfreuagiureanfgu4anfgurebnghreabghrabghdbaghbda")
    parser.add_argument('--configFile', default="config.toml")
    args = parser.parse_args()
    ans = input(f"Run {args.title} with config {args.configFile}? [y]/n ")
    if not ans == "n":
        run_changing_src_nodes(args.configFile, args.title)