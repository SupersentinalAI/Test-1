import openai
import logging
import time

class GPTBrain:
    def __init__(self, api_key, model="gpt-4o", timeout=30, max_retries=3):
        """Initialize GPTBrain for making requests to OpenAI."""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        logging.basicConfig(level=logging.INFO)

    def get_response(self, prompt):
        """Send a prompt to OpenAI and return the response."""
        retries = 0
        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    timeout=self.timeout
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                retries += 1
                logging.error(f"GPT error: {e}, retrying {retries}/{self.max_retries}")
                time.sleep(2)

        raise Exception("Max retries exceeded for GPT request.")
