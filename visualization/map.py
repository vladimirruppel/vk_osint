import os
from datetime import datetime
import folium
from folium.plugins import MarkerCluster


def build_map(geodata: list[dict], output_path: str = "output/map.html") -> str:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if not geodata:
        return ""

    center_lat = sum(p["lat"] for p in geodata) / len(geodata)
    center_lng = sum(p["lng"] for p in geodata) / len(geodata)

    m = folium.Map(location=[center_lat, center_lng], zoom_start=5, tiles="CartoDB dark_matter")
    cluster = MarkerCluster().add_to(m)

    for point in geodata:
        date_str = ""
        if point.get("date"):
            try:
                date_str = datetime.fromtimestamp(point["date"]).strftime("%Y-%m-%d")
            except Exception:
                pass

        popup_lines = [f"<b>{date_str}</b>"] if date_str else []
        if point.get("text"):
            popup_lines.append(point["text"][:200])
        if point.get("url"):
            popup_lines.append(f'<a href="{point["url"]}" target="_blank">Открыть фото</a>')

        popup_html = "<br>".join(popup_lines) if popup_lines else "Фото"

        folium.Marker(
            location=[point["lat"], point["lng"]],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="blue", icon="camera", prefix="fa"),
        ).add_to(cluster)

    m.save(output_path)
    return output_path
