"""Knowledge graph with entities and relationships"""
import json
from typing import Dict, List, Optional, Set
from collections import deque, defaultdict


class KnowledgeGraph:
    """Knowledge graph with nodes, edges, and traversal capabilities"""
    
    def __init__(self):
        """Initialize knowledge graph"""
        self.nodes = {}  # node_id -> {type, properties}
        self.edges = defaultdict(list)  # from_id -> [(to_id, relation, properties)]
        self.reverse_edges = defaultdict(list)  # to_id -> [(from_id, relation, properties)]
    
    def add_node(self, node_id: str, node_type: str, properties: Dict = None) -> bool:
        """
        Add a node to the graph
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node (e.g., 'person', 'document', 'concept')
            properties: Optional properties dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not node_id or not node_type:
                return False
            
            self.nodes[node_id] = {
                'type': node_type,
                'properties': properties or {}
            }
            return True
        except Exception as e:
            print(f"Error adding node: {e}")
            return False
    
    def get_node(self, node_id: str) -> Dict:
        """
        Get a node by ID
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node dictionary or empty dict if not found
        """
        node_data = self.nodes.get(node_id, {})
        if node_data:
            return {
                'node_id': node_id,
                'type': node_data.get('type'),
                'properties': node_data.get('properties', {})
            }
        return {}
    
    def update_node(self, node_id: str, properties: Dict) -> bool:
        """
        Update node properties
        
        Args:
            node_id: Node identifier
            properties: Properties to update (merged with existing)
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            return False
        
        try:
            current_props = self.nodes[node_id].get('properties', {})
            current_props.update(properties)
            self.nodes[node_id]['properties'] = current_props
            return True
        except Exception as e:
            print(f"Error updating node: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its edges
        
        Args:
            node_id: Node identifier
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            return False
        
        # Remove node
        del self.nodes[node_id]
        
        # Remove outgoing edges
        if node_id in self.edges:
            del self.edges[node_id]
        
        # Remove incoming edges
        if node_id in self.reverse_edges:
            del self.reverse_edges[node_id]
        
        # Remove edges pointing to this node
        for from_id in list(self.edges.keys()):
            self.edges[from_id] = [
                edge for edge in self.edges[from_id]
                if edge[0] != node_id
            ]
        
        # Remove reverse edges from this node
        for to_id in list(self.reverse_edges.keys()):
            self.reverse_edges[to_id] = [
                edge for edge in self.reverse_edges[to_id]
                if edge[0] != node_id
            ]
        
        return True
    
    def list_nodes(self, node_type: str = None) -> List[Dict]:
        """
        List all nodes, optionally filtered by type
        
        Args:
            node_type: Optional type filter
            
        Returns:
            List of node dictionaries
        """
        results = []
        for node_id, node_data in self.nodes.items():
            if node_type is None or node_data.get('type') == node_type:
                results.append({
                    'node_id': node_id,
                    'type': node_data.get('type'),
                    'properties': node_data.get('properties', {})
                })
        return results
    
    def add_edge(self, from_id: str, to_id: str, relation: str, properties: Dict = None) -> bool:
        """
        Add an edge between nodes
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Relationship type
            properties: Optional edge properties
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if nodes exist
            if from_id not in self.nodes or to_id not in self.nodes:
                return False
            
            if not relation:
                return False
            
            # Add edge
            edge_data = (to_id, relation, properties or {})
            self.edges[from_id].append(edge_data)
            
            # Add reverse edge for efficient bidirectional traversal
            reverse_edge_data = (from_id, relation, properties or {})
            self.reverse_edges[to_id].append(reverse_edge_data)
            
            return True
        except Exception as e:
            print(f"Error adding edge: {e}")
            return False
    
    def get_edges(self, node_id: str, direction: str = 'both') -> List[Dict]:
        """
        Get edges connected to a node
        
        Args:
            node_id: Node identifier
            direction: 'out', 'in', or 'both'
            
        Returns:
            List of edge dictionaries
        """
        if node_id not in self.nodes:
            return []
        
        results = []
        
        # Outgoing edges
        if direction in ('out', 'both'):
            for to_id, relation, props in self.edges.get(node_id, []):
                results.append({
                    'from': node_id,
                    'to': to_id,
                    'relation': relation,
                    'properties': props,
                    'direction': 'out'
                })
        
        # Incoming edges
        if direction in ('in', 'both'):
            for from_id, relation, props in self.reverse_edges.get(node_id, []):
                results.append({
                    'from': from_id,
                    'to': node_id,
                    'relation': relation,
                    'properties': props,
                    'direction': 'in'
                })
        
        return results
    
    def delete_edge(self, from_id: str, to_id: str, relation: str) -> bool:
        """
        Delete an edge
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Relationship type
            
        Returns:
            True if successful, False otherwise
        """
        if from_id not in self.edges:
            return False
        
        # Remove from forward edges
        original_len = len(self.edges[from_id])
        self.edges[from_id] = [
            edge for edge in self.edges[from_id]
            if not (edge[0] == to_id and edge[1] == relation)
        ]
        
        # Remove from reverse edges
        if to_id in self.reverse_edges:
            self.reverse_edges[to_id] = [
                edge for edge in self.reverse_edges[to_id]
                if not (edge[0] == from_id and edge[1] == relation)
            ]
        
        return len(self.edges[from_id]) < original_len
    
    def find_path(self, from_id: str, to_id: str, max_depth: int = 5) -> List[List[str]]:
        """
        Find paths between two nodes using BFS
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            max_depth: Maximum path depth
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        if from_id not in self.nodes or to_id not in self.nodes:
            return []
        
        if from_id == to_id:
            return [[from_id]]
        
        # BFS to find all paths
        paths = []
        queue = deque([(from_id, [from_id])])
        visited_at_depth = defaultdict(set)
        
        while queue:
            current, path = queue.popleft()
            depth = len(path)
            
            if depth > max_depth:
                continue
            
            # Get neighbors
            for to_node, relation, props in self.edges.get(current, []):
                if to_node == to_id:
                    # Found a path
                    paths.append(path + [to_node])
                elif to_node not in path and to_node not in visited_at_depth[depth]:
                    # Continue searching
                    visited_at_depth[depth].add(to_node)
                    queue.append((to_node, path + [to_node]))
        
        return paths
    
    def get_neighbors(self, node_id: str, depth: int = 1) -> List[Dict]:
        """
        Get all neighbors within specified depth
        
        Args:
            node_id: Node identifier
            depth: How many hops to traverse
            
        Returns:
            List of neighbor nodes with their distance
        """
        if node_id not in self.nodes or depth < 1:
            return []
        
        neighbors = []
        visited = {node_id}
        queue = deque([(node_id, 0)])
        
        while queue:
            current, current_depth = queue.popleft()
            
            if current_depth >= depth:
                continue
            
            # Get adjacent nodes
            for to_node, relation, props in self.edges.get(current, []):
                if to_node not in visited:
                    visited.add(to_node)
                    node_data = self.nodes.get(to_node, {})
                    neighbors.append({
                        'node_id': to_node,
                        'type': node_data.get('type'),
                        'properties': node_data.get('properties', {}),
                        'distance': current_depth + 1,
                        'relation_from_source': relation
                    })
                    queue.append((to_node, current_depth + 1))
        
        return neighbors
    
    def query(self, pattern: str) -> List[Dict]:
        """
        Simple pattern matching query
        
        Pattern format: "type:node_type" or "property:key=value"
        
        Args:
            pattern: Query pattern
            
        Returns:
            List of matching nodes
        """
        results = []
        
        if pattern.startswith('type:'):
            # Filter by type
            node_type = pattern[5:].strip()
            return self.list_nodes(node_type)
        
        elif pattern.startswith('property:'):
            # Filter by property
            prop_spec = pattern[9:].strip()
            if '=' in prop_spec:
                key, value = prop_spec.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                for node_id, node_data in self.nodes.items():
                    props = node_data.get('properties', {})
                    if key in props and str(props[key]) == value:
                        results.append({
                            'node_id': node_id,
                            'type': node_data.get('type'),
                            'properties': props
                        })
        
        return results
    
    def save(self, path: str) -> bool:
        """
        Save graph to JSON file
        
        Args:
            path: File path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert edges to serializable format
            edges_list = []
            for from_id, edge_list in self.edges.items():
                for to_id, relation, props in edge_list:
                    edges_list.append({
                        'from': from_id,
                        'to': to_id,
                        'relation': relation,
                        'properties': props
                    })
            
            data = {
                'nodes': self.nodes,
                'edges': edges_list
            }
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving graph: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """
        Load graph from JSON file
        
        Args:
            path: File path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.nodes = data.get('nodes', {})
            
            # Rebuild edges
            self.edges.clear()
            self.reverse_edges.clear()
            
            for edge in data.get('edges', []):
                from_id = edge['from']
                to_id = edge['to']
                relation = edge['relation']
                props = edge.get('properties', {})
                
                self.edges[from_id].append((to_id, relation, props))
                self.reverse_edges[to_id].append((from_id, relation, props))
            
            return True
        except Exception as e:
            print(f"Error loading graph: {e}")
            return False
    
    def export_graphviz(self) -> str:
        """
        Export graph in GraphViz DOT format
        
        Returns:
            DOT format string
        """
        lines = ['digraph KnowledgeGraph {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box];')
        lines.append('')
        
        # Add nodes
        for node_id, node_data in self.nodes.items():
            node_type = node_data.get('type', 'unknown')
            label = f"{node_id}\\n({node_type})"
            lines.append(f'  "{node_id}" [label="{label}"];')
        
        lines.append('')
        
        # Add edges
        for from_id, edge_list in self.edges.items():
            for to_id, relation, props in edge_list:
                lines.append(f'  "{from_id}" -> "{to_id}" [label="{relation}"];')
        
        lines.append('}')
        
        return '\n'.join(lines)
