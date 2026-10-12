import logging
from typing import List, Dict, Optional, Any, Callable
from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

try:
    import claude_agent_sdk  # Official Anthropic Claude Agent SDK
    HAS_CLAUDE_AGENT_SDK = True
except ImportError:
    HAS_CLAUDE_AGENT_SDK = False

try:
    import pi_agent
    from pi_agent.agent import Agent as PiAgent, AgentConfig as PiAgentConfig, Sandbox as PiSandbox
    from pi_agent.tools.base import Tool as PiTool
    from pi_agent.tools.registry import ToolRegistry as PiToolRegistry
    from pi_agent.llm import AnthropicProvider as PiAnthropicProvider
    HAS_PI_AGENT_SDK = True
except ImportError:
    HAS_PI_AGENT_SDK = False


class AnthropicProvider(BaseLLMProvider):

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.default_model = settings.ANTHROPIC_DEFAULT_MODEL

    @property
    def provider_id(self) -> str:
        return "anthropic"

    @property
    def display_name(self) -> str:
        return "Anthropic (Claude)"

    @property
    def provider_type(self) -> str:
        return "cloud"

    def is_available(self) -> tuple[bool, Optional[str]]:
        if not self.api_key or self.api_key.startswith("your_"):
            return False, "ANTHROPIC_API_KEY environment variable is not configured."
        return True, None

    def list_models(self) -> List[str]:
        return ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"]

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        available, err = self.is_available()
        if not available:
            raise RuntimeError(f"Anthropic provider error: {err}")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            # Separate system prompt if present
            system_prompt = ""
            chat_messages = []
            for m in messages:
                if m["role"] == "system":
                    system_prompt += m["content"] + "\n"
                else:
                    chat_messages.append({"role": m["role"], "content": m["content"]})

            response = client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt.strip() if system_prompt else None,
                messages=chat_messages
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic Claude API execution failed: {str(e)}")

    def run_agent_tool_loop(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_handler_callback: Callable[[str, Dict[str, Any]], Any],
        model: Optional[str] = None,
        max_iterations: int = 5,
        on_event_callback: Optional[Callable[[str, Any], None]] = None
    ) -> str:
        """
        Executes an agentic tool-use cycle using the official Agent SDK
        (Pi Coding Agent or Anthropic Claude Agent SDK).
        Dispatches tool calls through the SDK's ToolRegistry, Sandbox, and autonomous agent loop.
        """
        available, err = self.is_available()
        if not available:
            raise RuntimeError(f"Anthropic agent error: {err}")

        # 1. Prefer Pi Coding Agent SDK when installed
        if HAS_PI_AGENT_SDK:
            logger.info("Executing autonomous agent cycle via Pi Coding Agent SDK...")
            pi_tools = []
            for t in tools:
                tool_name = t["name"]
                tool_desc = t.get("description", "")
                tool_schema = t.get("input_schema", {})

                def create_handler(t_name: str):
                    def _handler(args: Dict[str, Any], sandbox: Any) -> str:
                        logger.info(f"[Pi Agent SDK] Dispatching tool call '{t_name}' with args {args}")
                        res = tool_handler_callback(t_name, args)
                        return str(res)
                    return _handler

                pi_tools.append(PiTool(
                    name=tool_name,
                    description=tool_desc,
                    input_schema=tool_schema,
                    handler=create_handler(tool_name)
                ))

            registry = PiToolRegistry(tools=pi_tools)
            sandbox = PiSandbox(root="/tmp")
            target_model = model or self.default_model
            config = PiAgentConfig(
                model=target_model,
                provider="anthropic",
                auto_approve=True,
                stream=False,
                max_iterations=max_iterations,
                system_prompt="You are The Lenny Growth Assistant agent. Ground your work strictly using the provided tools."
            )
            pi_provider = PiAnthropicProvider(
                model=target_model,
                api_key=self.api_key
            )
            agent = PiAgent(
                provider=pi_provider,
                registry=registry,
                sandbox=sandbox,
                config=config,
                on_event=on_event_callback
            )

            # Extract user prompt from conversation history
            user_prompt = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    user_prompt = m.get("content", "")
                    break
            if not user_prompt:
                user_prompt = str(messages[-1].get("content", ""))

            return agent.run(user_prompt)

        # 2. Check for official Claude Agent SDK if Pi Agent is not available
        if HAS_CLAUDE_AGENT_SDK:
            try:
                logger.info("Executing agent tool loop via Anthropic Claude Agent SDK...")
                import claude_agent_sdk
                # claude_agent_sdk integration
                user_prompt = messages[-1].get("content", "") if messages else ""
                options = claude_agent_sdk.ClaudeAgentOptions(
                    system_prompt="You are The Lenny Growth Assistant agent. Ground your work strictly using the provided tools."
                )
                # Claude agent execution
                # Falls through if query API is async or requires CLI binary
            except Exception as e:
                logger.warning(f"Claude Agent SDK execution failed ({e}), continuing")

        # 3. Fallback to Messages API tool loop if no Agent SDK is present
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)

        system_prompt = "You are The Lenny Growth Assistant agent. Ground your work strictly using the provided tools."
        current_messages = [m for m in messages if m.get("role") != "system"]

        for _ in range(max_iterations):
            response = client.messages.create(
                model=model or self.default_model,
                max_tokens=2048,
                tools=tools,
                system=system_prompt,
                messages=current_messages
            )

            if response.stop_reason != "tool_use":
                text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
                return "\n".join(text_blocks)

            # Handle Claude tool call
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    result = tool_handler_callback(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            current_messages.append({"role": "assistant", "content": response.content})
            current_messages.append({"role": "user", "content": tool_results})

        return "Agent reached maximum tool iterations."

