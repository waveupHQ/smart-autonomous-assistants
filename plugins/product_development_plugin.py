from src.plugin_manager import hookimpl


class ProductDevelopmentPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Guides through the process of developing new products from ideation to launch."""
        return f"""
        Develop a comprehensive plan for the following product:

        Objective: {objective}

        Create a detailed product development strategy covering the following areas:

        1. Market Analysis:
           - Target audience and their needs
           - Competitive landscape
           - Market trends and opportunities

        2. Product Conceptualization:
           - Core features and functionalities
           - Unique selling propositions
           - Product vision and long-term roadmap

        3. Technical Architecture:
           - High-level system design
           - Technology stack recommendations
           - Scalability and performance considerations

        4. User Experience (UX) Design:
           - User personas and journey maps
           - Key user interfaces and interactions
           - Accessibility and usability guidelines

        5. Development Planning:
           - Sprint planning and milestones
           - Resource allocation
           - Risk assessment and mitigation strategies

        6. Quality Assurance:
           - Testing strategies (unit, integration, user acceptance)
           - Performance benchmarks
           - Security and compliance considerations

        7. Launch Strategy:
           - Go-to-market plan
           - Marketing and promotion strategies
           - Customer onboarding and support plans

        8. Post-launch Considerations:
           - Maintenance and update schedules
           - User feedback collection and analysis
           - Performance monitoring and optimization

        Ensure each area is thoroughly addressed and consider interdependencies between different aspects of the product development process.
        """


product_development_plugin = ProductDevelopmentPlugin()
