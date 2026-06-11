from app.agent.orchestrator import AgentOrchestrator


class ChatService:
    def __init__(self):
        self.agentOrchestrator = AgentOrchestrator()

    async def processMessage(self, message: str, conversationHistory: list[dict]) -> dict:
        return await self.agentOrchestrator.run(message, conversationHistory)
