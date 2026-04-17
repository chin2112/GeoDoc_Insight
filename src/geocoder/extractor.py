import ahocorasick
import re
from src.db.database import get_db_connection

class LocationExtractor:
    def __init__(self):
        self.automaton = None
        self._load_dictionary()

    def _load_dictionary(self):
        self.automaton = ahocorasick.Automaton()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 1. Load standard roads
            cursor.execute("SELECT road_name FROM osm_roads")
            for row in cursor.fetchall():
                road = row['road_name']
                if len(road) > 1:
                    self.automaton.add_word(road, ('ROAD', road))
            
            # 2. Load custom landmarks (Learned patterns)
            cursor.execute("SELECT name FROM custom_landmarks")
            for row in cursor.fetchall():
                name = row['name']
                self.automaton.add_word(name, ('LANDMARK', name))
                    
        try:
            self.automaton.make_automaton()
        except:
            pass

    def extract_intersections(self, text):
        if not text or not self.automaton:
            return []
            
        found_entities = []
        for end_idx, value in self.automaton.iter(text):
            etype, name = value
            start_idx = end_idx - len(name) + 1
            found_entities.append({'type': etype, 'name': name, 'start': start_idx, 'end': end_idx})
        
        # Sort and deduplicate overlapping matches
        found_entities.sort(key=lambda x: x['start'])
        filtered = []
        for r in found_entities:
            overlap = False
            for i in range(len(filtered)):
                f = filtered[i]
                if not (r['end'] < f['start'] or r['start'] > f['end']):
                    overlap = True
                    if len(r['name']) > len(f['name']):
                        filtered[i] = r
                    break
            if not overlap:
                filtered.append(r)
        
        # Split into roads and custom landmarks
        roads = [f for f in filtered if f['type'] == 'ROAD']
        custom_hits = [f['name'] for f in filtered if f['type'] == 'LANDMARK']
        
        # Find adjacent roads for intersections
        intersections = []
        for i in range(len(roads)):
            for j in range(i+1, len(roads)):
                if roads[j]['start'] - roads[i]['end'] <= 10:
                    if roads[i]['name'] != roads[j]['name']:
                        pair = sorted([roads[i]['name'], roads[j]['name']])
                        intersections.append(f"{pair[0]}_{pair[1]}")
                        
        return list(set(intersections)), list(set(custom_hits))

    def extract_landmarks(self, text):
        if not text:
            return []
        # Regex for schools, stations, hospitals, airports, etc.
        pattern = r"([\u4e00-\u9fa5]{2,6}(國小|國中|高中|大學|醫院|公園|火車站|捷運站|市場|機場|轉運站|交流道|圓環))"
        matches = re.findall(pattern, text)
        return [m[0] for m in matches]

    def extract_coordinates(self, text):
        if not text:
            return None
        # Match explicit coordinates provided in the text, e.g. 通報位置(lat,lng)：(22.6211,120.3458)
        pattern = r"\(lat,lng\).*?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)"
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return float(matches.group(1)), float(matches.group(2))
        return None
