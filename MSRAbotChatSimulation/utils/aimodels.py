import openai
import json

with open('./secrets.json') as f:
    credentials = json.load(f)


class Davinci3:
    def __init__(self):      
        openai.api_type = "azure"
        openai.api_base = credentials["chatengine"]["AZURE_OPENAI_ENDPOINT"]
        openai.api_version = "2023-03-15-preview"
        openai.api_key = credentials["chatengine"]["AZURE_OPENAI_KEY"]
        self.messages = []
        self.max_token_length_input = 2048
        self.max_token_length_total = 4096
        self.prompt = "You are an excellent chat bot, named MSRAbot. " + \
            "Please respond to the current message accurately, taking into account your knowledge and our previous conversations."

    def generate(self, message):
        deployment_name = credentials["chatengine"]["AZURE_OPENAI_DEPLOYMENT_NAME_DAVINCI3"]
        # cut off long input
        if len(message) > self.max_token_length_input:
            message = message[:self.max_token_length_input]

        # check the word count of the prompt message. If its more than 2048,
        # then split it into multiple prompts
        history_input = '\n Previous conversations:' + "\n".join(self.messages)
        message_input = '\n Current message:' + message

        # cut off if history data gets long
        max_token_length = self.max_token_length_total - \
            len(self.prompt) - len(history_input)
        if len(history_input) > max_token_length:
            history_input = history_input[-max_token_length:]

        prompt_message = self.prompt + history_input + message_input

        response = openai.Completion.create(engine=deployment_name,
                                            prompt=prompt_message,
                                            temperature=0.1,
                                            max_tokens=50,
                                            top_p=1.0,
                                            frequency_penalty=0.5,
                                            presence_penalty=0.5)
        text = response['choices'][0]['text'].replace(
            '\n', '').replace(' .', '.').strip()
        self.messages.append(message)
        self.messages.append(text)
        return text


class ChatGPT:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = credentials["chatengine"]["AZURE_OPENAI_ENDPOINT"]
        openai.api_version = "2023-03-15-preview"
        openai.api_key = credentials["chatengine"]["AZURE_OPENAI_KEY"]
        self.messages = []
        self.max_token_length = 16000
        self.system_message = "<|im_start|>system\n" + \
            "You are an excellent chat bot, named MSRAbot. " + \
            "You are embodied with a small robot, which makes lively gestures in response to your speech. " + \
            "Please keep conversations with the user by responding with short English phrases. " + \
            "The response can be composed of several sentences, but every sentence " + \
            "should be definitely short and less than 12 words.\n" + \
            "Answer in English in any situation.\n" + \
            "<|im_end|>"
    # See
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt#chatml

    def create_prompt(self, messages):
        prompt = self.system_message
        for message in messages:
            if message['sender'] == 'user':
                prompt += f"\n<|im_start|>{message['sender']}\n{message['text']}" + \
                    "(answer in English)" + "\n<|im_end|>"
            else:
                prompt += f"\n<|im_start|>{message['sender']}\n{message['text']}\n<|im_end|>"
        prompt += "\n<|im_start|>assistant\n"
        return prompt

    def generate(self, message):
        deployment_name = credentials["chatengine"]["AZURE_OPENAI_DEPLOYMENT_NAME_CHATGPT"]
        # Remove unsafe user inputs. May need further refinement in the future.
        if message.find('<|im_start|>') != -1:
            message = message.replace('<|im_start|>', '')
        if message.find('<|im_end|>') != -1:
            message = message.replace('<|im_end|>', '')

        # cut off long input
        if len(message) > self.max_token_length:
            message = message[:self.max_token_length]  
        print(self.messages)      
        self.messages.append({"role": "system", "content": "You are an AI assistant that helps people find information.Please response no later than 12 words"})
        self.messages.append({"role": "user", "content": message})

        """ response = openai.Completion.create(
            engine=deployment_name,
            prompt=self.create_prompt(self.messages),
            temperature=0,
            max_tokens=100,
            top_p=0.5,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            stop=["<|im_end|>"])
        text = response['choices'][0]['text'].replace(
            '\n', '').replace(' .', '.').strip()
        self.messages.append({"sender": "assistant", "text": text}) """
        
    
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo-16k",
            messages = self.messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        
        text = json.loads(str(response['choices'][0]['message']))
        print(text["content"])
        self.messages.append({"role": "assistant", "content": text["content"]})
        return text["content"]
