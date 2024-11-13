
class Agent:
    def __init__(self, role, instance):
        self.role = role
        self.instance = instance
        
    def process(self, method_name, *args, **kwargs):
        """Dynamically call a method on the wrapped instance."""
        method = getattr(self.instance, method_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        return f"Task {method_name} not found for {self.role}"