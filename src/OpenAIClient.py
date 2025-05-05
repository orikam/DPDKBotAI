from openai import OpenAI
import SystemMsg


class OpenAIClient:
    def __init__(self):
        """
        Initializes the OpenAIClient with the API key from the environment and creates the OpenAI client.
        """
        self.client = OpenAI()
        self.messages = []

    def add_user_message(self, message):
        """
        Adds a user message to the list of messages.
        """
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message):
        """
        Adds an assistant message to the list of messages.
        """
        self.messages.append({"role": "assistant", "content": message})

    def add_developer_message(self, message):
        """
        Adds an developer message to the list of messages.
        """
        self.messages.append({"role": "developer", "content": message})

    def query(self, model="gpt-4.1"):
        """
        Sends the messages to the OpenAI API and returns the result.
        """
        try:
            response = self.client.responses.create(
            model = model,
            temperature = 0,
            instructions = SystemMsg.system_message,
            input = self.messages
            )
            return response.output_text
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    
    def clear_messages(self):
        """
        Clears the list of messages.
        """
        self.messages = []