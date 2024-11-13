import os
import yaml
import datetime
import time
import shutil
from pathlib import Path

from agents.agent import Agent
from config.settings import LLM_URLS, API_KEYS, LLM_MODELS
from utils.logger import ErrorLogger

from brain_regions.hippocampus import Hippocampus
from brain_regions.prefrontal_cortex import PrefrontalCortex
from brain_regions.cerebellum import Cerebellum
from brain_regions.amygdala import Amygdala
from brain_regions.association_cortex import AssociationCortex

class Orchestrator:
    def __init__(self, config_path="config/agents.yaml"):
        self.logger = ErrorLogger("logs/system_log.txt")
        self.config = self.load_config(config_path)
        self.agents = {}

    def load_config(self, path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def initialize_agents(self):
        # Shared resources
        shared_logger = self.logger

        # Initialize agents
        self.hippocampus = Hippocampus(
            logger=shared_logger, 
            db_file=self.config["hippocampus"].get("db_file", "data/hippocampus.db"),
            **self.config["hippocampus"]
        )

        self.cerebellum = Cerebellum(
            logger=shared_logger,
            **self.config["cerebellum"]
        )

        self.prefrontal_cortex = PrefrontalCortex(
            logger=shared_logger,
            **self.config["prefrontal_cortex"]
        )

        self.amygdala = Amygdala(
            logger=shared_logger,
            db_file=self.config["amygdala"].get("db_file", "data/amygdala.db"),  
            **{k: v for k, v in self.config["amygdala"].items() if k != "db_file"} 
        )

        self.association_cortex = AssociationCortex(
            logger=shared_logger,
            **self.config["association_cortex"]
        )
        self.agents["Contextual Memory"] = self.association_cortex
        print("AssociationCortex initialized successfully.")

    def run_main_tasks(self):
        """
        The central processing loop for the orchestrator, coordinating agents to perform tasks.
        Inspired by the brain's functional flow: Sense → Process → Store → Act.
        """
        # 1. Sense: Gather inputs
        inputs = self.gather_inputs()  # External inputs (e.g., data streams, user commands)

        # 2. Prefrontal Cortex: Decide what to do based on inputs
        for input_data in inputs:
            task = self.prefrontal_cortex.decide_task(input_data)  # Determines the task and assigns agents

            # 3. Process: Route tasks to relevant agents
            if task["type"] == "update_context":
                self.agents["Association Cortex"].add_node(task["data"])
            elif task["type"] == "emotional_analysis":
                self.agents["Amygdala"].process_emotion(task["data"])

            # 4. Store: Save results or feedback in memory
            self.hippocampus.store_recent_action(task)

        # 5. Act: Trigger external-facing actions
        outputs = self.trigger_actions()  # Generate outputs for external systems (e.g., user feedback)

        # Feedback Loop: Agents update one another based on results
        self.perform_feedback_loops()

    def gather_inputs(self):
        """Simulate gathering external inputs (e.g., user commands, sensors, logs)."""
        return [{"type": "update_context", "data": {"id": "node_1", "value": "test"}}]

    def trigger_actions(self):
        """Simulate generating external-facing actions."""
        return [{"action": "print", "message": "Action performed!"}]

    def perform_feedback_loops(self):
        """Simulate updating agents based on feedback from their outputs."""
        # Example: Association Cortex updates the Hippocampus
        recent_contexts = self.agents["Association Cortex"].get_recent_nodes()
        self.agents["Hippocampus"].update_context_memory(recent_contexts)    

    def route_task(self, agent_name, task_name, *args, **kwargs):
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found.")

            task_method = getattr(agent, task_name, None)
            if not task_method:
                raise ValueError(f"Task {task_name} not found for Agent {agent_name}.")

            return task_method(*args, **kwargs)
        except Exception as e:
            self.logger.log_error(f"Failed to route task {task_name} for {agent_name}", str(e))
            return f"Error routing task: {e}"

    def safe_route_task(self, agent_role, method_name, *args, **kwargs):
        try:
            return self.route_task(agent_role, method_name, *args, **kwargs)
        except Exception as e:
            error_message = f"Task '{method_name}' failed for {agent_role}: {e}"
            self.logger.log_error(error_message)
            return f"Error: {error_message}" 
        
    def complex_integration_workflow(self):
        print("\n=== STARTING COMPLEX INTEGRATION WORKFLOW ===")

        # Add a task and validate
        try:
            self.add_task("Prepare Dataset", "high")
            print("Added task: Prepare Dataset")
        except Exception as e:
            print(f"Failed to add task 'Prepare Dataset': {e}")

        # Store dataset details in Hippocampus
        key = "Dataset Details"
        value = {"source": "raw_data.csv", "columns": ["id", "value", "timestamp"]}
        metadata = {"tags": ["data", "workflow"], "priority": "high"}

        try:
            self.manage_memory(key, value, metadata)
            print(f"Stored in Hippocampus: {key} -> {value}")
        except Exception as e:
            print(f"Failed to store memory in Hippocampus: {e}")

        # Create a workflow and store it in Cerebellum
        workflow_name = "Data Preprocessing"
        workflow_steps = {"step1": "Load data", "step2": "Clean data", "step3": "Analyze data"}
        workflow_metadata = {"tags": ["data", "preprocessing"]}

        try:
            self.store_workflow(workflow_name, workflow_steps, workflow_metadata)
            print(f"Workflow stored in Cerebellum: {workflow_name}")
        except Exception as e:
            print(f"Failed to store workflow in Cerebellum: {e}")

        # Retrieve and optimize the workflow in Cerebellum
        try:
            retrieved_workflow = self.retrieve_workflow(workflow_name)
            print(f"Retrieved workflow: {retrieved_workflow}")
        except ValueError as e:
            print(f"Workflow retrieval error: {e}")
        except Exception as e:
            print(f"Failed to retrieve workflow from Cerebellum: {e}")
        
        try:
            optimized_steps = {"step2": "Standardize data"}
            result = self.optimize_workflow(workflow_name, optimized_steps)
            print(f"Workflow optimized in Cerebellum: {workflow_name}")
        except ValueError as e:
            print(f"Optimization error: {e}")
        except Exception as e:
            print(f"Failed to optimize workflow in Cerebellum: {e}")

        # Simulate task feedback
        try:
            self.feedback_loop("Prepare Dataset", "success", "Workflow created and optimized.")
            print("Task 'Prepare Dataset' marked as completed.")
        except Exception as e:
            print(f"Failed to provide feedback for task 'Prepare Dataset': {e}")

    ### PREFRONTAL CORTEX (Working Memory & Task Coordination) ###

    def add_to_working_memory(self, key, value, metadata=None):
        """Store data in working memory."""
        return self.route_task("Task Coordinator", "add_to_working_memory", key, value, metadata)
    
    def view_archived_tasks(self):
        """Expose archived tasks from Prefrontal Cortex."""
        return self.route_task("Task Coordinator", "view_archived_tasks")

    def retrieve_from_working_memory(self, key):
        """Retrieve data from working memory."""
        return self.route_task("Task Coordinator", "retrieve_from_working_memory", key)

    def clear_working_memory(self):
        """Clear all working memory."""
        return self.route_task("Task Coordinator", "clear_working_memory")

    def add_task(self, task_name, priority="normal", metadata=None):
        """Add a task to the Prefrontal Cortex task queue."""
        valid_priorities = {"high", "normal", "low"}
        if priority not in valid_priorities:    
            self.logger.log_error("add_task", f"Invalid priority: {priority}")  
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {valid_priorities}.")  
        return self.route_task("Task Coordinator", "add_task", task_name, priority, metadata)

    def process_next_task(self):
        """Process the next task in the Prefrontal Cortex task queue."""
        return self.route_task("Task Coordinator", "process_next_task")

    def adjust_task_priorities(self, urgency_factor=1.5, decay_factor=0.9):
        """Adjust task priorities dynamically."""
        return self.route_task("Task Coordinator", "adjust_task_priorities", urgency_factor, decay_factor)

    def feedback_loop(self, task_name, status, feedback=None):
        """Provide feedback on completed tasks."""
        return self.route_task("Task Coordinator", "feedback_loop", task_name, status, feedback)
    
    
    ### HIPPOCAMPUS AGENT (Declarative Memory) ###

    def manage_memory(self, key, value, memory_type="declarative", metadata=None):
        """Handle memory management."""
        if memory_type == "declarative":
            return self.route_task("Declarative Memory", "store", key, value, metadata)
        return "Unknown memory type."
    
    def prioritize_memory(self, filter_by="priority", value="high"):
        """Retrieve prioritized memories based on priority or importance."""
        if filter_by == "priority":
            return self.route_task("Declarative Memory", "retrieve_by_priority", value)
        elif filter_by == "importance":
            return self.route_task("Declarative Memory", "retrieve_by_importance", value)
        return "Invalid filter for prioritization."

    def retrieve_by_category(self, category):
        """Retrieve memories based on category."""
        return self.route_task("Declarative Memory", "retrieve_by_category", category)
    
    def retrieve_by_tags(self, tags):
        """Retrieve memories that match specific tags."""
        return self.route_task("Declarative Memory", "retrieve_by_tags", tags)
    
    def flexible_query(self, conditions):
        """Retrieve memories based on flexible conditions."""
        return self.route_task("Declarative Memory", "retrieve_flexible", conditions)

    def retrieve_workflows_by_metadata(self, tag=None, timestamp=None):
        """Delegate the retrieval of workflows by metadata to the Cerebellum agent."""
        return self.route_task("Procedural Memory", "retrieve_workflows_by_metadata", tag=tag, timestamp=timestamp)

    def add_tag_to_memory(self, key, tag):
        """Add a tag to an existing memory."""
        return self.route_task("Declarative Memory", "add_tag", key, tag)

    def remove_tag_from_memory(self, key, tag):
        """Remove a tag from an existing memory."""
        return self.route_task("Declarative Memory", "remove_tag", key, tag)

    def retrieve_important_memory(self, min_importance=5):
        """Retrieve memories based on importance."""
        return self.route_task("Declarative Memory", "retrieve_by_importance", min_importance)
    
    def clear_unimportant_memory(self, min_importance=5):
        """Clear memories with low importance."""
        return self.route_task("Declarative Memory", "clear_low_importance", min_importance)

    def clear_memory(self, priority="low", max_age_days=30, min_importance=1):
        """Clear memories based on priority and importance."""
        priority_result = self.route_task("Declarative Memory", "clear_memory_by_priority", priority, max_age_days)
        importance_result = self.route_task("Declarative Memory", "clear_low_importance", min_importance)
        return f"{priority_result} {importance_result}"

    ### AMYGDALA (Emotional Memory) ###
    def store_emotional_memory(self, memory_key, sentiment, intensity, metadata=None):
        """Store an emotional memory in the Amygdala."""
        return self.route_task("Emotional Memory", "store_emotional_memory", memory_key, sentiment, intensity, metadata)

    def retrieve_emotional_memory(self, sentiment=None, min_intensity=None):
        """Retrieve emotional memories based on sentiment and intensity."""
        return self.route_task("Emotional Memory", "retrieve_emotional_memory", sentiment, min_intensity)

    def adjust_emotional_priorities(self):
        """Adjust priorities system-wide based on emotional context."""
        return self.route_task("Emotional Memory", "adjust_priorities", self)
    
    ### ASSOCIATION CORTEX (Contextual Memory) ###

    def add_context_node(self, node_id, data=None):
        """Add a node to the Association Cortex graph."""
        return self.route_task("Contextual Memory", "add_node", node_id, data)

    def update_context_node_data(self, node_id, new_data):
        """Update data in an existing node."""
        return self.route_task("Contextual Memory", "update_node_data", node_id, new_data)

    def add_context_relationship(self, node1, node2, relationship_type="related"):
        """Add a relationship between two nodes in the graph."""
        return self.route_task("Contextual Memory", "add_relationship", node1, node2, relationship_type)

    def update_context_relationship_data(self, node1, node2, new_data):
        """Update data associated with a relationship between two nodes."""
        return self.route_task("Contextual Memory", "update_relationship_data", node1, node2, new_data)

    def find_related_contexts(self, node_id, depth=1):
        """Find related nodes to a given node."""
        return self.route_task("Contextual Memory", "find_related_nodes", node_id, depth)

    def get_context_node_data(self, node_id):
        """Retrieve data associated with a context node."""
        return self.route_task("Contextual Memory", "get_node_data", node_id)

    def get_context_relationship_data(self, node1, node2):
        """Retrieve data associated with a relationship between two nodes."""
        return self.route_task("Contextual Memory", "get_relationship_data", node1, node2)

    def remove_context_node(self, node_id):
        """Remove a node and its associated relationships."""
        return self.route_task("Contextual Memory", "remove_node", node_id)

    def remove_context_relationship(self, node1, node2):
        """Remove the relationship between two nodes."""
        return self.route_task("Contextual Memory", "remove_relationship", node1, node2)

    def find_shortest_context_path(self, node1, node2):
        """Find the shortest path between two nodes in the graph."""
        return self.route_task("Contextual Memory", "find_shortest_path", node1, node2)

    def find_all_context_paths(self, node1, node2):
        """Find all possible paths between two nodes."""
        return self.route_task("Contextual Memory", "find_all_paths", node1, node2)

    def filter_context_nodes(self, attribute=None, condition=None):
        """Filter nodes in the Association Cortex graph based on attributes."""
        return self.route_task("Contextual Memory", "filter_nodes", attribute, condition)

    def measure_context_node_centrality(self, centrality_type="degree"):
        """Compute centrality metrics for nodes."""
        return self.route_task("Contextual Memory", "measure_centrality", centrality_type)

    def detect_context_clusters(self, method="connected_components"):
        """Detect clusters in the graph."""
        return self.route_task("Contextual Memory", "detect_clusters", method)

    def visualize_context_graph(self):
        """Visualize the Association Cortex graph."""
        return self.route_task("Contextual Memory", "visualize_graph")
    
    def purge_context_data(self, retention_days=30):
        """Manually trigger purging of old data."""
        return self.route_task("Contextual Memory", "purge_old_data", retention_days)

    def monitor_and_purge_context_data(self, node_limit=10000, edge_limit=50000, retention_days=30):
        """Monitor graph size and trigger purging if needed."""
        return self.route_task("Contextual Memory", "monitor_and_purge", node_limit, edge_limit, retention_days)

    ### CEREBELLUM AGENT (Procedural Memory) ###

    def store_workflow(self, name, workflow, metadata=None):
        """Store a workflow in the Cerebellum."""
        return self.route_task("Procedural Memory", "store_workflow", name, workflow, metadata)

    def retrieve_workflow(self, name):
        """Retrieve a workflow from the Cerebellum."""
        if not name or not isinstance(name, str):
            self.logger.log_error("retrieve_workflow", "Workflow name must be a non-empty string.")
            raise ValueError("Workflow name must be a non-empty string.")
        return self.route_task("Procedural Memory", "retrieve_workflow", name)

    def optimize_workflow(self, name, insights):
        """Optimize a workflow in the Cerebellum."""
        if not isinstance(insights, dict):
            raise ValueError("Insights must be a dictionary.")
        return self.route_task("Procedural Memory", "optimize_workflow", name, insights)

    def delete_workflow(self, name):
        """Delete a workflow in the Cerebellum."""
        if not isinstance(insights, dict):
            self.logger.log_error("optimize_workflow", "Invalid insights. Must be a dictionary.")
            return "Workflow optimization failed: Insights must be a dictionary."
        return self.route_task("Procedural Memory", "delete_workflow", name)
        
    
    def log_error(self, message, exception):
        """Log errors for debugging."""
        error_message = f"{message}: {str(exception)}"
        print(error_message)  # Replace with logging to a file if needed

##############################TEST

def test_purging(orchestrator):
    print("Test Case: Data Purging")

    # Add old and recent nodes
    orchestrator.add_context_node(
        "old_node_1", {"timestamp": (datetime.datetime.now() - datetime.timedelta(days=40)).isoformat()}
    )
    orchestrator.add_context_node(
        "recent_node_1", {"timestamp": datetime.datetime.now().isoformat()}
    )

    # Add old and recent edges
    orchestrator.add_context_relationship(
        "old_node_1", "recent_node_1", {"timestamp": (datetime.datetime.now() - datetime.timedelta(days=40)).isoformat()}
    )
    orchestrator.add_context_relationship(
        "recent_node_1", "recent_node_1", {"timestamp": datetime.datetime.now().isoformat()}
    )

    # Perform manual purge
    print("[TEST] Performing manual purge...")
    result = orchestrator.purge_context_data(retention_days=30)
    print("Purge Results:", result)

    # Monitor and purge
    print("[TEST] Performing event-based purge...")
    monitor_result = orchestrator.monitor_and_purge_context_data(node_limit=1, edge_limit=1, retention_days=30)
    print("Monitor Results:", monitor_result)

    # Verify remaining data
    print("Remaining Nodes:", orchestrator.get_context_graph_nodes())
    print("Remaining Edges:", orchestrator.get_context_graph_edges())


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.initialize_agents()

    # Configurable purge interval (default: 1 hour)
    purge_interval_seconds = 3600  
    last_purge_time = time.time()

    try:
        while True:
            orchestrator.run_main_tasks()  # Orchestrator's primary logic

            # Time-based purging
            if time.time() - last_purge_time > purge_interval_seconds:
                print("[INFO] Initiating time-based purging.")
                orchestrator.purge_context_data(retention_days=30)
                last_purge_time = time.time()

            # Event-based purging
            orchestrator.monitor_and_purge_context_data(
                node_limit=10000, edge_limit=50000, retention_days=30
            )

            time.sleep(1)  # Loop throttle

    except KeyboardInterrupt:
        print("[INFO] Graceful shutdown initiated.")