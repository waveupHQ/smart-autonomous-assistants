from src.plugin_manager import hookimpl


class ResearchAnalysisPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Facilitates comprehensive research and analysis on complex topics."""
        return f"""
        Conduct a comprehensive research and analysis on the following topic:

        Objective: {objective}

        Develop a detailed research plan that covers the following aspects:

        1. Background and Context:
           - Historical overview of the topic
           - Current state of knowledge and key debates

        2. Research Questions:
           - Formulate 3-5 key research questions
           - Identify sub-questions for each main question

        3. Methodology:
           - Propose appropriate research methods (quantitative, qualitative, mixed)
           - Identify data sources and collection strategies
           - Outline analysis techniques

        4. Literature Review:
           - Identify key academic papers, books, and reports
           - Summarize main theories and findings
           - Highlight gaps in current research

        5. Data Analysis:
           - Describe how you would analyze the data
           - Suggest visualizations or statistical tests
           - Propose ways to ensure validity and reliability

        6. Multidisciplinary Perspectives:
           - Analyze the topic from various angles (e.g., social, economic, environmental, technological)
           - Consider potential interdisciplinary connections

        7. Ethical Considerations:
           - Identify potential ethical issues in the research
           - Propose mitigation strategies

        8. Potential Impact:
           - Discuss the potential implications of the research
           - Consider short-term and long-term effects
           - Identify stakeholders who might be affected

        9. Future Directions:
           - Suggest areas for future research
           - Discuss potential applications of the findings

        Ensure the research plan is comprehensive, methodologically sound, and addresses the complexity of the topic from multiple perspectives.
        """


research_analysis_plugin = ResearchAnalysisPlugin()
