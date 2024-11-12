def get_system_prompt(context: str):
    return fr"""
    You are a helpful assistant.
    You are given a conversation history (context) and you will receive a user message.
    Your task is to respond to the user message based on the conversation history.
    <context>
    {context}
    </context>
    """
