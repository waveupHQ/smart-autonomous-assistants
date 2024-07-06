from src.plugin_manager import hookimpl


class CustomerSupportPlugin:
    @hookimpl
    def get_use_case_prompt(self, objective: str) -> str:
        """Helps handle complex customer inquiries requiring input from multiple departments."""
        return f"""
        Develop a comprehensive response strategy for the following customer support scenario:

        Objective: {objective}

        Create a detailed plan to address this complex customer inquiry, considering the following aspects:

        1. Issue Understanding:
           - Break down the customer's problem into its core components
           - Identify which departments or areas of expertise are involved
           - Prioritize the issues based on urgency and impact

        2. Information Gathering:
           - List the key questions to ask the customer for clarification
           - Identify the internal sources of information needed (e.g., documentation, databases)
           - Outline a process for collecting input from different departments

        3. Technical Support:
           - Provide step-by-step troubleshooting instructions
           - Suggest potential solutions based on common issues
           - Outline escalation procedures for complex technical problems

        4. Billing and Account Management:
           - Address any billing-related concerns
           - Explain relevant policies and procedures
           - Suggest potential account adjustments or solutions

        5. Product Functionality:
           - Clarify product features and capabilities
           - Provide usage instructions or best practices
           - Suggest alternative features or workarounds if needed

        6. Cross-departmental Coordination:
           - Outline a workflow for involving multiple departments
           - Suggest methods for efficient information sharing between teams
           - Define responsibilities and timelines for each involved department

        7. Customer Communication:
           - Draft a clear and empathetic initial response to the customer
           - Plan follow-up communications and progress updates
           - Prepare answers to potential follow-up questions

        8. Resolution and Follow-up:
           - Outline steps to implement the solution
           - Create a plan to verify the customer's satisfaction
           - Suggest proactive measures to prevent similar issues in the future

        9. Knowledge Base Update:
           - Identify key learnings from this case
           - Suggest updates to internal documentation or FAQs
           - Outline training recommendations for support staff

        Ensure the response strategy is comprehensive, customer-centric, and efficiently utilizes internal resources to resolve the complex inquiry.
        """


customer_support_plugin = CustomerSupportPlugin()
