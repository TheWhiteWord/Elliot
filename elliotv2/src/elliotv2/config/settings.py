# settings.py

# Placeholder API keys
API_KEYS = {
    "openai": "fake-key-for-compatibility"
}

# Local LLM URLs
LLM_URLS = {
    "prefrontal_cortex": "http://localhost:11434/v1",  # Replace with actual URL for prefrontal cortex
    "hippocampus": "http://localhost:11434/v1",       # Replace with actual URL for hippocampus
    "amygdala": "http://localhost:11434/v1",           # Replace with actual URL for amygdala
    "association_cortex": "http://localhost:11434/v1",           # Replace with actual URL for thalamus
    "cerebellum": "http://localhost:11434/v1",         # Replace with actual URL for cerebellum
}

# Tools Configuration (if needed)
TOOLS = {
    "basic_tools": ["JSONSearchTool", "DirectorySearchTool"],
    "advanced_tools": ["CodeInterpreterTool", "WebsiteSearchTool"],
}

# Default LLM Model Names
LLM_MODELS = {
    "prefrontal_cortex": "hf.co/mradermacher/Llama3-8B-function-calling-uncensored-GGUF:Q8_0",
    "hippocampus": "hf.co/MaziyarPanahi/Llama-3.2-3B-Instruct-uncensored-GGUF:Q8_0",
}
