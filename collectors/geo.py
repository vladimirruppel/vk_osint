from api.vk_client import VKClient


def collect_geodata(client: VKClient, user_id: int) -> list[dict]:
    photos = client.get_photos_with_geo(user_id)
    return [
        {
            "lat": p["lat"],
            "lng": p["long"],
            "date": p.get("date", 0),
            "url": _best_url(p),
            "text": p.get("text", ""),
        }
        for p in photos
    ]


def _best_url(photo: dict) -> str:
    for size in ("photo_604", "photo_130", "photo_75"):
        if photo.get(size):
            return photo[size]
    return ""
