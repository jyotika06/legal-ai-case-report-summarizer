import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MODEL_API_KEY = os.getenv("MODEL_API_KEY")
MODEL_API_URL = os.getenv("MODEL_API_URL")

if not MODEL_API_KEY or not MODEL_API_URL:
    raise EnvironmentError("MODEL_API_KEY or MODEL_API_URL not set in environment variables")


def call_model(prompt: str, temperature: float = 0.2, timeout: int = 60) -> str:
    """
    Generic AI model inference wrapper.

    This function sends a prompt to the configured language model API
    and returns the generated text output.

    Args:
        prompt (str): Input prompt for model inference
        temperature (float): Creativity level (lower = more deterministic)
        timeout (int): Request timeout in seconds

    Returns:
        str: Model-generated text output

    Raises:
        Exception: If API call fails or returns invalid response
    """

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(
            f"{MODEL_API_URL}?key={MODEL_API_KEY}",
            json=payload,
            timeout=timeout
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Model API request failed: {str(e)}")

    try:
        data = response.json()
    except ValueError:
        raise Exception("Invalid JSON response from model API")

    # Handle API-level error
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown Model API Error"))

    # Validate response structure
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise Exception("Unexpected response structure from model API")