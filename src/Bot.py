from OpenAIClient import OpenAIClient
import DeveloperMsg
import ast
import TemplateAPICTX

class Bot:
    def __init__(self):
        """
        Initializes the Bot with the OpenAI client and a system message.
        """
        self.client = OpenAIClient()
        self.sys_msg = "You are a helpful assistant."
        self.client.add_user_message(self.sys_msg)

    def start_chat(self):
        """
        Starts the chat loop, allowing the user to send messages and receive responses.
        """
        print("Chatbot is ready! Type 'exit' to end the chat.")
        
        req = {}
        user_input = input("You: ")
        self.client.add_developer_message(DeveloperMsg.get_dev_msg('start_msg', user_input))
        response = self.client.query()
        print("Assistant:", response)
        self.client.clear_messages()
        req['context'] = TemplateAPICTX.ctx
        while user_input.lower() != "exit":           
            req['question'] = user_input
            self.client.add_user_message(str(req))
            response = self.client.query()
            print("Assistant:", response, '\n--------\n')
            print("Assistant:", ast.literal_eval(response)['answer'])
            self.client.add_assistant_message(response)
            user_input = input("You: ")

if __name__ == "__main__":  
    bot = Bot()
    bot.start_chat()

