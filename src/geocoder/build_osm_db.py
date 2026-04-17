import requests
import json
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')

def fetch_kaohsiung_osm():
    print("Fetching Kaohsiung named highways from OSM Overpass API...")
    # Bounding box roughly covering Kaohsiung and surrounding populated areas
    # (min_lat, min_lon, max_lat, max_lon)
    query = """
    [out:json][timeout:300][bbox:22.45, 120.15, 23.0, 120.6];
    (
      way["highway"]["name"];
    );
    out body;
    >;
    out skel qt;
    """
    
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]
    
    for url in overpass_urls:
        print(f"Trying {url}...")
        try:
            response = requests.post(url, data={'data': query}, timeout=120)
            if response.status_code == 200:
                print("Success.")
                return response.json()
        except:
            continue
            
    raise Exception("All Overpass API endpoints failed or timed out.")

def process_intersections(osm_data):
    print("Processing OSM data for intersections...")
    elements = osm_data.get('elements', [])
    
    # Dictionaries to hold our parsed graph
    nodes = {} # node_id -> {lat, lon}
    node_to_ways = {} # node_id -> set of way_names
    
    # First pass: Extract nodes and way-nodes
    for el in elements:
        if el['type'] == 'node':
            nodes[el['id']] = {'lat': el['lat'], 'lon': el['lon']}
            
    for el in elements:
        if el['type'] == 'way':
            name = el['tags'].get('name')
            if not name:
                continue
            for nid in el['nodes']:
                if nid not in node_to_ways:
                    node_to_ways[nid] = set()
                node_to_ways[nid].add(name)
                
    # Second pass: Find intersections
    intersections = {} # 'RoadA_RoadB' -> (sum_lat, sum_lon, count)
    
    for nid, ways in node_to_ways.items():
        if len(ways) >= 2:
            # This node connects 2 or more DIFFERENT named roads
            way_list = sorted(list(ways))
            # Generate all pairs of intersections at this node
            for i in range(len(way_list)):
                for j in range(i+1, len(way_list)):
                    pair_key = f"{way_list[i]}_{way_list[j]}"
                    node_info = nodes.get(nid)
                    if node_info:
                        if pair_key not in intersections:
                            intersections[pair_key] = [0.0, 0.0, 0]
                        intersections[pair_key][0] += node_info['lat']
                        intersections[pair_key][1] += node_info['lon']
                        intersections[pair_key][2] += 1
                        
    # Average the coordinates for each intersection pair
    final_intersections = {}
    for pair, stats in intersections.items():
        final_intersections[pair] = {
            'lat': stats[0] / stats[2],
            'lon': stats[1] / stats[2]
        }
        
    # Also we want a set of all standardized Kaohsiung road names
    road_names = set()
    for el in elements:
        if el['type'] == 'way':
            name = el['tags'].get('name')
            if name:
                road_names.add(name)
                
    return final_intersections, list(road_names)

def save_to_db(intersections, road_names):
    print("Saving to geodoc.db...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS osm_intersections (
            road_pair TEXT PRIMARY KEY,
            road_a TEXT,
            road_b TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS osm_roads (
            road_name TEXT PRIMARY KEY
        )
    ''')
    
    # Clean previous data to allow fresh rebuilds
    cursor.execute('DELETE FROM osm_intersections')
    cursor.execute('DELETE FROM osm_roads')
    
    intersection_records = []
    for pair, coords in intersections.items():
        roads = pair.split('_')
        intersection_records.append((pair, roads[0], roads[1], coords['lat'], coords['lon']))
        
    cursor.executemany('INSERT INTO osm_intersections VALUES (?, ?, ?, ?, ?)', intersection_records)
    
    road_records = [(r,) for r in road_names]
    cursor.executemany('INSERT INTO osm_roads VALUES (?)', road_records)
    
    conn.commit()
    conn.close()
    
    print(f"Successfully saved {len(intersection_records)} unique intersections and {len(road_records)} road names.")

if __name__ == "__main__":
    t0 = time.time()
    try:
        osm_data = fetch_kaohsiung_osm()
        intersections, road_names = process_intersections(osm_data)
        save_to_db(intersections, road_names)
        print(f"Total time: {time.time()-t0:.2f} seconds")
    except Exception as e:
        print(f"Error building OSM DB: {e}")
