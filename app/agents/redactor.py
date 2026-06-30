
from app.core.nvidia_client import client

def redact_message(context: dict, prompt: str, model: str = "meta/llama-3.1-70b-instruct"):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(context)},
        ],
        temperature=0.3,
        max_tokens=120,
    )
    return resp.choices[0].message.content