from core.context import Context
from core.gpt_brain import GPTBrain
from brokers.dhan_client import DhanClient

def test_gpt_dhan():
    context = Context()
    gpt = GPTBrain(api_key=context.openai_key)
    dhan = DhanClient(context)

    prompt = "Check my Dhan funds and portfolio."

    response = gpt.generate(prompt)
    
    if "funds" in response.lower():
        result = dhan.funds.get()
        print("✅ Funds:", result)

    if "portfolio" in response.lower() or "holdings" in response.lower():
        result = dhan.portfolio()
        print("✅ Portfolio:", result)

if __name__ == "__main__":
    test_gpt_dhan()
