from typing import List


def detect_circular_transactions(transactions: list) -> bool:
    """Detect circular transaction patterns within a 24-hour window.

    Each transaction is a dict with keys:
        from (str), to (str), amount (float), timestamp (float, UNIX epoch)

    Returns True if the directed graph of recent (±24h), amount-similar (±10%)
    transaction pairs contains a cycle.
    """
    ONE_DAY = 86400

    # Build edges: include an edge (tx_a) if there exists another tx_b where
    # |tx_a.timestamp - tx_b.timestamp| < 86400 AND amounts are within ±10%.
    # Then build the adjacency list from all such edges.
    edges = []
    n = len(transactions)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            tx_a = transactions[i]
            tx_b = transactions[j]
            amt_a = float(tx_a.get("amount", 0))
            amt_b = float(tx_b.get("amount", 0))
            ts_a = float(tx_a.get("timestamp", 0))
            ts_b = float(tx_b.get("timestamp", 0))
            if abs(ts_a - ts_b) < ONE_DAY and amt_b > 0:
                if abs(amt_a - amt_b) / amt_b <= 0.10:
                    edges.append((tx_a.get("from", ""), tx_a.get("to", "")))
                    break  # edge already added for tx_a

    # Build adjacency list
    graph: dict = {}
    for src, dst in edges:
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)

    # DFS cycle detection
    visited: set = set()
    visiting: set = set()

    def dfs(node: str) -> bool:
        visiting.add(node)
        for neighbour in graph.get(node, []):
            if neighbour in visiting:
                return True
            if neighbour not in visited:
                if dfs(neighbour):
                    return True
        visiting.discard(node)
        visited.add(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            if dfs(node):
                return True

    return False


def compute_trend_score(balances: List[float]) -> float:
    """Return a normalised trend score in [-1, 1] using linear regression slope.

    Uses the direct formula:
        slope = (n*sum(i*b) - sum(i)*sum(b)) / (n*sum(i^2) - sum(i)^2)

    Normalised by dividing by max(abs(balances)) so that the result is bounded.
    Returns 0.0 when fewer than 2 data points or when all balances are zero.
    """
    n = len(balances)
    if n < 2:
        return 0.0

    indices = list(range(n))
    sum_i = sum(indices)
    sum_b = sum(balances)
    sum_ib = sum(i * b for i, b in zip(indices, balances))
    sum_i2 = sum(i * i for i in indices)

    denom = n * sum_i2 - sum_i ** 2
    if denom == 0:
        return 0.0

    slope = (n * sum_ib - sum_i * sum_b) / denom

    max_abs = max(abs(b) for b in balances)
    if max_abs == 0:
        return 0.0

    return max(-1.0, min(1.0, slope / max_abs))
