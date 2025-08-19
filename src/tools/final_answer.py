from src.tools.tools import AsyncTool, ToolResult
from src.registry import TOOL

@TOOL.register_module(name="final_answer_tool", force=True)
class FinalAnswerTool(AsyncTool):
    name = "final_answer_tool"
    description = "Provides a final answer to the given problem."
    parameters = {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "The final answer to the problem.",
            },
        },
        "required": ["answer"],
    }
    output_type = "any"

    def __init__(self):
        super().__init__()
        # Initialize inputs for AsyncTool compatibility
        self.inputs = {
            "answer": {
                "type": "string",
                "description": "The final answer to the problem."
            }
        }
        self.is_initialized = True

    async def forward(self, answer: str) -> ToolResult:
        result = ToolResult(
            output=answer,
            error=None,
        )
        return result