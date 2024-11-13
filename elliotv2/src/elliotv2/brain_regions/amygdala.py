import sqlite3
import datetime
import json
import os

class Amygdala:
    def __init__(self, logger=None, db_file="data/amygdala.db", **kwargs):
        self.logger = logger
        self.db_file = db_file
        self.role = kwargs.get("role", "Emotional Memory")
        self.goal = kwargs.get("goal", "Handle emotionally weighted memories and advisory signals.")
        self.verbose = kwargs.get("verbose", False)
        self.conn = self.initialize_db(db_file)

    def initialize_db(self, db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file)

        query = """
        CREATE TABLE IF NOT EXISTS emotional_memory (
            memory_key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            metadata TEXT,
            sentiment TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()
        return self.conn

    def store_emotional_memory(self, memory_key, value, metadata=None, sentiment="neutral"):
        try:
            if not memory_key or not isinstance(memory_key, str):
                raise ValueError("Memory key must be a non-empty string.")

            metadata = metadata or {}
            metadata.setdefault("priority", "normal")
            metadata.setdefault("timestamp", datetime.datetime.now().isoformat())
            metadata.setdefault("tags", [])

            value_str = json.dumps(value) if not isinstance(value, str) else value
            metadata_str = json.dumps(metadata)

            query = """
            INSERT OR REPLACE INTO emotional_memory (memory_key, value, metadata, sentiment)
            VALUES (?, ?, ?, ?)
            """
            self.conn.execute(query, (memory_key, value_str, metadata_str, sentiment))
            self.conn.commit()
            print(f"Inserted memory: {memory_key}, {value_str}, {metadata_str}, {sentiment}")
            return f"Stored emotional memory: {memory_key} -> {value} with sentiment {sentiment}"
        except Exception as e:
            self.logger.log_error("Amygdala.store_emotional_memory", str(e))
            return f"Error storing emotional memory: {e}"

    def retrieve_emotional_memory(self, memory_key):
        try:
            print(f"Attempting to retrieve memory with key: {memory_key}")  # Debug line
            query = "SELECT value, metadata, sentiment FROM emotional_memory WHERE LOWER(memory_key) = LOWER(?)"
            print(f"Executing query: {query} with key: {memory_key}")
            cursor = self.conn.execute(query, (memory_key,))
            result = cursor.fetchone()

            if result:
                value_str, metadata_str, sentiment = result
                value = json.loads(value_str)
                metadata = json.loads(metadata_str)
                return {"value": value, "metadata": metadata, "sentiment": sentiment}
            else:
                return "No memory found"
        except Exception as e:
            self.logger.log_error("Amygdala.retrieve_emotional_memory", str(e))
            return f"Error retrieving emotional memory: {e}"
            

    def adjust_priorities(self, orchestrator):
        """Influence task/memory priorities dynamically."""
        try:
            memories = self.retrieve_emotional_memory(min_intensity=5.0)
            for memory in memories:
                # Example: Boost priority of tasks/memories with high emotional weight
                if orchestrator and hasattr(orchestrator, "adjust_task_priority"):
                    orchestrator.adjust_task_priority(memory["memory_key"], weight=memory["intensity"])
            if self.verbose:
                print("Adjusted priorities based on emotional context.")
        except Exception as e:
            return f"Error adjusting priorities: {e}"
        
    def view_all_emotions(self):
        query = "SELECT * FROM emotional_memory"
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    def close(self):
        self.conn.close()
