"""演化图谱构建节点

将实体和关系组装为 JSON 格式的演化图谱，识别演化路径。
"""

from __future__ import annotations

from collections import defaultdict

from langchain_core.messages import HumanMessage

from evomap_src.models import EvoMapState, KnowledgeEntity, EntityRelation


def _build_adjacency(
    entities: list[KnowledgeEntity],
    relations: list[EntityRelation],
) -> dict:
    """构建邻接表表示的图结构"""
    entity_map = {e.id: e.model_dump() for e in entities}
    adj: dict[str, list[dict]] = defaultdict(list)

    for r in relations:
        adj[r.source_id].append({
            "target": r.target_id,
            "type": r.relation_type,
            "strength": r.strength,
            "description": r.description,
        })

    return entity_map, dict(adj)


def _find_evolution_chains(
    entities: list[KnowledgeEntity],
    relations: list[EntityRelation],
) -> list[list[str]]:
    """找出演化链（从没有入边的节点出发的最长路径）"""
    entity_ids = {e.id for e in entities}
    has_incoming = {r.target_id for r in relations if r.target_id in entity_ids}
    roots = entity_ids - has_incoming
    if not roots:
        roots = entity_ids

    children: dict[str, list[str]] = defaultdict(list)
    for r in relations:
        if r.relation_type in ("inherits", "derives", "replaces"):
            children[r.source_id].append(r.target_id)

    chains: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        if node not in children or not children[node]:
            if len(path) >= 2:
                chains.append(list(path))
            return
        for child in children[node]:
            if child not in path:
                path.append(child)
                dfs(child, path)
                path.pop()
        if not any(c in set(path) - {node} for c in children[node]):
            if len(path) >= 2:
                chains.append(list(path))

    for root in roots:
        dfs(root, [root])

    chains.sort(key=len, reverse=True)
    return chains[:10]


def graph_builder(state: EvoMapState) -> dict:
    """构建演化图谱 JSON"""
    entities = state.get("entities", [])
    relations = state.get("relations", [])

    entity_map, adjacency = _build_adjacency(entities, relations)
    chains = _find_evolution_chains(entities, relations)

    entity_name_map = {e.id: e.name for e in entities}
    named_chains = [
        [entity_name_map.get(eid, eid) for eid in chain]
        for chain in chains
    ]

    category_groups: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        category_groups[e.category].append(e.name)

    status_groups: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        status_groups[e.status].append(e.name)

    evolution_graph = {
        "query": state["query"],
        "summary": {
            "total_entities": len(entities),
            "total_relations": len(relations),
            "categories": {k: len(v) for k, v in category_groups.items()},
            "status_distribution": {k: len(v) for k, v in status_groups.items()},
        },
        "entities": entity_map,
        "adjacency": adjacency,
        "evolution_chains": named_chains,
        "category_groups": dict(category_groups),
        "relations": [r.model_dump() for r in relations],
    }

    return {
        "evolution_graph": evolution_graph,
        "messages": [
            HumanMessage(
                content=(
                    f"演化图谱构建完成：{len(entities)} 个实体，"
                    f"{len(relations)} 条关系，"
                    f"{len(chains)} 条演化链"
                )
            )
        ],
    }
