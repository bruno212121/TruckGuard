from app.models import TripModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


def parse_distance_km(distance_text: str) -> float:
    """
    Acepta '25.3 km', '25 km', '25340 m', '15 mi' y devuelve km.
    """
    if not distance_text:
        return 0.0
    t = distance_text.strip().lower().replace(',', '.')
    if t.endswith('km'):
        return float(t.replace('km', '').strip())
    if t.endswith('m'):
        m = float(t.replace('m', '').strip())
        return m / 1000.0
    if t.endswith('mi'):
        mi = float(t.replace('mi', '').strip())
        return mi * 1.609344
    # último recurso: solo número
    try:
        return float(t)
    except:
        return 0.0


class GoogleGetLocation:

    """
    async def get_location(self, address: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
            )
            response.raise_for_status()
            data = response.json()

            # Converti a un json de latitud y longitud
            location = data["results"][0]["geometry"]["location"]
            return location
    """

    async def get_distance(self, origin: str, destination: str) -> dict:
        params = {
            "origins": origin,
            "destinations": destination,
            "key": API_KEY
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
            r.raise_for_status()
            data = r.json()

        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return {"error": "could not get distance"}

        # NUMÉRICO: metros y segundos
        distance_m = float(element["distance"]["value"])   # e.g. 25340.0
        duration_s = float(element["duration"]["value"])   # e.g. 1860.0
        distance_km = distance_m / 1000.0

        return {"distance_km": distance_km, "duration_min": duration_s / 60.0}
        
