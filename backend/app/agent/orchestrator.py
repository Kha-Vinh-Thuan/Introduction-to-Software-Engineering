import google.generativeai as genai
from app.core.config import settings
from app.agent.tools import TOOL_DEFINITIONS, executeToolCall

SYSTEM_PROMPT = """You are DataPilot, an intelligent database management assistant.

You have access to tools to interact with a SQLite database. When a user asks a question
or makes a request, decide which tools to call to fulfill the request.

RULES:
- Always call list_tables first if you don't know the database structure
- Always call describe_table before writing SQL queries
- Only use SELECT statements in execute_sql — never INSERT, UPDATE, DELETE, DROP
- Respond in the same language the user uses
- For CRUD operations via chat, use the dedicated crud tools (createRecord, updateRecord, deleteRecord)
- Be concise and clear in your responses
"""


class AgentOrchestrator:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            tools=TOOL_DEFINITIONS,
            system_instruction=SYSTEM_PROMPT,
        )

    async def run(self, userMessage: str, conversationHistory: list[dict]) -> dict:
        chat = self.model.start_chat(history=conversationHistory)
        response = chat.send_message(userMessage)

        toolCallsLog = []
        maxIterations = 5
        iteration = 0

        while response.candidates[0].content.parts and iteration < maxIterations:
            hasFunctionCall = any(
                hasattr(part, "function_call")
                for part in response.candidates[0].content.parts
            )
            if not hasFunctionCall:
                break

            functionResponses = []
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call"):
                    toolName = part.function_call.name
                    toolArgs = dict(part.function_call.args)
                    toolResult = executeToolCall(toolName, toolArgs)
                    toolCallsLog.append({"tool": toolName, "args": toolArgs, "result": toolResult})
                    functionResponses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=toolName,
                                response={"result": toolResult},
                            )
                        )
                    )

            response = chat.send_message(functionResponses)
            iteration += 1

        finalText = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text"):
                finalText += part.text

        return {
            "reply": finalText,
            "toolCalls": toolCallsLog,
        }
