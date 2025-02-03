import asyncio
from mistralai import Mistral
from settings import APIKEY


async def main_mistral(content):
    mistral = Mistral(api_key=APIKEY.strip())


    try:
        res = await mistral.chat.complete_async(
            model="mistral-small-latest",
            messages=[
                {
                    "content": content,
                    "role": "user",
                },
            ],
            stream=False
        )

        # Ensure the response structure is correct
        if not res.choices or not res.choices[0].message.content:
            raise ValueError("Invalid or empty response received from API")

        # Return the first message content
        return res.choices[0].message.content

    except Exception as e:
        # Handle exceptions and print error
        print(f"An error occurred: {e}")
        return None


# Example of calling the async main function
if __name__ == "__main__":
    content = "Hello! Can you explain the asynchronous usage of APIs?"
    result = asyncio.run(main(content))
    print(result)
