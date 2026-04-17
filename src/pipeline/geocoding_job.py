from src.db.database import get_db_connection
from src.geocoder.extractor import LocationExtractor
from src.geocoder.geocoder_api import Geocoder
import time

def run_geocoding_batch(limit=None):
    print("Initializing Location Extractor (Loading Cache)...")
    extractor = LocationExtractor()
    geocoder = Geocoder()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query_str = "SELECT case_id, content FROM cases WHERE geocode_status='PENDING'"
        if limit:
            query_str += f" LIMIT {limit}"
        cursor.execute(query_str)
        pending_cases = cursor.fetchall()
        
    print(f"Found {len(pending_cases)} pending cases for geocoding.")
    
    stats = {'DONE_EXACT': 0, 'DONE_INTERSECTION': 0, 'DONE_LANDMARK': 0, 'MANUAL_REVIEW': 0}
    
    for pc in pending_cases:
        case_id = pc['case_id']
        content = pc['content']
        
        success = False
        
        # 0. Explicit Coordinates (Tier 0)
        coords = extractor.extract_coordinates(content)
        if coords:
            lat, lon = coords
            _update_db(case_id, "精確座標 (系統自帶)", lat, lon, 'DONE', 'EXACT')
            stats['DONE_EXACT'] += 1
            continue
        
        # 1. Intersection and Custom Landmark matching (Tier 1 & 1.5)
        intersections, custom_hits = extractor.extract_intersections(content)
        
        # 1.1 Check Custom/Learned Landmarks first (High priority)
        if custom_hits:
            for hit in custom_hits:
                lat, lon = geocoder.geocode_custom(hit)
                if lat and lon:
                    _update_db(case_id, f"{hit} (自定義學習)", lat, lon, 'DONE', 'LEARNED')
                    stats['DONE_LANDMARK'] += 1
                    success = True
                    break

        # 1.2 Intersection matching
        if not success and intersections:
            for intersect_key in intersections:
                lat, lon = geocoder.geocode_intersection(intersect_key)
                if lat and lon:
                    roads = intersect_key.split('_')
                    address = f"高雄市{roads[0]}與{roads[1]}路口"
                    _update_db(case_id, address, lat, lon, 'DONE', 'OFFLINE')
                    stats['DONE_INTERSECTION'] += 1
                    success = True
                    break
                
        # 2. Landmark regex matching (Tier 2)
        if not success:
            landmarks = extractor.extract_landmarks(content)
            if landmarks:
                for lm in landmarks:
                    lat, lon = geocoder.geocode_nominatim(lm)
                    if lat and lon:
                        _update_db(case_id, lm, lat, lon, 'DONE', 'API')
                        stats['DONE_LANDMARK'] += 1
                        success = True
                        time.sleep(1) # rate limiting nominatim
                        break
                    
        # 3. Fallback (Tier 3)
        if not success:
            _update_db(case_id, None, None, None, 'MANUAL_REVIEW_NEEDED', None)
            stats['MANUAL_REVIEW'] += 1

    print("Batch Geocoding Finished. Stats:", stats)
    return stats

def _update_db(case_id, address, lat, lon, status, source):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE cases SET address=?, latitude=?, longitude=?, geocode_status=?, geocode_source=?
        WHERE case_id=?
        ''', (address, lat, lon, status, source, case_id))
        conn.commit()

if __name__ == "__main__":
    run_geocoding_batch(limit=None)
