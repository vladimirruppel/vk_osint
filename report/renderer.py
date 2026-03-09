from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import BarColumn, Progress, TextColumn
from rich.rule import Rule
from rich import box

console = Console()


def _row(label: str, value: str, label_width: int = 18) -> None:
    if value and value.strip():
        console.print(f"  [dim]{label:<{label_width}}[/dim] {value}")


def _section(title: str) -> None:
    console.print(f"\n[bold yellow][{title}][/bold yellow]")


def print_header(title: str) -> None:
    console.print(Panel(f"[bold cyan]VK OSINT — {title}[/bold cyan]", expand=False))


def print_profile(profile: dict) -> None:
    uid = profile.get("id", "")
    screen = profile.get("screen_name", "")

    # ── Основное ──────────────────────────────────────────────
    _section("Профиль")
    _row("Имя", profile.get("name", ""))
    if profile.get("nickname"):
        _row("Отчество/псевдоним", profile["nickname"])
    _row("ID", str(uid))
    _row("Ссылка", f"https://vk.com/{screen}" if screen else "")
    _row("Пол", profile.get("sex", ""))
    _row("Дата рождения", profile.get("bdate", ""))
    _row("Родной город", profile.get("home_town", ""))
    _row("Город/страна", profile.get("location", ""))
    _row("Сайт", profile.get("site", ""))
    if profile.get("mobile_phone"):
        _row("Телефон (моб.)", profile["mobile_phone"])
    if profile.get("home_phone"):
        _row("Телефон (доп.)", profile["home_phone"])
    if profile.get("skype"):
        _row("Skype", profile["skype"])

    # ── Статус / О себе ───────────────────────────────────────
    if profile.get("status") or profile.get("about"):
        _section("Статус / О себе")
        _row("Статус", profile.get("status", ""))
        if profile.get("about"):
            console.print(f"  [dim]О себе[/dim]")
            for line in profile["about"].splitlines():
                console.print(f"    {line}")

    # ── Образование ───────────────────────────────────────────
    has_edu = profile.get("education") or profile.get("schools") or profile.get("occupation")
    if has_edu:
        _section("Образование / Работа")
        if profile.get("occupation"):
            _row("Текущее место", profile["occupation"])
        for line in profile.get("education", "").splitlines():
            _row("Вуз", line)
        for s in profile.get("schools", []):
            _row("Школа", s)

    # ── Карьера ───────────────────────────────────────────────
    if profile.get("career"):
        _section("Карьера")
        for c in profile["career"]:
            console.print(f"  • {c}")

    # ── Военная служба ────────────────────────────────────────
    if profile.get("military"):
        _section("Военная служба")
        for m in profile["military"]:
            console.print(f"  • {m}")

    # ── Личная жизнь ──────────────────────────────────────────
    has_personal = profile.get("relation") or profile.get("relatives")
    if has_personal:
        _section("Личная жизнь")
        _row("Семейное положение", profile.get("relation", ""))
        for r in profile.get("relatives", []):
            console.print(f"  • {r}")

    # ── Интересы ──────────────────────────────────────────────
    interest_fields = [
        ("Интересы", "interests"),
        ("Деятельность", "activities"),
        ("Музыка", "music"),
        ("Фильмы", "movies"),
        ("ТВ", "tv"),
        ("Книги", "books"),
        ("Игры", "games"),
        ("Цитаты", "quotes"),
    ]
    interest_data = [(label, profile.get(key, "")) for label, key in interest_fields if profile.get(key)]
    if interest_data:
        _section("Интересы")
        for label, value in interest_data:
            _row(label, value[:120] + ("…" if len(value) > 120 else ""))

    # ── Жизненная позиция ─────────────────────────────────────
    position_fields = [
        ("Политика", "political"),
        ("Мировоззрение", "religion"),
        ("Языки", "langs"),
        ("Главное в людях", "people_main"),
        ("Главное в жизни", "life_main"),
        ("Вдохновляет", "inspired_by"),
        ("Курение", "smoking"),
        ("Алкоголь", "alcohol"),
    ]
    position_data = [(label, profile.get(key, "")) for label, key in position_fields if profile.get(key)]
    if position_data:
        _section("Жизненная позиция")
        for label, value in position_data:
            _row(label, value)

    # ── Статистика ────────────────────────────────────────────
    _section("Статистика")
    _row("Подписчики", f"{profile.get('followers', 0):,}")
    _row("Онлайн", "Да" if profile.get("online") else "Нет")
    _row("Последний визит", profile.get("last_seen", ""))

    # ── Приватность ───────────────────────────────────────────
    _section("Приватность")
    _row("Закрытый профиль", "Да" if profile.get("is_closed") else "Нет")
    _row("Верифицирован", "Да" if profile.get("verified") else "Нет")
    _row("Скрыт от поиска", "Да" if profile.get("is_no_index") else "Нет")


def print_friends_summary(count: int, graph_path: str) -> None:
    _section("Друзья")
    with Progress(
        TextColumn("  "),
        BarColumn(bar_width=20),
        TextColumn(f"[green]{count} друзей"),
        transient=False,
        console=console,
    ) as progress:
        task = progress.add_task("", total=100)
        progress.update(task, completed=min(count, 100))
    if graph_path:
        console.print(f"  Граф сохранён: [link={graph_path}]{graph_path}[/link]")
    else:
        console.print("  Граф не построен (--no-graph)")


def print_groups(groups: list[dict]) -> None:
    console.print(f"\n[bold yellow][Группы][/bold yellow]  {len(groups)} сообществ")

    if not groups:
        console.print("  Нет данных (закрытый профиль или нет групп)")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("Название", style="white", max_width=50)
    table.add_column("Тип", style="dim")
    table.add_column("Участники", justify="right", style="green")

    for g in groups[:20]:
        members = f"{g['members_count']:,}" if g.get("members_count") else "—"
        table.add_row(g["name"], g["type"], members)

    console.print(table)


def print_geo_summary(count: int, map_path: str) -> None:
    _section("Геолокация")
    if count == 0:
        console.print("  Фото с координатами не найдено")
        return
    console.print(f"  {count} фото с координатами")
    if map_path:
        console.print(f"  Карта сохранена: [link={map_path}]{map_path}[/link]")
    else:
        console.print("  Карта не построена (--no-map)")


def print_search_results(results: list[dict], query: str) -> None:
    console.print(Panel(f"[bold cyan]Поиск: {query}[/bold cyan]", expand=False))
    console.print(f"  Найдено результатов: [green]{len(results)}[/green]\n")

    if not results:
        console.print("  Ничего не найдено.")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Имя", style="white", min_width=20)
    table.add_column("Screen name", style="cyan")
    table.add_column("Город", style="dim")
    table.add_column("Образование", style="dim", max_width=30)
    table.add_column("Открытый", justify="center")

    for u in results:
        locked = "[green]✓[/green]" if not u.get("is_closed") else "[red]✗[/red]"
        table.add_row(
            str(u["id"]),
            u["name"],
            f"@{u['screen_name']}" if u.get("screen_name") else "",
            u.get("city", ""),
            u.get("education", ""),
            locked,
        )

    console.print(table)


def print_error(message: str) -> None:
    console.print(f"[bold red]Ошибка:[/bold red] {message}")
