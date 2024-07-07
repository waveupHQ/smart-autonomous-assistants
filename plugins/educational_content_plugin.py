from src.plugin_manager import hookimpl


class EducationalContentPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Aids in developing comprehensive educational materials and lesson plans."""
        return f"""
        Develop comprehensive educational content for the following topic:

        Objective: {objective}

        Create a detailed plan for educational content that covers the following aspects:

        1. Learning Objectives:
           - Define clear, measurable learning outcomes
           - Align objectives with relevant educational standards
           - Consider cognitive, affective, and psychomotor domains

        2. Content Outline:
           - Break down the topic into main themes and subtopics
           - Ensure a logical progression of ideas
           - Include key concepts, theories, and practical applications

        3. Historical Context:
           - Provide relevant historical background
           - Highlight significant developments or changes in understanding
           - Connect historical context to current knowledge

        4. Theoretical Concepts:
           - Explain core theories or models related to the topic
           - Compare and contrast different theoretical approaches
           - Discuss the evolution of theoretical understanding

        5. Practical Applications:
           - Provide real-world examples and case studies
           - Include hands-on activities or experiments
           - Discuss current and potential future applications

        6. Interdisciplinary Connections:
           - Identify links to other subjects or fields of study
           - Explore how the topic relates to broader themes or global issues
           - Encourage critical thinking across disciplines

        7. Multimedia Resources:
           - Suggest relevant videos, animations, or simulations
           - Recommend interactive tools or websites
           - Include ideas for infographics or visual aids

        8. Assessment Strategies:
           - Develop diverse assessment methods (e.g., quizzes, projects, discussions)
           - Include both formative and summative assessments
           - Align assessments with learning objectives

        9. Differentiation and Accessibility:
           - Provide strategies for adapting content to different learning styles
           - Suggest modifications for various ability levels
           - Ensure content is accessible to learners with diverse needs

        10. Extended Learning:
            - Recommend additional resources for further study
            - Suggest topics for independent research or projects
            - Provide discussion questions to encourage deeper exploration

        Ensure the educational content is comprehensive, engaging, and adaptable to different learning environments and student needs. Consider how to balance theoretical knowledge with practical skills and critical thinking development.
        """


educational_content_plugin = EducationalContentPlugin()
