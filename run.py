import anvil
import os
import time
import threading
from threading import Event

filtered_structures = ['minecraft:mineshaft', 'minecraft:nether_fossil', 'minecraft:ancient_city', 'minecraft:ocean_ruin_warm', 'minecraft:ocean_ruin_cold']
region_keys = {}

def checkChunk(chunkData):
    global region_keys
    new_keys = chunkData['structures']['References'].keys() + chunkData['structures']['starts'].keys()
    for key in filtered_structures: 
        while key in new_keys: new_keys.remove(key)
    if len(new_keys) == 0: return None
    if chunkData['xPos'].value*16 not in region_keys: region_keys[chunkData['xPos'].value*16] = {}
    if chunkData['zPos'].value*16 not in region_keys[chunkData['xPos'].value*16]: region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = []
    if region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] == new_keys: return None
    region_keys[chunkData['xPos'].value*16][chunkData['zPos'].value*16] = new_keys
    return new_keys

def runScript(worldName, event, worldFolder):
    print("Starting script for world " + worldName)
    global region_keys
    region_keys = {}

    while not event.is_set():
        region_folder = worldName + worldFolder
        try: region_files = os.listdir(region_folder)
        except: continue
        region_files = [region_folder + f for f in region_files if f.endswith(".mca")]
        for region_file in region_files:
            region = anvil.Region.from_file(region_file)
            for x_chunk in range(16):
                for z_chunk in range(16):
                    if event.is_set(): break
                    try: chunkData = region.chunk_data(x_chunk, z_chunk)
                    except: continue
                    if chunkData is None: continue
                    new_keys = checkChunk(chunkData)
                    if new_keys is None: continue
                    print('Nether' if worldFolder.startswith('/DIM-1/') else 'Overworld', new_keys, chunkData['xPos'].value*16, chunkData['zPos'].value*16)

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

    
worlds_dir = os.getenv('APPDATA') + "\\.minecraft\\saves"
world_folder = ""
world_folder = newest(worlds_dir)
while True:
    event = Event()
    thread = threading.Thread(target=runScript, args=(world_folder, event, "/region/"))
    thread2 = threading.Thread(target=runScript, args=(world_folder, event, "/DIM-1/region/"))
    thread.start()
    thread2.start()
    while newest(worlds_dir) == world_folder: time.sleep(1)
    event.set()
    world_folder = newest(worlds_dir)