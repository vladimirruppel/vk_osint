from api.vk_client import VKClient


def search_users(client: VKClient, query: str, city_id: int = 0, count: int = 20) -> list[dict]:
    raw = client.search_users(query, city_id=city_id, count=count)
    result = []
    for u in raw:
        city = u.get("city", {}).get("title", "") if u.get("city") else ""
        edu = u.get("university_name", "")
        result.append(
            {
                "id": u.get("id"),
                "name": f"{u.get('first_name', '')} {u.get('last_name', '')}".strip(),
                "screen_name": u.get("screen_name", ""),
                "bdate": u.get("bdate", ""),
                "city": city,
                "education": edu,
                "is_closed": u.get("is_closed", False),
                "photo_50": u.get("photo_50", ""),
            }
        )
    return result
