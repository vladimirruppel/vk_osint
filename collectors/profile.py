from api.vk_client import VKClient

_RELATION = {
    0: "",
    1: "не женат/не замужем",
    2: "есть друг/подруга",
    3: "помолвлен/а",
    4: "женат/замужем",
    5: "всё сложно",
    6: "в активном поиске",
    7: "влюблён/а",
    8: "в гражданском браке",
}

_SEX = {0: "", 1: "женский", 2: "мужской"}

_PLATFORM = {
    1: "мобильная версия",
    2: "iPhone",
    3: "iPad",
    4: "Android",
    5: "Windows Phone",
    6: "Windows 10",
    7: "веб",
}

_POLITICAL = {
    1: "коммунистические", 2: "социалистические", 3: "умеренные",
    4: "либеральные", 5: "консервативные", 6: "монархические",
    7: "ультраконсервативные", 8: "индифферентные", 9: "либертарианские",
}

_PEOPLE_MAIN = {
    1: "ум и креативность", 2: "доброта и честность", 3: "красота и здоровье",
    4: "власть и богатство", 5: "смелость и упорство", 6: "юмор и жизнелюбие",
}

_LIFE_MAIN = {
    1: "семья и дети", 2: "карьера и деньги", 3: "развлечения и отдых",
    4: "наука и исследования", 5: "совершенствование мира",
    6: "саморазвитие", 7: "красота и искусство", 8: "слава и влияние",
}

_ATTITUDE = {
    1: "резко негативное", 2: "негативное", 3: "компромиссное",
    4: "нейтральное", 5: "положительное",
}

_RELATIVE_TYPE = {
    "child": "сын/дочь", "sibling": "брат/сестра", "parent": "отец/мать",
    "grandparent": "дедушка/бабушка", "grandchild": "внук/внучка",
}


def collect_profile(client: VKClient, user_id: str) -> dict:
    return client.get_user(user_id)


def format_profile(profile: dict) -> dict:
    from datetime import datetime

    name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()

    city = profile.get("city", {}).get("title", "") if profile.get("city") else ""
    country = profile.get("country", {}).get("title", "") if profile.get("country") else ""
    location_parts = [p for p in [city, country] if p]
    location = ", ".join(location_parts)

    # Education: primary (education fields) + universities list
    edu_parts = []
    if profile.get("university_name"):
        u = profile["university_name"]
        if profile.get("faculty_name"):
            u += f", {profile['faculty_name']}"
        if profile.get("graduation"):
            u += f", {profile['graduation']}"
        edu_parts.append(u)
    for u in profile.get("universities", []):
        parts = [u.get("name", "")]
        if u.get("faculty_name"):
            parts.append(u["faculty_name"])
        if u.get("chair_name"):
            parts.append(u["chair_name"])
        if u.get("graduation"):
            parts.append(str(u["graduation"]))
        if u.get("education_form"):
            parts.append(u["education_form"])
        line = ", ".join(p for p in parts if p)
        if line and line not in edu_parts:
            edu_parts.append(line)

    schools = []
    for s in profile.get("schools", []):
        parts = [s.get("name", "")]
        if s.get("year_from") and s.get("year_to"):
            parts.append(f"{s['year_from']}–{s['year_to']}")
        elif s.get("year_graduated"):
            parts.append(str(s["year_graduated"]))
        if s.get("type_str"):
            parts.insert(0, s["type_str"])
        line = ", ".join(p for p in parts if p)
        if line:
            schools.append(line)

    career = []
    for c in profile.get("career", []):
        company = c.get("company", "")
        position = c.get("position", "")
        city_name = c.get("city_name", "")
        year_from = c.get("from", "")
        year_to = c.get("until", "")
        period = ""
        if year_from and year_to:
            period = f"{year_from}–{year_to}"
        elif year_from:
            period = f"с {year_from}"
        parts = [p for p in [company, position, city_name, period] if p]
        if parts:
            career.append(", ".join(parts))

    military = []
    for m in profile.get("military", []):
        unit = m.get("unit", "")
        year_from = m.get("from", "")
        year_to = m.get("until", "")
        period = f"{year_from}–{year_to}" if year_from and year_to else ""
        parts = [p for p in [unit, period] if p]
        if parts:
            military.append(", ".join(parts))

    relatives = []
    for r in profile.get("relatives", []):
        rtype = _RELATIVE_TYPE.get(r.get("type", ""), r.get("type", ""))
        rname = r.get("name", "")
        if not rname and r.get("id"):
            rname = f"id{r['id']}"
        if rname:
            relatives.append(f"{rname} ({rtype})")

    last_seen_str = ""
    if profile.get("last_seen"):
        ts = profile["last_seen"].get("time", 0)
        platform = profile["last_seen"].get("platform", 0)
        if ts:
            dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
            plat = _PLATFORM.get(platform, "")
            last_seen_str = f"{dt}" + (f" [{plat}]" if plat else "")

    contacts = profile.get("contacts", {}) or {}
    personal = profile.get("personal", {}) or {}

    occupation = ""
    if profile.get("occupation"):
        occ = profile["occupation"]
        occupation = occ.get("name", "")

    return {
        "id": profile.get("id"),
        "name": name,
        "nickname": profile.get("nickname", ""),
        "screen_name": profile.get("screen_name", ""),
        "domain": profile.get("domain", ""),
        "sex": _SEX.get(profile.get("sex", 0), ""),
        "bdate": profile.get("bdate", ""),
        "home_town": profile.get("home_town", ""),
        "location": location,
        "site": profile.get("site", ""),
        "status": profile.get("status", ""),
        "about": profile.get("about", ""),
        "occupation": occupation,
        "education": "\n".join(edu_parts),
        "schools": schools,
        "career": career,
        "military": military,
        "followers": profile.get("followers_count", 0),
        "relation": _RELATION.get(profile.get("relation", 0), ""),
        "relatives": relatives,
        "interests": profile.get("interests", ""),
        "activities": profile.get("activities", ""),
        "music": profile.get("music", ""),
        "movies": profile.get("movies", ""),
        "tv": profile.get("tv", ""),
        "books": profile.get("books", ""),
        "games": profile.get("games", ""),
        "quotes": profile.get("quotes", ""),
        "political": _POLITICAL.get(personal.get("political", 0), ""),
        "religion": personal.get("religion", ""),
        "langs": ", ".join(personal.get("langs", [])) if personal.get("langs") else "",
        "people_main": _PEOPLE_MAIN.get(personal.get("people_main", 0), ""),
        "life_main": _LIFE_MAIN.get(personal.get("life_main", 0), ""),
        "smoking": _ATTITUDE.get(personal.get("smoking", 0), ""),
        "alcohol": _ATTITUDE.get(personal.get("alcohol", 0), ""),
        "inspired_by": personal.get("inspired_by", ""),
        "mobile_phone": contacts.get("mobile_phone", ""),
        "home_phone": contacts.get("home_phone", ""),
        "skype": profile.get("skype", ""),
        "last_seen": last_seen_str,
        "online": bool(profile.get("online", 0)),
        "verified": bool(profile.get("verified", 0)),
        "is_closed": profile.get("is_closed", False),
        "is_no_index": bool(profile.get("is_no_index", 0)),
        "photo_200": profile.get("photo_200", ""),
    }
