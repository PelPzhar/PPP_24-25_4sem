import aiohttp
from bs4 import BeautifulSoup
import networkx as nx
from urllib.parse import urljoin, urlparse
from redis import Redis
from app.core.config import settings
import json
from pyvis.network import Network

redis_client = Redis.from_url(settings.REDIS_URL)

async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                return await response.text()
            return None
    except Exception:
        return None

async def parse_page(url, depth=0, max_depth=2, max_pages=100, visited=None, graph=None):
    if visited is None:
        visited = set()
    if graph is None:
        graph = nx.DiGraph()

    if depth > max_depth or len(visited) >= max_pages or url in visited:
        return graph

    visited.add(url)
    graph.add_node(url)

    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, url)
        if not html:
            return graph

        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            parsed_url = urlparse(absolute_url)
            if parsed_url.scheme in ('http', 'https') and parsed_url.netloc == urlparse(url).netloc:
                graph.add_edge(url, absolute_url)
                if absolute_url not in visited:
                    await parse_page(absolute_url, depth + 1, max_depth, max_pages, visited, graph)

    return graph

async def parse_and_store_graph(start_url, user_id):
    graph = await parse_page(start_url)
    graph_data = {
        "nodes": list(graph.nodes),
        "edges": list(graph.edges)
    }

    # Генерация визуализации с помощью pyvis
    net = Network(directed=True)
    for node in graph.nodes:
        net.add_node(node, label=node)
    for edge in graph.edges:
        net.add_edge(edge[0], edge[1])

    # Сохраняем граф как HTML-строку
    html_graph = net.generate_html()

    # Сохраняем данные и визуализацию в Redis
    redis_key_data = f"graph:data:{user_id}:{start_url}"
    redis_key_html = f"graph:html:{user_id}:{start_url}"
    redis_client.setex(redis_key_data, 3600, json.dumps(graph_data))  # Храним данные 1 час
    redis_client.setex(redis_key_html, 3600, html_graph)  # Храним HTML 1 час

    return graph_data, html_graph