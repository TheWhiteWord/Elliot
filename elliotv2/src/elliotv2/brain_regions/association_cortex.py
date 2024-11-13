import networkx as nx
import datetime

import networkx as nx

class AssociationCortex:
    def __init__(self, logger=None, **kwargs):
        self.role = kwargs.get("role", "Contextual Memory")
        self.goal = kwargs.get("goal", "Link concepts and relationships.")
        self.backstory = kwargs.get("backstory", "")
        self.verbose = kwargs.get("verbose", False)
        self.cache = kwargs.get("cache", True)
        self.max_iter = kwargs.get("max_iter", 10)
        self.allow_code_execution = kwargs.get("allow_code_execution", False)
        self.use_system_prompt = kwargs.get("use_system_prompt", True)
        self.respect_context_window = kwargs.get("respect_context_window", True)
        self.max_retry_limit = kwargs.get("max_retry_limit", 2)
        self.logger = logger

        # Initialize as a networkx graph
        self.graph = nx.Graph()

        if self.verbose:
            print(f"Association Cortex initialized with role: {self.role}")

    # Node Management

    def add_node(self, node_id, data=None):
        """Add a node to the graph if it doesn't already exist."""
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, data=data)
            self.logger.log_info("Association Cortex", f"Added node: {node_id} with data: {data}")
        else:
            self.logger.log_warning("Association Cortex", f"Node {node_id} already exists. Skipping.")

    def get_node_data(self, node_id):
        """Retrieve data associated with a node."""
        if node_id in self.graph:
            return self.graph.nodes[node_id].get('data', {})
        if self.logger:
            self.logger.log_error(f"Node {node_id} not found in the graph.")
        return None
    
    def remove_node(self, node_id):
        """Remove a node and its associated relationships."""
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            if self.logger:
                self.logger.log_info("Association Cortex", f"Removed node: {node_id}")
        else:
            if self.logger:
                self.logger.log_error(f"Node {node_id} not found in the graph.")

    def update_node_data(self, node_id, new_data):
        """Update data in an existing node."""
        if node_id in self.graph:
            self.graph.nodes[node_id]['data'] = new_data
            if self.logger:
                self.logger.log_info("Association Cortex", f"Updated data for node: {node_id} to: {new_data}")
        else:
            if self.logger:
                self.logger.log_error("Association Cortex", f"Node {node_id} not found.")

    #Relationship Management

    def add_relationship(self, node1, node2, relationship_type="related"):
        """Add a relationship between two nodes if it doesn't already exist."""
        if not self.graph.has_edge(node1, node2):
            self.graph.add_edge(node1, node2, relationship=relationship_type, timestamp=datetime.datetime.now().isoformat())
            self.logger.log_info("Association Cortex", f"Added relationship between {node1} and {node2} of type {relationship_type}.")
        else:
            self.logger.log_warning("Association Cortex", f"Relationship between {node1} and {node2} already exists. Skipping.")

    def find_related_nodes(self, node_id, depth=1):
        """Find related nodes up to a certain depth."""
        if node_id not in self.graph:
            if self.logger:
                self.logger.log_error(f"Node {node_id} not found in the graph.")
            return []

        related_nodes = list(nx.single_source_shortest_path_length(self.graph, node_id, cutoff=depth).keys())
        if self.logger:
            self.logger.log_info("Association Cortex", f"Found related nodes for {node_id}: {related_nodes}")
        return related_nodes

    def get_relationship_data(self, node1, node2):
        """Retrieve data associated with the relationship between two nodes."""
        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]
        if self.logger:
            self.logger.log_error(f"Relationship between {node1} and {node2} not found in the graph.")
        return None
    
    def remove_relationship(self, node1, node2):
        """Remove the relationship between two nodes."""
        # Check if the relationship exists
        if not self.graph.has_edge(node1, node2):
            error_reason = f"Relationship between {node1} and {node2} not found."
            if not self.graph.has_node(node1):
                error_reason += f" Node {node1} does not exist."
            if not self.graph.has_node(node2):
                error_reason += f" Node {node2} does not exist."
            self.logger.log_error("Association Cortex", error_reason)
            return None

        # Remove the relationship
        self.graph.remove_edge(node1, node2)
        self.logger.log_info("Association Cortex", f"Removed relationship between {node1} and {node2}.")

    def update_relationship_data(self, node1, node2, new_data):
        """Update data associated with the relationship between two nodes."""
        if self.graph.has_edge(node1, node2):
            self.graph[node1][node2].update(new_data)
            if self.logger:
                self.logger.log_info("Association Cortex", f"Updated relationship data between {node1} and {node2} to: {new_data}")
        else:
            if self.logger:
                self.logger.log_error("Association Cortex", f"Relationship between {node1} and {node2} not found.")

    def update_relationship_data(self, node1, node2, new_data):
        """Update data associated with the relationship between two nodes."""
        if self.graph.has_edge(node1, node2):
            self.graph[node1][node2].update(new_data)
            if self.logger:
                self.logger.log_info("Association Cortex", f"Updated relationship data between {node1} and {node2} to: {new_data}")
        else:
            if self.logger:
                self.logger.log_error("Association Cortex", f"Relationship between {node1} and {node2} not found.")

    # Advanced Graph Queries

    def find_all_paths(self, node1, node2):
        """Find all possible paths between two nodes."""
        if node1 in self.graph and node2 in self.graph:
            try:
                paths = list(nx.all_simple_paths(self.graph, source=node1, target=node2))
                if self.logger:
                    self.logger.log_info("Association Cortex", f"Found paths between {node1} and {node2}: {paths}")
                return paths
            except nx.NetworkXNoPath:
                if self.logger:
                    self.logger.log_warning("Association Cortex", f"No paths found between {node1} and {node2}.")
                return []
        if self.logger:
            self.logger.log_error("Association Cortex", f"One or both nodes {node1} and {node2} do not exist.")
        return []

    def filter_nodes(self, attribute=None, condition=None):
        """
        Filter nodes based on attributes.
        Example:
            attribute='tags', condition=lambda tags: 'critical' in tags
        """
        filtered_nodes = []
        for node, data in self.graph.nodes(data=True):
            if attribute in data.get('data', {}) and condition(data['data'][attribute]):
                filtered_nodes.append(node)
        if self.logger:
            self.logger.log_info("Association Cortex", f"Filtered nodes based on attribute {attribute}: {filtered_nodes}")
        return filtered_nodes

    def visualize_graph(self):
        """Optional: Visualize the graph (requires Matplotlib)."""
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        nx.draw(self.graph, with_labels=True, node_color="lightblue", font_weight="bold")
        plt.show()
    
    #Analytics and Insights

    def measure_centrality(self, centrality_type="degree"):
        """Compute centrality metrics for the graph."""
        try:
            if centrality_type == "degree":
                centrality = nx.degree_centrality(self.graph)
            else:
                raise ValueError(f"Unsupported centrality type: {centrality_type}")
    
            # Log summary
            node_count = len(centrality)
            self.logger.log_info("Association Cortex", f"Computed {centrality_type} centrality for {node_count} nodes.")
            # Optionally truncate detailed output
            truncated_centrality = dict(list(centrality.items())[:10])  # Show first 10 nodes
            self.logger.log_info("Association Cortex", f"Sample centrality: {truncated_centrality}")
    
            return centrality
        except Exception as e:
            self.logger.log_error("Association Cortex", f"Failed to compute {centrality_type} centrality: {e}")
            return None
   
    def detect_clusters(self, method="connected_components"):
        """Detect clusters in the graph."""
        try:
            if method == "connected_components":
                clusters = list(nx.connected_components(self.graph))
            else:
                raise ValueError(f"Unsupported clustering method: {method}")

            # Assign labels and summarize
            cluster_summary = {f"Cluster_{i+1}": len(cluster) for i, cluster in enumerate(clusters)}
            self.logger.log_info("Association Cortex", f"Detected {len(clusters)} clusters: {cluster_summary}")

            return cluster_summary
        except Exception as e:
            self.logger.log_error("Association Cortex", f"Failed to detect clusters: {e}")
            return None
    
    def detect_clusters(self, method="connected_components"):
        """Detect clusters in the graph."""
        try:
            if method == "connected_components":
                clusters = [set(component) for component in nx.connected_components(self.graph)]
            else:
                raise ValueError(f"Unsupported clustering method: {method}")

            if self.logger:
                self.logger.log_info("Association Cortex", f"Detected clusters using {method}: {clusters}")
            return clusters
        except Exception as e:
            if self.logger:
                self.logger.log_error("Association Cortex", f"Error detecting clusters with {method}: {e}")
            return []

    def find_shortest_path(self, node1, node2):
        """Find the shortest path between two nodes."""
        if node1 in self.graph and node2 in self.graph:
            try:
                path = nx.shortest_path(self.graph, source=node1, target=node2)
                if self.logger:
                    self.logger.log_info("Association Cortex", f"Shortest path between {node1} and {node2}: {path}")
                return path
            except nx.NetworkXNoPath:
                if self.logger:
                    self.logger.log_warning(f"No path found between {node1} and {node2}.")
                return None
        if self.logger:
            self.logger.log_error(f"One or both nodes {node1} and {node2} do not exist.")
        return None
    
    # Purge old data

    def purge_old_data(self, retention_days=30):
        """Remove old nodes and edges based on the retention period."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        removed_nodes = []
        removed_edges = []

        # Remove old nodes
        for node in list(self.graph.nodes):
            node_data = self.graph.nodes[node].get("data", {})
            if "timestamp" in node_data:
                node_date = datetime.datetime.fromisoformat(node_data["timestamp"])
                if node_date < cutoff_date:
                    self.graph.remove_node(node)
                    removed_nodes.append(node)

        # Remove old edges
        for edge in list(self.graph.edges):
            edge_data = self.graph.edges[edge].get("timestamp", None)
            if edge_data:
                edge_date = datetime.datetime.fromisoformat(edge_data)
                if edge_date < cutoff_date:
                    self.graph.remove_edge(*edge)
                    removed_edges.append(edge)

        if self.logger:
            self.logger.log_info(
                "Association Cortex",
                f"Purged {len(removed_nodes)} nodes and {len(removed_edges)} edges older than {retention_days} days."
            )
        return {"removed_nodes": removed_nodes, "removed_edges": removed_edges}

    def monitor_and_purge(self, node_limit=10000, edge_limit=50000, retention_days=30):
        """Monitor graph size and purge data if limits are exceeded."""
        if len(self.graph.nodes) > node_limit or len(self.graph.edges) > edge_limit:
            if self.logger:
                self.logger.log_warning(
                    "Association Cortex",
                    f"Graph exceeded limits: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges. Initiating purge."
                )
            return self.purge_old_data(retention_days)
        return {"status": "No purge needed."}



