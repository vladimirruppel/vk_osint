from api.vk_client import VKClient


def collect_friends(client: VKClient, user_id: int, limit: int = 100) -> list[dict]:
    friends = client.get_friends(user_id, count=200)
    # Sort by those with most data available; take top `limit`
    return friends[:limit]


def collect_mutual_edges(
    client: VKClient, user_id: int, friends: list[dict]
) -> list[tuple[int, int]]:
    """Return list of (a, b) edges where friend a and friend b are mutually connected."""
    friend_ids = [f["id"] for f in friends]
    mutual = client.get_mutual_friends(user_id, friend_ids)

    edges = set()
    for fid, common in mutual.items():
        for cid in common:
            if cid in friend_ids:
                edge = tuple(sorted((fid, cid)))
                edges.add(edge)
    return list(edges)
