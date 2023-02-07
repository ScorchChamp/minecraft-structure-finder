import anvil
import os
import time
import threading
from threading import Event

def numberToInChunkCoords(number):
    bits = str(bin(number))[2:]
    print(bits)
    return (int(bits[-31:], 2), int(bits[0:-32], 2))

def runScript(worldName, event):
    print("Starting script for world " + worldName)
    region_keys = {}

    while not event.is_set():
            region_folder = worldName + "/region/"
            region_files = os.listdir(region_folder)
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
                                if len(chunkData['structures']['References']) == 1 and 'minecraft:mineshaft' in chunkData['structures']['References']:
                                    continue
                                new_keys = chunkData['structures']['References'].keys() + chunkData['structures']['starts'].keys()

                                new_keys.remove('minecraft:mineshaft') if 'minecraft:mineshaft' in new_keys else None
                                new_keys.remove('minecraft:ancient_city') if 'minecraft:ancient_city' in new_keys else None
                                new_keys.remove('minecraft:ocean_ruin_warm') if 'minecraft:ocean_ruin_warm' in new_keys else None

                                if chunkData['xPos'].value*16 not in region_keys:
                                    region_keys[chunkData['xPos'].value*16] = {}
                                if chunkData['zPos'].value*16 not in region_keys[chunkData['xPos'].value*16]:
                                    region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = []
                                if region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] != new_keys:
                                    region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = new_keys
                                    print([numberToInChunkCoords(chunkData['structures']['References'][key].value[0]) for key in chunkData['structures']['References'].keys()])
                                    print(new_keys, chunkData['xPos'].value*16, chunkData['zPos'].value*16)

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

    
worlds_dir = "C:\\Users\\Scorch\\AppData\\Roaming\\.minecraft\\profiles\\1.19.2\\saves"
world_folder = ""
while True:
    event = Event()
    thread = threading.Thread(target=runScript, args=(world_folder, event))
    thread.start()
    while newest(worlds_dir) == world_folder:
        time.sleep(1)
    event.set()
    world_folder = newest(worlds_dir)