from api.vk_client import VKClient


def collect_groups(client: VKClient, user_id: int) -> list[dict]:
    groups = client.get_groups(user_id)
    return [
        {
            "id": g.get("id"),
            "name": g.get("name", ""),
            "screen_name": g.get("screen_name", ""),
            "type": g.get("type", ""),
            "members_count": g.get("members_count", 0),
        }
        for g in groups
    ]
