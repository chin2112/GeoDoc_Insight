import requests
import urllib.parse
from src.db.database import get_db_connection

class Geocoder:
    def geocode_intersection(self, intersection_key):
        """
        Geocode using offline lookup table for instant result.
        Returns: (lat, lon) or (None, None)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT latitude, longitude FROM osm_intersections WHERE road_pair=?", (intersection_key,))
            res = cursor.fetchone()
            if res:
                return float(res['latitude']), float(res['longitude'])
        return None, None

    def geocode_custom(self, landmark_name):
        """
        Geocode using the 'Learned' custom landmarks table.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT latitude, longitude FROM custom_landmarks WHERE name=?", (landmark_name,))
            res = cursor.fetchone()
            if res:
                return float(res['latitude']), float(res['longitude'])
        return None, None

    def geocode_nominatim(self, location_str):
        """
        Fallback geocoding using free Nominatim API.
        Returns: (lat, lon) or (None, None)
        """
        query = urllib.parse.quote(f"高雄市 {location_str}")
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        try:
            # Comply with nominatim TOS
            headers = {"User-Agent": "GeoDocInsight_Kaohsiung_Mapping/1.0"} 
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and len(res.json()) > 0:
                data = res.json()[0]
                return float(data['lat']), float(data['lon'])
        except Exception as e:
            print(f"Nominatim lookup failed for {location_str}: {e}")
            
        return None, None
