import os
import httpx
import asyncio
from google import genai
from google.genai import types as gemini_types
from httpx import HTTPStatusError, ConnectError

# --- Configuration ---
OPENAI_CHAT_MODEL = 'gpt-3.5-turbo'
GEMINI_CHAT_MODEL = 'gemini-2.5-flash'
OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'
GEMINI_EMBEDDING_MODEL = 'text-embedding-004' 

# --- Core API Calls (Individual Provider Functions) ---

async def _generate_text_openai(api_key: str, prompt: str, model: str = OPENAI_CHAT_MODEL) -> str:
    """Internal function to call the OpenAI Chat Completion API."""
    if not api_key:
        raise ValueError("OpenAI API key is missing or invalid.")
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.7,
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)
        r.raise_for_status() 
        data = r.json()
        return data['choices'][0]['message']['content']


from google.genai import types as gemini_types # Ensure this is imported
from google.genai.types import HarmCategory, HarmBlockThreshold # Import these specific enums

def _generate_text_gemini(api_key: str, prompt: str, model: str = GEMINI_CHAT_MODEL) -> str:
    """Internal synchronous function to call the Gemini API using the SDK with relaxed safety settings."""
    if not api_key:
        raise ValueError("Gemini API key is missing or invalid.") 

    try:
        client = genai.Client(api_key=api_key)
        
        # --- START OF MODIFICATION: RELAX SAFETY SETTINGS ---
        safety_settings = [
            gemini_types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            gemini_types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            gemini_types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            gemini_types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
        ]
        
        config = gemini_types.GenerateContentConfig(
          temperature=0.7,
          safety_settings=safety_settings
          # Note: max_output_tokens is now unset (or implicitly high)
)
        # --- END OF MODIFICATION ---
        
        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=config,
        )
        
        if not response.text:
            # Check the actual finish reason if it's still blocked
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "N/A"
            safety_ratings = response.candidates[0].safety_ratings if response.candidates else "N/A"
            
            print(f"DEBUG: Gemini blocked content. Finish Reason: {finish_reason}, Safety: {safety_ratings}")
            raise RuntimeError("Gemini API returned no text (Content Blocked).")

        return response.text
    
    except Exception as e:
        error_type = e.__class__.__name__
        error_details = str(e)
        print(f"ADAPTER DEBUG CONSOLE: Real Gemini SDK Error: {error_type}: {error_details}")
        raise RuntimeError(f"Gemini SDK failed: {error_type} - {error_details}")

async def _get_embeddings_openai(api_key: str, text: str, model: str = OPENAI_EMBEDDING_MODEL) -> list[float]:
    """Internal function to get embeddings from OpenAI."""
    if not api_key:
        raise ValueError("OpenAI API key is missing or invalid.")
        
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            'https://api.openai.com/v1/embeddings', 
            json={"model": model, "input": text}, 
            headers=headers
        )
        r.raise_for_status()
        data = r.json()
        return data['data'][0]['embedding']


def _get_embeddings_gemini(api_key: str, text: str, model: str = GEMINI_EMBEDDING_MODEL) -> list[float]:
    """Internal synchronous function to get embeddings from Gemini."""
    if not api_key:
        raise ValueError("Gemini API key is missing or invalid.")

    try:
        client = genai.Client(api_key=api_key)
        result = client.models.embed_content(
            model=model,
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result.embedding
    except Exception as e:
        raise RuntimeError(f"Gemini Embeddings SDK failed: {e.__class__.__name__} - {str(e)}")

# --- Main Adapter Functions (with Failover) ---

async def generate_text(openai_key: str, gemini_key: str, prompt: str, model: str = OPENAI_CHAT_MODEL) -> str:
    """
    Primary AI generation function with failover.
    Attempts to use OpenAI first. If it fails, falls back to Gemini.
    """
    last_error = None

    # 1. Primary Attempt: OpenAI
    if openai_key:
        try:
            print("Adapter: Attempting OpenAI (Primary)...")
            return await _generate_text_openai(openai_key, prompt, model)
        except (HTTPStatusError, ConnectError, ValueError) as e:
            # **DEBUGGING LINE 3:** Log specific OpenAI network/status error
            error_details = str(e)
            if isinstance(e, HTTPStatusError):
                error_details = f"{e.response.status_code} {e.response.reason_phrase}"
            
            last_error = f"OpenAI failed: {e.__class__.__name__} ({error_details})"
            print(f"Adapter: ❌ {last_error}. Falling back to Gemini.")
        except Exception as e:
            last_error = f"OpenAI failed: {e.__class__.__name__}"
            print(f"Adapter: ❌ {last_error}. Falling back to Gemini.")
    else:
        print("Adapter: OpenAI key missing. Skipping primary attempt.")

    # 2. Backup Attempt: Gemini
    if gemini_key:
        try:
            print("Adapter: Attempting Gemini (Backup)...")
            # Run the synchronous Gemini call in a thread pool
            return await asyncio.to_thread(_generate_text_gemini, gemini_key, prompt, GEMINI_CHAT_MODEL)
        except Exception as e_backup:
            # The error raised from _generate_text_gemini (which includes the specific reason) is caught here.
            last_error = f"Gemini also failed: {e_backup}" 
            print(f"Adapter: ❌ {last_error}.")
    else:
        print("Adapter: Gemini key also missing. No backup possible.")

    # 3. Final Failure
    raise RuntimeError(f"All providers failed to generate text. Last error: {last_error or 'No keys provided.'}")


async def get_embeddings(openai_key: str, gemini_key: str, text: str) -> list[float]:
    """
    Primary embedding function with failover.
    Attempts to use OpenAI first. If it fails, falls back to Gemini.
    """
    last_error = None
    
    # 1. Primary Attempt: OpenAI
    if openai_key:
        try:
            print("Adapter: Attempting OpenAI Embeddings (Primary)...")
            return await _get_embeddings_openai(openai_key, text)
        except (HTTPStatusError, ConnectError, ValueError) as e:
            error_details = str(e)
            if isinstance(e, HTTPStatusError):
                error_details = f"{e.response.status_code} {e.response.reason_phrase}"
            
            last_error = f"OpenAI Embeddings failed: {e.__class__.__name__} ({error_details})"
            print(f"Adapter: ❌ {last_error}. Falling back to Gemini.")
        except Exception as e:
            last_error = f"OpenAI Embeddings failed: {e.__class__.__name__}"
            print(f"Adapter: ❌ {last_error}. Falling back to Gemini.")
    else:
        print("Adapter: OpenAI key missing for embeddings. Skipping primary attempt.")

    # 2. Backup Attempt: Gemini
    if gemini_key:
        try:
            print("Adapter: Attempting Gemini Embeddings (Backup)...")
            return await asyncio.to_thread(_get_embeddings_gemini, gemini_key, text)
        except Exception as e_backup:
            last_error = f"Gemini Embeddings also failed: {e_backup}" 
            print(f"Adapter: ❌ {last_error}.")
    else:
        print("Adapter: Gemini key also missing. No backup possible for embeddings.")

    # 3. Final Failure
    raise RuntimeError(f"All providers failed to generate embeddings. Last error: {last_error or 'No keys provided.'}")