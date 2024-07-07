from src.plugin_manager import hookimpl


class ProjectPlanningPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Assists in creating detailed project plans covering all aspects of project management."""
        return f"""
        Develop a comprehensive project plan for the following objective:

        Objective: {objective}

        Create a detailed project plan that covers the following areas:

        1. Project Scope and Objectives:
           - Clear definition of project goals
           - Key deliverables and success criteria
           - Project boundaries and constraints

        2. Stakeholder Analysis:
           - Identify key stakeholders
           - Define roles and responsibilities
           - Communication plan for each stakeholder group

        3. Work Breakdown Structure (WBS):
           - Break down the project into manageable tasks
           - Identify major milestones
           - Estimate time and resources for each task

        4. Timeline and Schedule:
           - Develop a Gantt chart or similar timeline visualization
           - Identify critical path and dependencies
           - Include buffer time for unforeseen circumstances

        5. Resource Allocation:
           - Human resources required (roles and skills)
           - Material and equipment needs
           - Budget allocation for each project phase

        6. Risk Management:
           - Identify potential risks and their impact
           - Develop mitigation strategies for each risk
           - Create a contingency plan for high-priority risks

        7. Quality Management:
           - Define quality standards and metrics
           - Outline quality control processes
           - Plan for regular quality audits

        8. Communication Plan:
           - Establish communication channels and frequency
           - Define reporting structure and templates
           - Plan for status updates and review meetings

        9. Change Management:
           - Process for handling change requests
           - Impact assessment procedures
           - Approval and implementation guidelines

        10. Monitoring and Evaluation:
            - Key performance indicators (KPIs)
            - Tools and methods for tracking progress
            - Plan for regular project evaluations and adjustments

        Ensure the project plan is comprehensive, realistic, and aligned with the overall objective. Consider interdependencies between different aspects of the project and provide strategies for successful execution.
        """


project_planning_plugin = ProjectPlanningPlugin()
