from src.plugin_manager import hookimpl


class ComplexProblemSolvingPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Generates prompts for solving complex, multifaceted problems requiring diverse expertise."""
        return f"""
        Analyze and develop a comprehensive solution for the following complex problem:

        Objective: {objective}

        Break down this problem into several key areas of focus. For each area:
        1. Identify the core challenges and opportunities
        2. Propose potential solutions or strategies
        3. Consider interdependencies with other areas
        4. Suggest metrics for measuring success

        Your analysis should cover multiple perspectives, such as:
        - Strategic implications
        - Financial considerations
        - Operational logistics
        - Market dynamics
        - Technological aspects
        - Human resources impact

        Provide a holistic approach that addresses the complexity of the problem while ensuring all components work together cohesively.
        """


complex_problem_solving_plugin = ComplexProblemSolvingPlugin()
