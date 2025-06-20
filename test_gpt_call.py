from core.context import Context
from core.gpt_brain import GPTBrain
from brokers.dhan_client import DhanClient

def test_gpt_dhan():
    # Initialize context and clients
    context = Context()
    gpt = GPTBrain(api_key=context.openai_key)
    dhan = DhanClient(context)

    prompt = "Check my Dhan funds and portfolio."

    # Get GPT response
    response = gpt.get_response(prompt)

    # Check if GPT mentions funds
    if "fund" in response.lower():
        return self.dhan.http.get("/fundlimit")
        print("✅ Funds:", result)

    # Check if GPT mentions portfolio or holdings
    if "portfolio" in response.lower() or "holding" in response.lower():
        result = dhan.portfolio.get_holdings()
        print("✅ Portfolio:", result)

if __name__ == "__main__":
    test_gpt_dhan()
