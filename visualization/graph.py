import os
import networkx as nx
from pyvis.network import Network


def build_graph(
    target: dict,
    friends: list[dict],
    edges: list[tuple[int, int]],
    output_path: str = "output/graph.html",
) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    G = nx.Graph()

    target_id = target["id"]
    target_label = target.get("name", str(target_id))
    G.add_node(target_id, label=target_label, color="red", size=30, title=target_label)

    friend_ids = {f["id"] for f in friends}

    # Count how many mutual connections each friend has (degree in subgraph)
    degree: dict[int, int] = {f["id"]: 0 for f in friends}
    for a, b in edges:
        if a in degree:
            degree[a] += 1
        if b in degree:
            degree[b] += 1

    for f in friends:
        fid = f["id"]
        label = f"{f.get('first_name', '')} {f.get('last_name', '')}".strip()
        size = 10 + min(degree.get(fid, 0), 20)
        city = f.get("city", {}).get("title", "") if f.get("city") else ""
        title = label + (f"\n{city}" if city else "")
        url = f"https://vk.com/id{fid}"
        G.add_node(fid, label=label, color="#4a90d9", size=size, title=title, url=url)
        G.add_edge(target_id, fid)

    for a, b in edges:
        if a in friend_ids and b in friend_ids:
            G.add_edge(a, b)

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="white",
        notebook=False,
    )
    net.from_nx(G)
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=150,
        spring_strength=0.001,
        damping=0.09,
    )
    net.show_buttons(filter_=["physics"])

    # Make nodes clickable
    net.html = net.html  # trigger generation
    net.save_graph(output_path)

    _inject_click_handler(output_path)

    return output_path


def _inject_click_handler(path: str) -> None:
    """Inject JS so clicking a node opens VK profile."""
    click_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    if (typeof network !== 'undefined') {
      network.on('click', function(params) {
        if (params.nodes.length > 0) {
          var nodeId = params.nodes[0];
          var node = network.body.data.nodes.get(nodeId);
          if (node && node.url) {
            window.open(node.url, '_blank');
          }
        }
      });
    }
  }, 1000);
});
</script>
"""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if "</body>" in html:
        html = html.replace("</body>", click_js + "</body>")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
