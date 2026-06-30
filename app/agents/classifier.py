from app.core.nvidia_client import client

def classify_event(event: dict, prompt: str, model: str = "meta/llama-3.1-70b-instruct"):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(event)},
        ],
        temperature=0.2,
        max_tokens=300,
    )
    return resp.choices[0].message.content