import ast
import time
import signal
import sys

COORDS_FILE = "tee_koordinaadid.csv"
REPORT_TIME = 5

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
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def line_coefficients(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    
    return slope, intercept

def find_intersection_point(line1, line2):
    m1, b1 = line_coefficients(line1[0], line1[1])
    m2, b2 = line_coefficients(line2[0], line2[1])
    
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
    print("-------------------------------------------------")
    print(f"Nr of roads processed: {nr_roads_done}/{nr_roads}")
    print(f"Nr of intersections found: {nr_found}")
    print(f"Overall progress: {progress*100}%")
    print(f"Time taken: {time_taken}s")
    print(f"Estimated time left: {((1/progress)*time_taken)-time_taken}s")
    print("-------------------------------------------------\n")
    return time.time()

def write_results_to_file(intersections, road_nr):
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
    out_string += f"{road_nr};\n"

    with open("ristmikud_raw.csv", "w") as out_file:
        out_file.write(out_string)
        out_file.close()

    print("Goooooodbyeeeeeeeeeeee!")
    sys.exit(0)

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
                start_road = int(line.split(";")[0])
    print(f"Last saved progress was road nr: {start_road}")
except:
    start_road = 0


# Get number of all existing segments to start measuring progress
print("Enumerating segments...")
nr_segments = 0
processed_segments = 0
for idx, road in enumerate(road_coords):
    nr_segments += len(road[1])

temp_sum = 0
for idx, road in enumerate(road_coords):
    temp_sum += len(road[1])
    processed_segments += (nr_segments - temp_sum)
    if idx == start_road:
        break

nr_segments = (nr_segments**2)/2

last_report_time = start_time = time.time()

idx = 0
def stop(sig, frame):
    global idx, start_road, found_intersections
    write_results_to_file(found_intersections, start_road + idx)

print("Starting to find intersections...")
signal.signal(signal.SIGINT, stop)
# Iterate through all of the roads
done = False
for idx, road in enumerate(road_coords[start_road:]):
    if len(road[1]) < 2:
        continue
    # Last road, it can't collide with itself ;)
    if start_road + idx == len(road_coords):
        continue

    # Iterate through every segment in every road
    for f_point in range(len(road[1])):
        if f_point >= len(road[1]) - 1:
            break
        last_report_time = print_logs_if_needed(last_report_time, start_road+idx, nr_roads, processed_segments, nr_segments, start_time, len(found_intersections))
        main_segment = [road[1][f_point], road[1][f_point+1]]

        # Iterate through all leftover roads
        for other_road in road_coords[start_road+idx+1:]:
            # Iterate through all of their segments
            for target_segment_id in range(len(other_road[1])):
                if target_segment_id >= len(other_road[1]) - 1:
                    break
                other_segment = [other_road[1][target_segment_id], other_road[1][target_segment_id+1]]
                juust = get_segment_intersection(main_segment, other_segment)
                if juust != None:
                    found_intersections.append(juust)
                processed_segments += 1
done = True
    

if done:
    print("Intersections done, will convert them to writable string now...")
write_results_to_file(found_intersections, start_road + idx)