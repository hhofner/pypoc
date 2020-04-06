import pypoc
import toml
import os
import time

NUMBER_OF_SOURCE_NODES = list(range(15, 150))

print("Loading TOML file")
config = toml.load('config.toml')

for count in NUMBER_OF_SOURCE_NODES:
    print(f"Editing Source Count from {config['nodes']['src-nodes']['count']} -- to --> {count}")
    config["nodes"]["src-nodes"]["count"] = count
    f=open('config.toml', mode='w')
    toml.dump(config, f)
    print("~~~~ Saved to file! ~~~~")
    time.sleep(0.5)  # IDK why
    print("...Now running...")
    try:
        os.system("python pypoc --run")
    except:
        break
