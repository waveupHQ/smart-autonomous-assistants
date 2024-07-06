from src.plugin_manager import hookimpl


class ContentCreationPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Assists in creating comprehensive, multi-faceted content on various topics."""
        return f"""
        Create comprehensive content on the following topic:

        Objective: {objective}

        Develop a detailed outline for the content, including:
        1. An engaging introduction that sets the context
        2. Main sections, each covering a key aspect of the topic
        3. Subsections that delve into specific details
        4. A conclusion that summarizes key points and provides a call to action

        For each section, consider including:
        - Relevant data and statistics
        - Expert opinions or quotes
        - Case studies or real-world examples
        - Visual elements (describe what kind of charts, graphs, or images would be useful)

        Ensure the content:
        - Is well-researched and factually accurate
        - Presents a balanced view of the topic
        - Engages the target audience effectively
        - Follows a logical flow of ideas
        - Incorporates current trends and future outlooks

        Suggest ways to repurpose this content for different formats (e.g., blog post, white paper, infographic, video script).
        """


content_creation_plugin = ContentCreationPlugin()
