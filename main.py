#!/usr/bin/env python3
"""VK OSINT Tool — автоматизация сбора открытых данных через VK API."""

import argparse
import sys
import os
import re
from datetime import datetime

# Ensure project root is on path when run directly
sys.path.insert(0, os.path.dirname(__file__))

from api.vk_client import VKClient
from collectors.profile import collect_profile, format_profile
from collectors.friends import collect_friends, collect_mutual_edges
from collectors.groups import collect_groups
from collectors.geo import collect_geodata
from collectors.search import search_users
from visualization.graph import build_graph
from visualization.map import build_map
from report.renderer import (
    console,
    print_header,
    print_profile,
    print_friends_summary,
    print_groups,
    print_geo_summary,
    print_search_results,
    print_error,
)


def _make_output_dir(slug: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^\w\-]", "_", slug)
    out_dir = os.path.join(os.path.dirname(__file__), "output", f"{safe}_{ts}")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def run_user_mode(client: VKClient, args: argparse.Namespace) -> None:
    user_arg = args.user

    raw_profile = collect_profile(client, user_arg)
    if not raw_profile:
        print_error(f"Пользователь '{user_arg}' не найден.")
        sys.exit(1)

    profile = format_profile(raw_profile)
    user_id: int = profile["id"]
    slug = profile.get("screen_name") or str(user_id)
    display = f"@{slug}" if profile.get("screen_name") else profile["name"]
    out_dir = _make_output_dir(slug)

    print_header(display)
    print_profile(profile)

    # --- Friends + Graph ---
    graph_path = ""
    friends = []
    if not args.no_graph:
        friends = collect_friends(client, user_id, limit=100)

        if friends:
            if args.depth >= 2:
                extra_friends: list[dict] = []
                for f in friends[:10]:
                    sub = collect_friends(client, f["id"], limit=20)
                    extra_friends.extend(sub)
                seen = {f["id"] for f in friends}
                for f in extra_friends:
                    if f["id"] not in seen:
                        friends.append(f)
                        seen.add(f["id"])

            edges = collect_mutual_edges(client, user_id, friends)
            graph_path = build_graph(
                raw_profile | {"name": profile["name"]},
                friends,
                edges,
                output_path=os.path.join(out_dir, "graph.html"),
            )

    print_friends_summary(len(friends), graph_path)

    # --- Groups ---
    groups = collect_groups(client, user_id)
    print_groups(groups)

    # --- Geo / Map ---
    map_path = ""
    geo = []
    if not args.no_map:
        geo = collect_geodata(client, user_id)
        if geo:
            map_path = build_map(geo, output_path=os.path.join(out_dir, "map.html"))
    print_geo_summary(len(geo), map_path)


def run_search_mode(client: VKClient, args: argparse.Namespace) -> None:
    city_id = 0
    # Simple city name → id mapping for most common cities
    CITY_IDS = {
        "москва": 1,
        "санкт-петербург": 2,
        "спб": 2,
        "екатеринбург": 9,
        "новосибирск": 11,
        "казань": 43,
    }
    if args.city:
        city_id = CITY_IDS.get(args.city.lower(), 0)

    results = search_users(client, args.search, city_id=city_id, count=args.count)
    print_search_results(results, args.search)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VK OSINT Tool — сбор открытых данных о пользователях VK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main.py --user durov
  python main.py --user 1 --no-map
  python main.py --search "Павел Дуров"
  python main.py --search "Иван Иванов" --city Москва --count 30
  python main.py --user durov --depth 2
""",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--user", metavar="ID|USERNAME", help="ID или screen_name пользователя")
    mode.add_argument("--search", metavar="ФИО", help="Поиск пользователей по имени")

    parser.add_argument("--no-graph", action="store_true", help="Не строить граф друзей")
    parser.add_argument("--no-map", action="store_true", help="Не строить карту геолокаций")
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        choices=[1, 2],
        help="Глубина графа: 1 = только друзья (default), 2 = друзья друзей (медленно)",
    )
    parser.add_argument("--city", metavar="ГОРОД", help="Фильтр по городу для --search")
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Количество результатов для --search (default: 20)",
    )

    args = parser.parse_args()

    try:
        client = VKClient()
    except EnvironmentError as e:
        console.print(f"[bold red]{e}[/bold red]")
        sys.exit(1)

    try:
        if args.user:
            run_user_mode(client, args)
        else:
            run_search_mode(client, args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Прервано пользователем.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
