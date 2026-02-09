from adapters.graph_adapter import get_graph_engine

class GraduationSystem:
    def __init__(self):
        self.graph = get_graph_engine()
        self.main_character_threshold = 0.15  # PageRank threshold (approx 1/7th of attention)

    def evaluate_character(self, name: str) -> bool:
        """
        Determines if a character should graduate to 'Main Cast'.
        Returns True if they are important enough for a unique voice.
        """
        score = self.graph.get_character_importance(name)
        
        # PageRank scores sum to 1.0. 
        # For a small cast (e.g. 5-10 characters), an effectively "main" character 
        # should have a significant share (e.g. > 10-15%).
        # We'll use a dynamic threshold approach in the future, 
        # but for now 0.15 is a reasonable baseline for "Main Cast".
        
        print(f"[Graduation] {name}: Score {score:.4f} / Threshold {self.main_character_threshold}")
        
        return score >= self.main_character_threshold

# Singleton
_grad_system = None
def get_graduation_system():
    global _grad_system
    if _grad_system is None:
        _grad_system = GraduationSystem()
    return _grad_system
