import ast
import time
import signal
import sys
import multiprocessing
import os

COORDS_FILE = "tee_koordinaadid.csv"
REPORT_TIME = 5
NR_THREADS = os.cpu_count()

def unpack_csv(filename):
    out_data = []
    with open(filename, "r") as file:
        raw_data = file.read().split("\n")
        for line in raw_data:
            if line == "":
                continue
            road_number, coords = line.split("\t")
            coords = ast.literal_eval(coords)
            out_data.append([int(road_number), coords])
    return out_data


# Courtesy to: https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
        return (ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)) or (A == C or A == D or B == C or B == D)

# Returns the format y = ax + b
def line_coefficients(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x1 == x2:
        return float('inf'), x1

    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1

    return slope, intercept

def find_intersection_point(line1, line2):
    m1, b1 = line_coefficients(line1[0], line1[1])
    m2, b2 = line_coefficients(line2[0], line2[1])

    # If both are vertical, just find which points are the closest as this function only gets called when they surely intersect
    if m1 == float('inf') and m2 == float('inf') or m1 == m2:
        if line1[0] == line2[0] or line1[0] == line2[1]:
            return line1[0]
        elif line1[1] == line2[0] or line1[1] == line2[1]:
            return line1[1]
    elif m1 == float('inf'):
        x_intersection = b1
        y_intersection = m2 * x_intersection + b2
    elif m2 == float('inf'):
        # Line 2 is vertical
        x_intersection = b2
        y_intersection = m1 * x_intersection + b1
    else:
        x_intersection = (b2 - b1) / (m1 - m2)
        y_intersection = m1 * x_intersection + b1

    return [x_intersection, y_intersection]

def get_segment_intersection(line1, line2):
    if intersect(line1[0], line1[1], line2[0], line2[1]):
        return find_intersection_point(line1, line2)
    return None

def print_logs_if_needed(last_report_time, nr_roads_done, nr_roads, done_segments, total_segments, start_time, nr_found):
    if time.time() < last_report_time + REPORT_TIME:
        return last_report_time
    progress = done_segments/total_segments
    time_taken = round(time.time() - start_time, 4)
    if progress == 0:
        time_left = float('inf')
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

def write_results_to_file(intersections, road_nr, total_segments):
    out_string = ""
    lines_to_remove = []
    try:
        with open("ristmikud_raw.csv", "r") as in_file:
            temp = in_file.read().split("\n")
            for idx, line in enumerate(temp):
                if ";" in line:
                    lines_to_remove.append(idx)

        removed = 0
        for line in lines_to_remove:
            del temp[line]
            removed += 1

        for line in temp:
            if line == "":
                continue
            out_string += line + "\n"
    except:
        pass

    print(f"Writing {len(intersections)} entries..")
    for intersection in intersections:
        out_string += f"{intersection[0]},{intersection[1]}\n"
    out_string += f"{road_nr};{total_segments}\n"

    with open("ristmikud_raw.csv", "w") as out_file:
        out_file.write(out_string)
        out_file.close()

    print("Goooooodbyeeeeeeeeeeee!")
    sys.exit(0)

# This will get summoned as a thread to process a certain road
# Each road will be processed by a different thread because it requires surprising amount of computational power
def process_road(d_queue, roads):
    if len(roads) < 2:
        return
    processed_segments = 0
    current_road = roads[0][1]
    other_roads = roads[1:]
    nr_current_segments = len(current_road)
    intersections = []
    # Iterate through every segment in every road
    for idx, p1 in enumerate(current_road):
        # If on the last point, stop because it cannot form a line
        if idx >= nr_current_segments - 1:
            break
        main_segment = [p1, current_road[idx + 1]]

        # Iterate through all leftover roads
        for other_road in other_roads:
            other_segments = other_road[1]
            nr_other_segments = len(other_segments)
            # Iterate through all of their segments
            for other_segment_idx, t_point0 in enumerate(other_road[1]):
                # If on the last point, stop because it cannot form a line
                if other_segment_idx >= nr_other_segments - 1:
                    break
                other_segment = [t_point0, other_segments[other_segment_idx + 1]]
                intersection = get_segment_intersection(main_segment, other_segment)
                if intersection != None:
                    intersections.append(intersection)
                processed_segments += 1
    d_queue.put([intersections, processed_segments])

print("Starting up...")
road_coords = unpack_csv(COORDS_FILE)
nr_roads = len(road_coords)
found_intersections = []

print("Checking if we have previous progress")
try:
    with open("ristmikud_raw.csv", "r") as in_file:
        temp = in_file.read().split("\n")
        for idx, line in enumerate(temp):
            if ";" in line:
                start_road, total_processed_segments = map(int, line.split(";"))
    print(f"Last saved progress was road nr: {start_road} on the segment nr: {total_processed_segments}")
except:
    total_processed_segments = 0
    start_road = 0


# Get number of all existing segments to start measuring progress
print("Enumerating segments...")
nr_segments = 0
for idx, road in enumerate(road_coords):
    nr_segments += len(road[1])

temp_sum = 0
for idx, road in enumerate(road_coords):
    if idx == start_road:
        break
    temp_sum += len(road[1])
    total_processed_segments += (nr_segments - temp_sum)

nr_segments = (nr_segments * (nr_segments - 1))/2

last_report_time = start_time = time.time()

road_index = start_road
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
currently_done_segments = 0
total_segments_left = nr_segments - total_processed_segments
while not done:
    if len(road_coords[road_index][1]) < 2:
        road_index += 1
        continue

    if road_index >= len(road_coords) - 1:
        done = True

    if stop:
        break

    # Clean up threads that have done their jobs and create new ones
    current_threads = [t for t in current_threads if t.is_alive()]
    while len(current_threads) < NR_THREADS:
        current_threads.append(multiprocessing.Process(target=process_road, args=(data_queue, road_coords[road_index:])))
        current_threads[-1].start()
        road_index += 1

    while not data_queue.empty():
        raw_data = data_queue.get()
        if raw_data != None and len(raw_data) == 2:
            intersections, segments = raw_data
        total_processed_segments += segments
        currently_done_segments += segments
        for intersection in intersections:
            found_intersections.append(intersection)

    last_report_time = print_logs_if_needed(last_report_time, road_index - len(current_threads), nr_roads, currently_done_segments, total_segments_left, start_time, len(found_intersections))
    time.sleep(0.1)

print("Waiting for threads to stop, might take a few minutes...")
while len(current_threads) > 0:
    current_threads = [t for t in current_threads if t.is_alive()]

while not data_queue.empty():
    raw_data = data_queue.get()
    if raw_data != None and len(raw_data) == 2:
        intersections, segments = raw_data
    total_processed_segments += segments
    for intersection in intersections:
        found_intersections.append(intersection)

if done:
    print("Intersections done, will convert them to writable string now...")
write_results_to_file(found_intersections, road_index, total_processed_segments)