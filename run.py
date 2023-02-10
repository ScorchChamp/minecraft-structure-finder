import anvil
import os
import time
import threading
from threading import Event

MINESHAFT = 'minecraft:mineshaft'

def runScript(worldName, event, worldFolder):
    print("Starting script for world " + worldName)
    region_keys = {}

    while not event.is_set():
        region_folder = worldName + worldFolder
        try: 
            region_files = os.listdir(region_folder)
        except:
            continue
        region_files = [region_folder + f for f in region_files if f.endswith(".mca")]
        for region_file in region_files:
            region = anvil.Region.from_file(region_file)
            for x_chunk in range(16):
                for z_chunk in range(16):
                    if event.is_set(): break
                    try: 
                        chunkData = region.chunk_data(x_chunk, z_chunk)
                    except:
                        continue
                    if chunkData is not None:
                        if chunkData['structures']['References'] != {}:
                            if len(chunkData['structures']['References']) == 1 and MINESHAFT in chunkData['structures']['References']:
                                continue
                            new_keys = chunkData['structures']['References'].keys() + chunkData['structures']['starts'].keys()

                            new_keys.remove(MINESHAFT) if MINESHAFT in new_keys else None
                            new_keys.remove('minecraft:ancient_city') if 'minecraft:ancient_city' in new_keys else None
                            new_keys.remove('minecraft:ocean_ruin_warm') if 'minecraft:ocean_ruin_warm' in new_keys else None
                            new_keys.remove('minecraft:nether_fossil') if 'minecraft:nether_fossil' in new_keys else None

                            if chunkData['xPos'].value*16 not in region_keys:
                                region_keys[chunkData['xPos'].value*16] = {}
                            if chunkData['zPos'].value*16 not in region_keys[chunkData['xPos'].value*16]:
                                region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = []
                            if region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] != new_keys:
                                region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = new_keys
                                print(worldFolder, new_keys, chunkData['xPos'].value*16, chunkData['zPos'].value*16)

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

    
worlds_dir = "C:\\Users\\Larsc\\AppData\\Roaming\\.minecraft\\saves"
world_folder = ""
world_folder = newest(worlds_dir)
while True:
    event = Event()
    thread = threading.Thread(target=runScript, args=(world_folder, event, "/region/"))
    thread2 = threading.Thread(target=runScript, args=(world_folder, event, "/DIM1/region/"))
    thread3 = threading.Thread(target=runScript, args=(world_folder, event, "/DIM-1/region/"))
    thread.start()
    thread2.start()
    thread3.start()
    while newest(worlds_dir) == world_folder:
        time.sleep(1)
    event.set()
    world_folder = newest(worlds_dir)