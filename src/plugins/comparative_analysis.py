from src.plugin_manager import hookimpl


class ComparativeAnalysisPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        return f"""
        Conduct a comparative analysis on the following topic:

        Objective: {objective}

        Break down this analysis into several comparison tasks.
        For each task, provide:
        1. A clear aspect or criterion to compare
        2. Detailed instructions on what to investigate for each subject
        3. Suggested methods or sources for gathering comparative data
        4. Any specific points of contrast to focus on

        Your response will guide a thorough comparative analysis, so be specific and comprehensive.
        """


comparative_analysis_plugin = ComparativeAnalysisPlugin()
