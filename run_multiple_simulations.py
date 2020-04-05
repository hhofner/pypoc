import pypoc
import toml
import os

NUMBER_OF_SOURCE_NODES = list(range(15, 150))

print("Loading TOML file")
config = toml.load('config.toml')

for count in NUMBER_OF_SOURCE_NODES:
    print(f"Editing TOML file from {config['nodes']['src-nodes']['count']} --> {count}")
    config["nodes"]["src-nodes"]["count"] = count
    f=open('config.toml', mode='w')
    toml.dump(config, f)
    print("Saved to file!")
    print("Now running...")
    try:
        os.system("python pypoc --run")
    except:
        break
