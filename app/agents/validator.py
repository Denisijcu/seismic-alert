from app.core.nvidia_client import client

def validate_event(payload: dict, prompt: str, model: str = "meta/llama-3.1-70b-instruct"):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(payload)},
        ],
        temperature=0.1,
        max_tokens=200,
    )
    return resp.choices[0].message.content