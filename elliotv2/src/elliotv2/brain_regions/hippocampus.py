import sqlite3
import json
import os
import datetime 
import yaml
import logger
from crewai import Agent
from pathlib import Path

class Hippocampus:
    def __init__(self, logger=None, db_file="data/hippocampus.db", **kwargs):
        self.logger = logger
        self.db_file = db_file
        self.role = kwargs.get("role", "Declarative Memory")
        self.goal = kwargs.get("goal", "Store and retrieve factual information efficiently.")
        self.backstory = kwargs.get("backstory", "")
        self.verbose = kwargs.get("verbose", False)
        self.cache = kwargs.get("cache", True)
        self.max_iter = kwargs.get("max_iter", 10)
        self.allow_code_execution = kwargs.get("allow_code_execution", False)
        self.use_system_prompt = kwargs.get("use_system_prompt", True)
        self.respect_context_window = kwargs.get("respect_context_window", True)
        self.max_retry_limit = kwargs.get("max_retry_limit", 2)

        # SQLite setup
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file)
        self.initialize_db()

    def initialize_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS declarative_memory (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            metadata TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def store(self, key, value, metadata=None):
        existing = self.retrieve(key)
        if existing != "No memory found":
            return f"Key {key} already exists. Use update method instead."
           
        try:
            if not key or not isinstance(key, str):
                raise ValueError("Memory key must be a non-empty string.")

            if not isinstance(metadata, dict):
                metadata = {"priority": "normal", "timestamp": datetime.datetime.now().isoformat()}

            metadata.setdefault("importance", 5)
            metadata.setdefault("tags", [])

            value_str = json.dumps(value) if not isinstance(value, str) else value
            metadata_str = json.dumps(metadata)

            query = """
            INSERT OR REPLACE INTO declarative_memory (key, value, metadata) 
            VALUES (?, ?, ?)
            """
            self.conn.execute(query, (key, value_str, metadata_str))
            self.conn.commit()

            return f"Stored in hippocampus: {key} -> {value} with metadata {metadata}"
        except Exception as e:
            self.logger.log_error("Hippocampus.store", str(e))
            return f"Error storing memory: {e}"
        
    def retrieve(self, key):
        """Retrieve a key-value pair."""
        try:
            query = "SELECT value, metadata FROM declarative_memory WHERE key = ?"
            cursor = self.conn.execute(query, (key,))
            result = cursor.fetchone()

            if result:
                value, metadata_str = result
                metadata = json.loads(metadata_str)
                return {"value": value, "metadata": metadata}
            return "No memory found"
        except Exception as e:
            # Safely log the error if a logger is available
            if hasattr(self, "logger") and self.logger:
                if self.logger:
                    self.logger.log_error("Hippocampus.retrieve", str(e))
            return f"Error retrieving memory: {e}"
    
    def retrieve_flexible(self, conditions):
        """Retrieve memories using flexible logical conditions."""
        where_clauses = []
        params = []
    
        # Process conditions: priority, importance, tags, etc.
        if "tags" in conditions:
            tags_query = " OR ".join(["json_each.value = ?"] * len(conditions["tags"]))
            where_clauses.append(f"({tags_query})")
            params.extend(conditions["tags"])
    
        if "priority" in conditions:
            if isinstance(conditions["priority"], list):
                priority_query = " OR ".join(["json_extract(metadata, '$.priority') = ?"] * len(conditions["priority"]))
                where_clauses.append(f"({priority_query})")
                params.extend(conditions["priority"])
            else:
                where_clauses.append("json_extract(metadata, '$.priority') = ?")
                params.append(conditions["priority"])
    
        if "min_importance" in conditions:
            where_clauses.append("CAST(json_extract(metadata, '$.importance') AS INTEGER) >= ?")
            params.append(conditions["min_importance"])
    
        # Combine all conditions using AND
        where_clause = " AND ".join(where_clauses)
    
        query = f"""
        SELECT DISTINCT declarative_memory.key, declarative_memory.value, declarative_memory.metadata
        FROM declarative_memory
        LEFT JOIN json_each(json_extract(metadata, '$.tags')) ON true
        WHERE {where_clause}
        """
        
        cursor = self.conn.execute(query, params)
        results = cursor.fetchall()
    
        return [
            {"key": row[0], "value": row[1], "metadata": json.loads(row[2]) if row[2] else {}}
            for row in results
        ]

    def retrieve_by_priority(self, priority="high"):
        """Retrieve all memories of a specific priority."""
        query = """
        SELECT key, value, metadata FROM declarative_memory
        WHERE json_extract(metadata, '$.priority') = ?
        """
        cursor = self.conn.execute(query, (priority,))
        results = cursor.fetchall()
        return [
            {"key": row[0], "value": row[1], "metadata": json.loads(row[2]) if row[2] else {}}
            for row in results
        ]

    def retrieve_by_importance(self, min_importance=5):
        """Retrieve all memories with importance above a certain threshold."""
        query = """
        SELECT key, value, metadata FROM declarative_memory
        WHERE CAST(json_extract(metadata, '$.importance') AS INTEGER) >= ?
        """
        cursor = self.conn.execute(query, (min_importance,))
        results = cursor.fetchall()
        return [
            {"key": row[0], "value": row[1], "metadata": json.loads(row[2]) if row[2] else {}}
            for row in results
        ]
    
    def retrieve_by_category(self, category):
        """Retrieve all memories that belong to a specific category.""" 
        query = """ 
        SELECT key, value, metadata FROM declarative_memory 
        WHERE json_extract(metadata, '$.category') = ?  
        """ 
        cursor = self.conn.execute(query, (category,))  
        results = cursor.fetchall() 
        return [    
            {"key": row[0], "value": row[1], "metadata": json.loads(row[2]) if row[2] else {}}  
            for row in results  
        ]   

    def retrieve_by_tags(self, tags):
        """Retrieve all memories that match any of the given tags."""
        tags_query = " OR ".join(["json_each.value = ?"] * len(tags))
        query = f"""
        SELECT DISTINCT declarative_memory.key, declarative_memory.value, declarative_memory.metadata
        FROM declarative_memory, json_each(json_extract(metadata, '$.tags'))
        WHERE {tags_query}
        """
        cursor = self.conn.execute(query, tags)
        results = cursor.fetchall()
        return [
            {"key": row[0], "value": row[1], "metadata": json.loads(row[2]) if row[2] else {}}
            for row in results
        ]
    
    def add_tag(self, key, tag):
        """Add a new tag to an existing memory."""
        memory = self.retrieve(key)
        if memory == "No memory found":
            return "Memory not found"

        metadata = memory["metadata"]
        tags = set(metadata.get("tags", []))  # Use a set to avoid duplicates
        tags.add(tag)
        metadata["tags"] = list(tags)

        # Update the memory with new tags
        query = """
        UPDATE declarative_memory
        SET metadata = ?
        WHERE key = ?
        """
        metadata_str = json.dumps(metadata)
        self.conn.execute(query, (metadata_str, key))
        self.conn.commit()
        return f"Added tag '{tag}' to memory '{key}'."
    
    def remove_tag(self, key, tag):
        """Remove a tag from an existing memory."""
        memory = self.retrieve(key)
        if memory == "No memory found":
            return "Memory not found"

        metadata = memory["metadata"]
        tags = metadata.get("tags", [])
        if tag not in tags:
            return f"Tag '{tag}' not found in memory '{key}'."

        tags.remove(tag)
        metadata["tags"] = tags

        # Update the memory without the removed tag
        query = """
        UPDATE declarative_memory
        SET metadata = ?
        WHERE key = ?
        """
        metadata_str = json.dumps(metadata)
        self.conn.execute(query, (metadata_str, key))
        self.conn.commit()
        return f"Removed tag '{tag}' from memory '{key}'."
    

    def clear_memory_by_priority(self, priority="low", max_age_days=30):
        """Clear memories of a specific priority that are older than the max age."""
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=max_age_days)).isoformat()
        query = """
        DELETE FROM declarative_memory
        WHERE json_extract(metadata, '$.priority') = ?
        AND json_extract(metadata, '$.timestamp') < ?
        """
        self.conn.execute(query, (priority, cutoff_date))
        self.conn.commit()
        return f"Cleared all {priority} priority memories older than {max_age_days} days."

    def clear_low_importance(self, min_importance=5):
        """Clear memories with importance below a certain threshold."""
        query = """
        DELETE FROM declarative_memory
        WHERE CAST(json_extract(metadata, '$.importance') AS INTEGER) < ?
        """
        self.conn.execute(query, (min_importance,))
        self.conn.commit()
        return f"Cleared all memories with importance below {min_importance}." 
    
    def log_error(self, message, exception):
        """Log errors for debugging."""
        error_message = f"{message}: {str(exception)}"
        print(error_message)  # Replace with logging to a file if needed 
      

    def close(self):
        self.conn.close()

# Load configuration from agents.yaml
def load_agent_config(agent_name):
    config_path = Path("config/agents.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file {config_path} not found.")
    
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    
    return config.get(agent_name, {})


# Initialize Hippocampus Agent from YAML
hippocampus_config = load_agent_config("hippocampus")

hippocampus_agent = Agent(
    role=hippocampus_config["role"],
    goal=hippocampus_config["goal"],
    backstory=hippocampus_config["backstory"],
    tools=hippocampus_config.get("tools", []),
    verbose=hippocampus_config.get("verbose", False),
    cache=hippocampus_config.get("cache", False),
    max_iter=hippocampus_config.get("max_iter", 10),
    allow_code_execution=hippocampus_config.get("allow_code_execution", False),
    use_system_prompt=hippocampus_config.get("use_system_prompt", True),
    respect_context_window=hippocampus_config.get("respect_context_window", True),
    max_retry_limit=hippocampus_config.get("max_retry_limit", 2),
)
