import os
import json
import logger
import datetime
import pickle 
import re

class Cerebellum:
    @staticmethod
    def sanitize_filename(name):
        """Remove invalid characters for a filename."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name)
    
    def __init__(self, logger=None, **kwargs):
        # Handle general configurations
        self.role = kwargs.get("role", "Procedural Memory")
        self.goal = kwargs.get("goal", "Store workflows and serialized models for procedural tasks.")
        self.backstory = kwargs.get("backstory", "")
        self.verbose = kwargs.get("verbose", False)
        self.cache = kwargs.get("cache", True)
        self.max_iter = kwargs.get("max_iter", 50)
        self.allow_code_execution = kwargs.get("allow_code_execution", False)
        self.use_system_prompt = kwargs.get("use_system_prompt", True)
        self.respect_context_window = kwargs.get("respect_context_window", True)
        self.max_retry_limit = kwargs.get("max_retry_limit", 2)
        self.logger = logger
        self.storage_path = kwargs.get("storage_path", "data/cerebellum/")
        os.makedirs(self.storage_path, exist_ok=True)  # Ensure storage path exists
        self.workflows = {}  # Dictionary to store workflows

    ### WORKFLOW MANAGEMENT ###

    def store_workflow(self, name, workflow, metadata=None):
        try:
            if not name or not isinstance(name, str):
                self.logger.log_error("store_workflow", "Workflow name must be a non-empty string.")
                raise ValueError("Workflow name must be a non-empty string.")

            metadata = metadata or {}
            metadata.setdefault("timestamp", datetime.datetime.now().isoformat())
            metadata.setdefault("tags", [])

            workflow_data = {"workflow": workflow, "metadata": metadata}
            file_path = os.path.join(self.storage_path, f"{name}.pkl")
            with open(file_path, "wb") as file:
                pickle.dump(workflow_data, file)

            if self.verbose:
                print(f"Stored workflow: {name} at {file_path}")
            return f"Workflow '{name}' stored successfully."
        except Exception as e:
            self.logger.log_error("store_workflow", str(e))
            return f"Error storing workflow: {e}"

    def retrieve_workflow(self, name):
        try:
            if not name or not isinstance(name, str):
                self.logger.log_error("retrieve_workflow", "Workflow name must be a non-empty string.")
                raise ValueError("Workflow name must be a non-empty string.")

            file_path = os.path.join(self.storage_path, f"{name}.pkl")
            if not os.path.exists(file_path):
                return f"Workflow '{name}' not found."

            with open(file_path, "rb") as file:
                workflow_data = pickle.load(file)

            if self.verbose:
                print(f"Retrieved workflow: {name}")
            return workflow_data
        except Exception as e:
            self.logger.log_error("retrieve_workflow", str(e))
            return f"Error retrieving workflow: {e}"

    def list_workflows(self):
        """List all stored workflows."""
        return [file.split(".pkl")[0] for file in os.listdir(self.storage_path) if file.endswith(".pkl")]

    def delete_workflow(self, name):
        """Delete a workflow by name."""
        file_path = os.path.join(self.storage_path, f"{name}.pkl")
        if os.path.exists(file_path):
            os.remove(file_path)
            if self.verbose:
                print(f"Deleted workflow: {name}")
            return f"Workflow '{name}' deleted successfully."
        return f"Workflow '{name}' not found."

    ### WORKFLOW OPTIMIZATION ###

    def optimize_workflow(self, name, insights):
        try:
            if not name or not isinstance(name, str):
                self.logger.log_error("optimize_workflow", "Workflow name must be a non-empty string.")
                raise ValueError("Workflow name must be a non-empty string.")
            if not isinstance(insights, dict):
                self.logger.log_error("optimize_workflow", "Insights must be a dictionary.")
                raise ValueError("Insights must be a dictionary.")
            
            workflow_data = self.retrieve_workflow(name)
            if isinstance(workflow_data, str):  # Workflow not found
                return workflow_data
            
            workflow = workflow_data["workflow"]
            metadata = workflow_data["metadata"]
    
            # Apply insights to improve the workflow
            for key, value in insights.items():
                workflow[key] = value
            
            # Update workflow metadata
            metadata["last_optimized"] = datetime.datetime.now().isoformat()
            return self.store_workflow(name, workflow, metadata)
        except Exception as e:
            self.logger.log_error("optimize_workflow", str(e))
            return f"Error optimizing workflow: {e}"

    def retrieve_workflows_by_metadata(self, tag=None, timestamp=None):
        """Retrieve workflows based on metadata filtering."""
        results = []
        for name in self.list_workflows():
            workflow_data = self.retrieve_workflow(name)
            metadata = workflow_data["metadata"]
            if tag and tag not in metadata.get("tags", []):
                continue
            if timestamp and metadata["timestamp"] < timestamp:
                continue
            results.append({"name": name, "metadata": metadata})
        return results
    
    def log_error(self, message, exception):
        """Log errors for debugging."""
        error_message = f"{message}: {str(exception)}"
        print(error_message)  # Replace with logging to a file if needed
