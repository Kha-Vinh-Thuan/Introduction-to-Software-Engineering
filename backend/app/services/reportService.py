from app.agent.orchestrator import AgentOrchestrator


class ReportService:
    def __init__(self):
        self.agentOrchestrator = AgentOrchestrator()

    async def generateWeeklyReport(self) -> dict:
        prompt = (
            "Generate a comprehensive weekly report. "
            "Use the generate_weekly_report skill: "
            "1) list all tables, "
            "2) query data from the last 7 days, "
            "3) calculate top metrics, "
            "4) return a structured Markdown report."
        )
        return await self.agentOrchestrator.run(prompt, [])
