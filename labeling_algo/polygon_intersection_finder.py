import time
import signal
import sys
import multiprocessing
import os
import geopandas as gpd
import pandas

COORDS_FILE = "Data/ETAK_EESTI_GPKG.gpkg"
REPORT_TIME = 5
NR_THREADS = os.cpu_count() - 2

def unpack_db(db_file):
    db1 = gpd.read_file(db_file, layer="E_501_tee_j", engine="pyogrio").geometry
    db2 = gpd.read_file(db_file, layer="E_501_tee_a", engine="pyogrio").geometry
    return pandas.concat([db1, db2], ignore_index=True)

def print_logs_if_needed(last_report_time, nr_roads_done, nr_roads, start_time, nr_found):
    if time.time() < last_report_time + REPORT_TIME:
        return last_report_time
    progress = nr_roads_done/nr_roads
    time_taken = round(time.time() - start_time, 4)
    if progress == 0:
        time_left = 999999999999
    else:
        time_left = ((1/progress)*time_taken)-time_taken
    print("-------------------------------------------------")
    print(f"Nr of roads processed: {nr_roads_done}/{nr_roads}")
    print(f"Nr of intersections found: {nr_found}")
    print(f"Current progress: {round(progress*100, 3)}%")
    print(f"Time taken: {round(time_taken, 3)}s")
    print(f"Estimated time left: {round(time_left, 3)}s")
    print("-------------------------------------------------\n")
    return time.time()

def write_results_to_file(intersections):
    out_string = ""

    print(f"Writing {len(intersections)} entries..")
    for intersection in intersections:
        out_string += f"{intersection[0]},{intersection[1]}\n"

    with open("ristmikud_raw.csv", "a+") as out_file:
        out_file.write(out_string)
        out_file.close()

    print("Goooooodbyeeeeeeeeeeee!")
    sys.exit(0)

# This will get summoned as a thread to process a certain road
# Each road will be processed by a different thread because it requires surprising amount of computational power
def process_road(d_queue, roads):
    if len(roads) < 2:
        return
    current_road = roads.iloc[0]
    other_roads = roads.iloc[1:]
    intersections = []
    for other_road in other_roads:
        intersection = current_road.intersection(other_road)
        if type(intersection) is list:
            for section in intersection:
                if section.is_empty:
                    continue
                section = section.centroid
                section.append([section.x, section.y])
        else:
            if intersection.is_empty:
                continue
            intersection = intersection.centroid
            intersections.append([intersection.x, intersection.y])
    d_queue.put(intersections)

print("Starting up...")
road_coords = unpack_db(COORDS_FILE)
nr_roads = len(road_coords)
found_intersections = []

last_report_time = start_time = time.time() - 56391.228
current_threads = []
data_queue = multiprocessing.Queue()
stop = False
def stop_f(sig, frame):
    global stop
    print("Sent a stop signal..")
    stop = True

print("Starting to find intersections...")
signal.signal(signal.SIGINT, stop_f)
# Iterate through all of the roads
done = False
road_index = 128787
while not done:
    if road_index >= len(road_coords) - 1:
        done = True
        break

    if stop:
        break

    # Clean up threads that have done their jobs and create new ones
    current_threads = [t for t in current_threads if t.is_alive()]
    while len(current_threads) < NR_THREADS:
        current_threads.append(multiprocessing.Process(target=process_road, args=(data_queue, road_coords.iloc[road_index:])))
        current_threads[-1].start()
        road_index += 1

    while not data_queue.empty():
        intersections = data_queue.get()
        for intersection in intersections:
            found_intersections.append(intersection)

    last_report_time = print_logs_if_needed(last_report_time, road_index - len(current_threads), nr_roads, start_time, len(found_intersections))
    time.sleep(0.001)

print("Waiting for threads to stop, might take a few minutes...")
while len(current_threads) > 0:
    current_threads = [t for t in current_threads if t.is_alive()]

while not data_queue.empty():
    intersections = data_queue.get()
    for intersection in intersections:
        found_intersections.append(intersection)

if done:
    print("Intersections done, will convert them to writable string now...")
write_results_to_file(found_intersections)
