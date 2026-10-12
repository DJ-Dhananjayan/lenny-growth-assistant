import pytest
from unittest.mock import MagicMock
from app.db.models import TranscriptModel, TranscriptChunkModel
from app.services.vector_store import search_chunks
from app.agent.engine import LennyGrowthAgent, AGENT_TOOLS
from app.services.providers.anthropic_provider import AnthropicProvider, HAS_PI_AGENT_SDK
from pi_agent.agent import Agent as PiAgent
from pi_agent.tools.base import Tool as PiTool
from pi_agent.tools.registry import ToolRegistry as PiToolRegistry
from pi_agent.llm import LLMProvider, AssistantResponse, Usage, ToolCall


class MockAutonomousSDKProvider(LLMProvider):
    """
    Mock LLM conforming to Pi Coding Agent LLMProvider Protocol.
    Simulates multi-turn tool-calling loop: Turn 1 triggers tool_use; Turn 2 returns final answer.
    """
    name = "mock-pi-llm"
    model = "claude-3-5-sonnet-20241022"
    supports_streaming = False

    def __init__(self, target_tool: str = "search_transcripts", target_args: dict = None):
        self.turns = 0
        self.target_tool = target_tool
        self.target_args = target_args or {"query": "LNO framework", "top_k": 2}
        self.tools_received = []

    def complete(self, system, messages, tools):
        self.turns += 1
        self.tools_received = tools
        if self.turns == 1:
            return AssistantResponse(
                text="Investigating transcripts using search_transcripts tool...",
                tool_calls=[ToolCall(id="call_sdk_1", name=self.target_tool, args=self.target_args)],
                usage=Usage(input_tokens=20, output_tokens=15),
                stop_reason="tool_use"
            )
        return AssistantResponse(
            text="According to Shreyas Doshi on Lenny's Podcast, the LNO framework categorizes tasks into Leverage, Neutral, and Overhead.",
            tool_calls=[],
            usage=Usage(input_tokens=40, output_tokens=30),
            stop_reason="end_turn"
        )


def test_agent_sdk_tool_registration(db_session):
    """Verify that all Lenny Growth Assistant tools conform to Agent SDK schemas and can be registered in ToolRegistry."""
    tool_names = [t["name"] for t in AGENT_TOOLS]
    assert "search_transcripts" in tool_names
    assert "generate_ship30_essay" in tool_names
    assert "create_artifact" in tool_names

    # Convert to PiTool instances
    pi_tools = [
        PiTool(
            name=t["name"],
            description=t["description"],
            input_schema=t["input_schema"],
            handler=lambda args, sb: "ok"
        )
        for t in AGENT_TOOLS
    ]
    registry = PiToolRegistry(tools=pi_tools)
    assert len(registry.names()) == 3
    assert "search_transcripts" in registry.names()
    assert "generate_ship30_essay" in registry.names()
    assert "create_artifact" in registry.names()


def test_actual_agent_sdk_invocation_and_tool_execution(db_session):
    """
    Verify actual Agent SDK invocation and tool execution against database chunks.
    Ensures Pi Coding Agent autonomously invokes search_transcripts and receives real evidence.
    """
    # Seed transcript and chunk in DB
    transcript = TranscriptModel(
        episode_title="Shreyas Doshi on the LNO Framework",
        guest="Shreyas Doshi",
        episode_url="https://www.lennyweekly.com/p/shreyas-doshi",
        content="Shreyas Doshi breaks down Leverage, Neutral, Overhead."
    )
    db_session.add(transcript)
    db_session.commit()

    chunk = TranscriptChunkModel(
        transcript_id=transcript.id,
        chunk_index=0,
        content="LNO Framework: Leverage tasks yield 10x leverage. Neutral tasks yield 1x. Overhead tasks yield less than 1x.",
        embedding=[0.1] * 384
    )
    db_session.add(chunk)
    db_session.commit()

    dummy_provider = MagicMock()
    agent = LennyGrowthAgent(db=db_session, provider=dummy_provider)

    mock_llm = MockAutonomousSDKProvider(
        target_tool="search_transcripts",
        target_args={"query": "LNO framework", "top_k": 2}
    )

    response, citations, artifact, trace = agent.run_with_agent_sdk(
        prompt="Explain Shreyas Doshi's LNO framework",
        custom_provider=mock_llm
    )

    # 1. Verify agent executed multi-turn cycle
    assert mock_llm.turns == 2
    assert "LNO framework" in response

    # 2. Verify tool execution occurred and captured real database citations
    assert len(citations) >= 1
    assert citations[0]["guest"] == "Shreyas Doshi"
    assert "LNO" in citations[0]["episode_title"]

    # 3. Verify event trace contains tool_call and tool_result events
    event_names = [e["event"] for e in trace]
    assert "tool_call" in event_names
    assert "tool_result" in event_names


def test_agent_sdk_essay_tool_execution(db_session):
    """Verify Agent SDK invoking generate_ship30_essay produces a structured essay artifact."""
    transcript = TranscriptModel(
        episode_title="Elena Verna on PLG",
        guest="Elena Verna",
        episode_url="https://www.lennyweekly.com/p/elena-verna",
        content="Elena discusses acquisition loops and PLG."
    )
    db_session.add(transcript)
    db_session.commit()

    chunk = TranscriptChunkModel(
        transcript_id=transcript.id,
        chunk_index=0,
        content="Product-led growth loops turn active users into new acquired users automatically.",
        embedding=[0.2] * 384
    )
    db_session.add(chunk)
    db_session.commit()

    dummy_provider = MagicMock()
    dummy_provider.generate_completion.return_value = "### The Power of PLG Loops\n\nProduct-led growth loops scale efficiently."
    agent = LennyGrowthAgent(db=db_session, provider=dummy_provider)

    mock_llm = MockAutonomousSDKProvider(
        target_tool="generate_ship30_essay",
        target_args={"topic": "Product-Led Growth loops"}
    )

    response, citations, artifact, trace = agent.run_with_agent_sdk(
        prompt="Write a Ship 30 for 30 essay on Product-Led Growth loops",
        custom_provider=mock_llm
    )

    assert mock_llm.turns == 2
    assert artifact is not None
    assert artifact["artifact_type"] == "markdown"
    assert "Ship 30" in artifact["title"] or "Growth Strategy" in artifact["title"]


def test_anthropic_provider_has_agent_sdk_enabled(monkeypatch):
    """Verify that AnthropicProvider detects HAS_PI_AGENT_SDK = True and executes through PiAgent."""
    assert HAS_PI_AGENT_SDK is True

    provider = AnthropicProvider(api_key="sk-ant-test-key")
    assert provider.provider_id == "anthropic"

    # Test that run_agent_tool_loop executes through PiAgent without throwing unexpected errors
    executed_tools = []
    def dummy_tool_handler(name, args):
        executed_tools.append((name, args))
        return "Tool execution result."

    # Mock PiAgent.run to verify it is invoked by run_agent_tool_loop
    monkeypatch.setattr(
        PiAgent,
        "run",
        lambda self, prompt: f"SDK response for prompt: {prompt}"
    )

    messages = [{"role": "user", "content": "Explain LNO framework"}]
    res = provider.run_agent_tool_loop(
        messages=messages,
        tools=AGENT_TOOLS,
        tool_handler_callback=dummy_tool_handler,
        model="claude-3-5-sonnet-20241022"
    )
    assert res == "SDK response for prompt: Explain LNO framework"

