from src.plugin_manager import hookimpl


class InnovationManagementPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Assists in developing strategies to foster, manage, and implement innovation within an organization."""
        return f"""
        Develop a comprehensive innovation management strategy for the following objective:

        Objective: {objective}

        Create a detailed innovation management plan that covers the following aspects:

        1. Innovation Vision and Goals:
           - Define a clear vision for innovation within the organization
           - Set specific, measurable innovation goals aligned with business objectives
           - Identify key areas or domains for innovation focus

        2. Innovation Culture:
           - Outline strategies to foster a culture of creativity and experimentation
           - Suggest ways to encourage risk-taking and learning from failures
           - Develop approaches to break down silos and promote cross-functional collaboration

        3. Idea Generation and Capture:
           - Design processes for soliciting ideas from employees, customers, and partners
           - Suggest tools or platforms for capturing and organizing ideas
           - Develop criteria for initial idea evaluation and prioritization

        4. Innovation Portfolio Management:
           - Create a framework for categorizing innovation projects (e.g., core, adjacent, transformational)
           - Develop a balanced portfolio approach to manage risk and potential returns
           - Suggest methods for allocating resources across different types of innovation

        5. Innovation Process:
           - Outline a stage-gate process for moving ideas from concept to implementation
           - Define key milestones, deliverables, and decision points in the innovation journey
           - Suggest agile methodologies for rapid prototyping and iterative development

        6. Open Innovation Strategies:
           - Develop approaches for engaging external partners in the innovation process
           - Suggest methods for identifying and managing strategic partnerships or collaborations
           - Outline strategies for participating in innovation ecosystems or clusters

        7. Innovation Metrics and KPIs:
           - Define key performance indicators to measure innovation success
           - Suggest both leading and lagging indicators for innovation performance
           - Develop a dashboard for tracking and reporting innovation metrics

        8. Funding and Resource Allocation:
           - Outline strategies for securing funding for innovation projects
           - Suggest models for allocating resources (e.g., dedicated innovation budget, time allocation)
           - Develop approaches for managing innovation project portfolios

        9. Talent Management for Innovation:
           - Identify key skills and competencies needed for innovation
           - Suggest strategies for attracting, developing, and retaining innovative talent
           - Outline approaches for building diverse, cross-functional innovation teams

        10. Innovation Governance:
            - Design an innovation governance structure (e.g., innovation council, chief innovation officer)
            - Define roles and responsibilities for managing the innovation process
            - Develop decision-making frameworks for innovation investments

        11. Intellectual Property Strategy:
            - Outline approaches for protecting and managing intellectual property
            - Suggest strategies for leveraging IP for competitive advantage
            - Develop guidelines for IP sharing in collaborative innovation efforts

        12. Innovation Training and Education:
            - Design programs to develop innovation skills across the organization
            - Suggest methods for sharing innovation best practices and case studies
            - Outline approaches for continuous learning and skill development in innovation

        13. Technology and Tools:
            - Recommend technologies to support the innovation process (e.g., idea management software, collaboration tools)
            - Suggest approaches for leveraging emerging technologies in the innovation process
            - Outline strategies for maintaining technological competitiveness

        14. Innovation Communication and Recognition:
            - Develop strategies for communicating innovation successes and learnings
            - Suggest approaches for recognizing and rewarding innovative contributions
            - Outline methods for storytelling and celebrating innovation within the organization

        15. Scaling and Implementation:
            - Design processes for scaling successful innovations
            - Suggest strategies for overcoming resistance to change and driving adoption
            - Develop approaches for integrating innovations into existing operations

        Ensure the innovation management strategy is comprehensive, adaptable to the organization's specific context, and provides actionable plans for fostering and managing innovation effectively.
        """


innovation_management_plugin = InnovationManagementPlugin()
