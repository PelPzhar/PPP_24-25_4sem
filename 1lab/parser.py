import re

def parse_sql(query):
    query = query.strip()
    select_pattern = r"SELECT\s+\*\s+FROM\s+(\w+)(?:\s+WHERE\s+(\w+)\s*([=<>!]+)\s*['\"]?([^'\"]+)['\"]?)?$"
    match = re.match(select_pattern, query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid SELECT query")

    table = match.group(1)
    result = {"type": "SELECT", "table": table}
    if match.group(2) and match.group(3) and match.group(4):
        result["where"] = (match.group(2), match.group(3), match.group(4))
    print(f"Parsed query: {result}")  # Отладка
    return result