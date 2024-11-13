import datetime
import requests
from config.settings import API_KEYS, LLM_MODELS, LLM_URLS

class PrefrontalCortex:
    def __init__(self, orchestrator=None, logger=None, **kwargs):
        self.orchestrator = orchestrator
        self.role = kwargs.get("role", "Task Coordinator and Working Memory")
        self.goal = kwargs.get("goal", "Coordinate tasks across memory regions and manage working memory.")
        self.backstory = kwargs.get("backstory", "")
        self.tools = kwargs.get("tools", [])
        self.verbose = kwargs.get("verbose", False)
        self.cache = {}  # Temporary cache for high-priority data
        self.working_memory = {}  # Working memory for active contexts
        self.logger = logger
        self.task_queue = []  # Task queue for prioritized execution
        self.cache_size = kwargs.get("cache_size", 50)  # Max cache size
        self.working_memory_size = kwargs.get("working_memory_size", 20)  # Max working memory size
        self.completed_tasks = []
        self.cerebellum = kwargs.get("cerebellum_instance")
        
    ### WORKING MEMORY FUNCTIONS ###
    def add_to_working_memory(self, key, value, metadata=None):
        """Store data in working memory with size limitation."""
        if len(self.working_memory) >= self.working_memory_size:
            oldest_key = next(iter(self.working_memory))
            del self.working_memory[oldest_key]  # Remove the oldest entry to make space
            if self.verbose:
                print(f"Removed oldest entry from working memory: {oldest_key}")
        metadata = metadata or {"timestamp": datetime.datetime.now().isoformat()}
        self.working_memory[key] = {"value": value, "metadata": metadata}
        if self.verbose:
            print(f"Stored in working memory: {key} -> {value}")
        return f"Stored {key} -> {value} in working memory."

    def retrieve_from_working_memory(self, key):
        """Retrieve data from working memory."""
        return self.working_memory.get(key, "No data found in working memory.")

    def clear_working_memory(self):
        """Clear all data from working memory."""
        self.working_memory.clear()
        if self.verbose:
            print("Cleared all data from working memory.")
        return "Working memory cleared."

    ### CACHE FUNCTIONS ###
    def add_to_cache(self, key, value, metadata=None):
        """Add an item to the cache with priority-based expiration."""
        metadata = metadata or {}
        metadata.setdefault("priority", "normal")
        metadata.setdefault("timestamp", datetime.datetime.now().isoformat())
        if len(self.cache) >= self.cache_size:
            # Remove the lowest-priority item to make space
            lowest_priority = min(self.cache.items(), key=lambda x: x[1]["metadata"].get("priority", 1))
            del self.cache[lowest_priority[0]]
        self.cache[key] = {"value": value, "metadata": metadata}

    def retrieve_from_cache(self, key):
        """Retrieve data from cache."""
        return self.cache.get(key, "No data found in cache.")

    def clear_cache(self):
        """Clear all data from cache."""
        self.cache.clear()
        if self.verbose:
            print("Cleared all data from cache.")

    ### TASK MANAGEMENT ###
    def add_task(self, task_name, priority="normal", metadata=None):
        """Add a task to the queue with priority."""
        try:
            if not task_name or not isinstance(task_name, str):
                raise ValueError("Task name must be a non-empty string.")

            metadata = metadata or {}
            metadata.setdefault("priority", priority)
            metadata.setdefault("timestamp", datetime.datetime.now().isoformat())

            # Validate priority before adding
            if not isinstance(metadata["priority"], (int, float, str)):
                raise ValueError("Priority must be an int, float, or string.")

            # Convert priority to a comparable value (e.g., integer)
            priority_value = (
                metadata["priority"]
                if isinstance(metadata["priority"], (int, float))
                else {"low": 1, "normal": 2, "high": 3}.get(metadata["priority"], 2)
            )

            self.task_queue.append({"task_name": task_name, "metadata": metadata, "priority_value": priority_value})
            self.task_queue.sort(key=lambda x: x["priority_value"], reverse=True)  # Sort by priority

            if self.verbose:
                print(f"Task added: {task_name} with priority {priority}")
            return f"Task '{task_name}' added successfully."
        except Exception as e:
            self.logger.log_error("PrefrontalCortex.add_task", str(e))
            return f"Error adding task: {e}"

    def view_archived_tasks(self):
        """View all archived tasks."""
        return self.completed_tasks

    def process_next_task(self):
        """Process the next task in the queue."""
        if not self.task_queue:
            return "No tasks in the queue."
        task = self.task_queue.pop(0)
        if self.verbose:
            print(f"Processing task: {task['task_name']} with metadata: {task['metadata']}")
        # Add task execution logic here (e.g., delegate to other regions)
        return f"Executed task: {task['task_name']}"

    def adjust_task_priorities(self, urgency_factor=1.5, decay_factor=0.9):
        """Dynamically adjust task priorities based on urgency and decay."""
        for task in self.task_queue:
            priority = task["metadata"].get("priority", "normal")
            timestamp = task["metadata"].get("timestamp")

            # Validate and normalize timestamp
            try:
                time_elapsed = (datetime.datetime.now() - datetime.datetime.fromisoformat(timestamp)).total_seconds()
            except (TypeError, ValueError):
                self.logger.log_error("adjust_task_priorities", f"Invalid timestamp for task: {task.get('task_name', 'Unknown')}")
                time_elapsed = float("inf")  # Assign a very high value to deprioritize

            # Normalize priority
            priority_map = {"high": urgency_factor, "normal": 1, "low": decay_factor}
            priority_factor = priority_map.get(priority, 1)  # Default to "normal" if priority is unrecognized

            # Adjust priority score
            task["metadata"]["priority_score"] = priority_factor / (1 + time_elapsed)

        # Sort tasks by recalculated priority scores
        self.task_queue.sort(key=lambda x: x["metadata"].get("priority_score", 0), reverse=True)

        if self.verbose:
            print("Task priorities adjusted dynamically.")

    def feedback_loop(self, task_name, status, feedback=None):
        """Process feedback for completed tasks."""
        if self.verbose:
            print(f"Task: {task_name} - Status: {status}. Feedback: {feedback}")

        # Find the task
        task = next((t for t in self.task_queue if t["task_name"] == task_name), None)
        if not task:
            self.logger.log_error("feedback_loop", f"Task '{task_name}' not found in task queue.")
            return f"Task '{task_name}' not found."

        if status == "success":
            self.completed_tasks.append(task)  # Archive successful task
            self.task_queue.remove(task)
            if self.verbose:
                print(f"Task '{task_name}' completed successfully and archived.")
        elif status == "failure":
            retries = task["metadata"].get("retries", 0) + 1
            task["metadata"]["retries"] = retries

            if retries > 3:  # Limit retries to 3
                self.task_queue.remove(task)
                self.logger.log_error("feedback_loop", f"Task '{task_name}' exceeded retry limit and was removed.")
                if self.verbose:
                    print(f"Task '{task_name}' exceeded retry limit and removed from queue.")
            else:
                task["metadata"]["priority"] = "low"  # Set priority to low after failure
                self.logger.log_error("feedback_loop", f"Task '{task_name}' failed and was requeued with retries: {retries}.")
                if self.verbose:
                    print(f"Task '{task_name}' failed. Priority reduced and requeued with retry count: {retries}.")


    ### DELEGATION ###
    def delegate_task(self, orchestrator, task_name, target_region, *args, **kwargs):
        """
        Delegate a task to a target memory region via the orchestrator.
        """
        if self.verbose:
            print(f"Delegating task '{task_name}' to {target_region}")
        return orchestrator.route_task(target_region, task_name, *args, **kwargs)
    
    def delegate_to_cerebellum(self, task_name, workflow_name, *args, **kwargs):
        """Delegate a procedural task to the Cerebellum."""
        if not self.cerebellum:
            return "Cerebellum instance not initialized."
        if task_name == "store_workflow":
            return self.cerebellum.store_workflow(workflow_name, *args, **kwargs)
        elif task_name == "retrieve_workflow":
            return self.cerebellum.retrieve_workflow(workflow_name)
        elif task_name == "optimize_workflow":
            return self.cerebellum.optimize_workflow(workflow_name, *args)
        elif task_name == "delete_workflow":
            return self.cerebellum.delete_workflow(workflow_name)
        return f"Unknown Cerebellum task: {task_name}"

    def route_to_memory_region(self, target_agent, method, *args, **kwargs):
        """Route tasks intelligently to memory regions."""
        if hasattr(target_agent, "instance"):
            target_instance = target_agent.instance  # Access the actual instance
            if hasattr(target_instance, method):
                return getattr(target_instance, method)(*args, **kwargs)
            else:
                return f"Method {method} not found in {target_instance.__class__.__name__}."
        else:
            return f"Unknown memory region: {target_agent}"
        
    def decide_target_region(self, task):
        """Determine the best memory region for the task."""
        if "emotion" in task["metadata"].get("tags", []):
            return "Amygdala"
        elif "factual" in task["metadata"].get("tags", []):
            return "Hippocampus"
        return "Default"

    ### LLM REASONING ###
    def llm_reasoning(self, prompt, model_name="prefrontal_cortex"):
        headers = {"Authorization": f"Bearer {API_KEYS['openai']}"}
        try:
            response = requests.post(
                LLM_URLS[model_name],
                json={"prompt": prompt, "model": LLM_MODELS[model_name]},
                headers=headers
            )
            if response.status_code == 200:
                return response.json().get("content", "No response content")
            return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"
        
    def log_error(self, message, exception):
        """Log errors for debugging."""
        error_message = f"{message}: {str(exception)}"
        print(error_message)  # Replace with logging to a file if needed

