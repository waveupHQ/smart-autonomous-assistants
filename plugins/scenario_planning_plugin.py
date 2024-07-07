from src.plugin_manager import hookimpl


class ScenarioPlanningPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Guides the process of developing and analyzing multiple future scenarios for strategic decision-making."""
        return f"""
        Develop a comprehensive scenario planning analysis for the following objective:

        Objective: {objective}

        Create a detailed scenario planning process that covers the following aspects:

        1. Focal Issue Identification:
           - Clearly define the central issue or decision to be addressed
           - Specify the time horizon for the scenarios (e.g., 5, 10, or 20 years)
           - Identify the key stakeholders involved

        2. Key Drivers Analysis:
           - Identify the major forces shaping the future environment (PESTLE analysis)
           - Distinguish between predetermined elements and critical uncertainties
           - Prioritize the most impactful and uncertain drivers

        3. Scenario Framework Development:
           - Select two critical uncertainties as axes for a 2x2 scenario matrix
           - Define four distinct, plausible future scenarios
           - Provide a brief narrative description for each scenario

        4. Scenario Detailing:
           For each of the four scenarios, elaborate on:
           - Political landscape
           - Economic conditions
           - Social and demographic trends
           - Technological advancements
           - Legal and regulatory environment
           - Environmental factors

        5. Implications Analysis:
           For each scenario:
           - Identify potential opportunities and threats
           - Analyze the impact on the organization's strategy and operations
           - Consider implications for different stakeholders

        6. Indicator Development:
           - Develop a set of early warning indicators for each scenario
           - Specify trigger points that signal a scenario is becoming more likely

        7. Strategy Development:
           - Identify robust strategies that perform well across multiple scenarios
           - Develop contingency plans for specific scenarios
           - Suggest ways to increase organizational flexibility and adaptability

        8. Scenario Testing:
           - Stress-test current strategies against each scenario
           - Identify potential vulnerabilities and blind spots
           - Suggest modifications to improve strategic resilience

        9. Stakeholder Implications:
           - Analyze how different stakeholders might react in each scenario
           - Identify potential winners and losers in each future
           - Suggest engagement strategies for key stakeholders

        10. Monitoring System:
            - Develop a system for tracking relevant trends and indicators
            - Establish a process for regularly updating and refining scenarios
            - Suggest methods for incorporating scenario insights into ongoing strategic planning

        11. Communication Plan:
            - Outline how to effectively communicate scenarios to different audiences
            - Suggest ways to use scenarios in strategic conversations and decision-making
            - Develop visual aids or other tools to help stakeholders engage with the scenarios

        12. Action Planning:
            - Identify immediate actions based on scenario insights
            - Develop a timeline for strategy implementation and review
            - Suggest ways to maintain strategic flexibility while taking decisive action

        Ensure the scenario planning process is comprehensive, creative yet grounded in current trends, and provides actionable insights for strategic decision-making.
        """


scenario_planning_plugin = ScenarioPlanningPlugin()
