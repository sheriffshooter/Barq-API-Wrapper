from google import genai
from google.genai import types

class Gemini:
    """Gemini wrapper with a lot of abstractions."""

    def __init__(self, apiKeys, context=""):
        """Clones apiKeys. Use internal functions cycle and addAPIKey to modify internal list.

        Args:
            context (str): A message sent with every query to gemini
        """

        if len(apiKeys) < 1:
            print("Failed to init Gemini, not enough api keys")
        
        self.apiKeys = apiKeys.copy()
        self.client = genai.Client(api_key = self.apiKeys[0], http_options = types.HttpOptions(api_version = "v1alpha"))
        self.context = context

    def cycle(self):
        """Cycles the apiKeys list."""

        firstItem = self.apiKeys.pop(0)
        self.apiKeys.append(firstItem)

    def addAPIKey(self, apiKey):
        """Adds an api key to the apiKeys list."""

        self.apiKeys.append(apiKey)
    
    def query(self, query, model="gemini-2.0-flash-001", includeContext=True):
        """Queries gemini with a message. Expects the caller to handle exceptions.

        Args:
            includeContext (bool): Include the context?

        Returns:
            str: Gemini's response.
        """

        if includeContext:
            query = f"{self.context}{query}"

        response = self.client.models.generate_content(model=model, contents=query)

        return response.text
        
