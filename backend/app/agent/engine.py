import logging
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from app.services.vector_store import search_chunks
from app.services.providers.base import BaseLLMProvider
from app.agent.tools import is_essay_request, is_html_artifact_request, format_citations
from app.agent.ship30_skill import generate_ship30_essay

logger = logging.getLogger(__name__)

# Official Anthropic Claude Agent SDK Tool Definitions
AGENT_TOOLS = [
    {
        "name": "search_transcripts",
        "description": "Searches Lenny's Podcast transcript chunks using vector similarity for product strategy evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query or concept"},
                "top_k": {"type": "integer", "default": 4}
            },
            "required": ["query"]
        }
    },
    {
        "name": "generate_ship30_essay",
        "description": "Generates a structured ~1,250 word Ship 30 for 30 style growth essay based on transcript evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The strategic essay topic"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "create_artifact",
        "description": "Generates a Markdown or HTML artifact snippet for rendering in the workspace side panel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "artifact_type": {"type": "string", "enum": ["markdown", "html"]},
                "content": {"type": "string"}
            },
            "required": ["title", "artifact_type", "content"]
        }
    }
]


class LennyGrowthAgent:
    """
    Autonomous RAG Agent orchestrator for product/growth intelligence.
    Executes tool-calling loops over transcript vector store and skill modules.
    Compatible with Anthropic Claude Agent SDK and local LLM execution.
    """

    def __init__(self, db: Session, provider: BaseLLMProvider, model: Optional[str] = None):
        self.db = db
        self.provider = provider
        self.model = model

    def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Dispatches tool execution for agentic loops."""
        if tool_name == "search_transcripts":
            chunks = search_chunks(self.db, query=tool_input.get("query", ""), top_k=tool_input.get("top_k", 4))
            if hasattr(self, "_active_citations") and isinstance(self._active_citations, list):
                self._active_citations.extend(chunks)
            return chunks
        elif tool_name == "generate_ship30_essay":
            chunks = search_chunks(self.db, query=tool_input.get("topic", ""), top_k=4)
            if hasattr(self, "_active_citations") and isinstance(self._active_citations, list):
                self._active_citations.extend(chunks)
            essay, artifact = generate_ship30_essay(self.provider, tool_input.get("topic", ""), chunks, model=self.model)
            if artifact and hasattr(self, "_active_artifact"):
                self._active_artifact = artifact
            return essay
        elif tool_name == "create_artifact":
            if hasattr(self, "_active_artifact"):
                self._active_artifact = tool_input
            return f"Artifact '{tool_input.get('title')}' created successfully."
        return f"Unknown tool: {tool_name}"

    def run(
        self,
        prompt: str,
        history_messages: List[Dict[str, str]] = None
    ) -> Tuple[str, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Executes the main agent cycle.
        Returns (response_text, citations_list, artifact_dict).
        """
        history_messages = history_messages or []
        clean_prompt = prompt.strip()
        lowered = clean_prompt.lower()
        self._active_citations = []
        self._active_artifact = None

        # 1. Handle common greetings & introductory questions
        greeting_words = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "yo"}
        clean_word = lowered.strip(".!?")
        if clean_word in greeting_words or clean_word.startswith("hi ") or clean_word.startswith("hello ") or clean_word in {"who are you", "what can you do", "help", "about"}:
            welcome_msg = (
                "👋 **Hello! Welcome to The Lenny Growth Assistant.**\n\n"
                "I am an evidence-grounded AI assistant for Product Managers, Growth Leads, and Founders, powered by transcripts from **Lenny's Podcast**.\n\n"
                "Here are a few things you can ask me:\n"
                "• **Product Strategy**: *'What is the LNO framework by Shreyas Doshi?'*\n"
                "• **Founder-Led Mode**: *'How does Brian Chesky explain Founder-Led Mode at Airbnb?'*\n"
                "• **PLG & Growth Loops**: *'What are the core metrics for Product-Led Growth according to Elena Verna?'*\n"
                "• **Distribution Strategy**: *'What does Elad Gil say about distribution vs. product quality?'*\n"
                "• **Ship 30 for 30 Essay**: *'Write a Ship 30 for 30 essay on Product-Led Growth loops'*\n"
                "• **Interactive Artifacts**: *'Generate an HTML dashboard card widget for PLG metrics'*\n\n"
                "What product or growth challenge would you like to explore?"
            )
            return welcome_msg, [], None

        # 2. Out-of-scope / Unrelated query handling
        cookie_keywords = ["cookie", "cookies", "chocolate chip"]
        recipe_keywords = ["recipe", "recipes", "bake", "baking", "cook", "cooking", "ingredient", "ingredients", "cake", "pasta", "pizza", "lasagna", "pie", "bread"]
        
        is_cookie_or_recipe = any(k in lowered for k in cookie_keywords) or (
            any(k in lowered for k in recipe_keywords) and not any(term in lowered for term in ["growth", "product", "metric", "framework", "funnel", "loop", "strategy", "retention", "startup"])
        )
        if is_cookie_or_recipe:
            out_of_scope_msg = (
                "I'm designed to answer product, growth, and startup questions grounded in Lenny's Podcast. "
                "I can't provide a cookie recipe, but I can help with a product or growth question."
            )
            return out_of_scope_msg, [], None

        out_of_domain_topics = {
            "quantum physics": "quantum physics",
            "black hole": "black hole thermodynamics",
            "thermodynamics": "thermodynamics",
            "weather": "weather forecasts",
            "football": "sports scores",
            "nba": "sports",
            "nfl": "sports",
            "world cup": "sports",
            "capital of": "geography trivia",
            "astronomy": "astronomy",
            "faucet": "home repair",
            "medical": "medical advice"
        }
        for kw, topic in out_of_domain_topics.items():
            if kw in lowered:
                out_of_domain_msg = (
                    f"I'm designed to answer product, growth, and startup questions grounded in Lenny's Podcast. "
                    f"I can't assist with {topic}, but I can help with a product or growth question."
                )
                return out_of_domain_msg, [], None

        # 3. Contextual query formulation for follow-up turns
        search_query = clean_prompt
        if history_messages:
            last_user_msgs = [m["content"] for m in history_messages if m.get("role") == "user"]
            if last_user_msgs:
                search_query = f"{last_user_msgs[-1]} {clean_prompt}"

        # 4. Execute transcript vector search tool
        all_chunks = search_chunks(self.db, query=search_query, top_k=4)

        # 5. Strict relevance & grounding check
        grounding_stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "about", "into", "through", "after", "before", "under", "above",
            "and", "or", "but", "so", "if", "then", "else", "when", "where", "why", "how", "what",
            "which", "who", "whom", "whose", "this", "that", "these", "those", "it", "its", "you",
            "your", "we", "our", "he", "she", "they", "them", "their", "can", "could", "will",
            "would", "should", "have", "has", "had", "do", "does", "did", "tell", "give", "explain",
            "describe", "write", "make", "podcast", "episode", "lenny", "lennys", "say", "says"
        }
        content_words = [
            w.strip("?,.!;:\"'()")
            for w in search_query.lower().split()
            if len(w.strip("?,.!;:\"'()")) > 2 and w.strip("?,.!;:\"'()") not in grounding_stopwords
        ]

        relevant_chunks = []
        for c in all_chunks:
            chunk_score = c.get("score", 0.0)
            text_corpus = (c.get("snippet", "") + " " + c.get("guest", "") + " " + c.get("episode_title", "")).lower()
            matching_terms = [w for w in content_words if w in text_corpus]
            # Grounded if strong vector score (>= 0.45) or content words match with decent score (>= 0.25)
            if (chunk_score >= 0.45) or (len(matching_terms) >= 1 and chunk_score >= 0.25):
                relevant_chunks.append(c)

        # If there are grounded matches, only keep top matches close to top score to avoid irrelevant sources
        if relevant_chunks:
            top_score = relevant_chunks[0]["score"]
            cutoff = max(0.25, top_score * 0.70)
            relevant_chunks = [c for c in relevant_chunks if c["score"] >= cutoff]

        # 6. Abstention if insufficient evidence
        if not relevant_chunks and not is_essay_request(clean_prompt) and not is_html_artifact_request(clean_prompt):
            abstention_msg = (
                "The available Lenny's Podcast transcripts do not contain sufficient evidence to answer this question reliably.\n\n"
                "Currently ingested episodes include insights from:\n"
                "• **Brian Chesky** (Airbnb) on Founder-Led Mode & Product Design\n"
                "• **Shreyas Doshi** on the LNO Framework & Product Prioritization\n"
                "• **Elad Gil** on High Growth & Distribution vs Product\n"
                "• **Elena Verna** on Product-Led Growth (PLG) & Growth Loops\n\n"
                "Try asking about one of these topics, such as *'What is the LNO framework by Shreyas Doshi?'* or *'How does Brian Chesky explain Founder-Led Mode?'*"
            )
            return abstention_msg, [], None

        citations = format_citations(relevant_chunks)

        # 5. Route to Ship 30 Essay Skill tool
        if is_essay_request(clean_prompt):
            essay_text, artifact = generate_ship30_essay(self.provider, clean_prompt, relevant_chunks, model=self.model)
            return essay_text, citations, artifact

        # 6. Route to HTML Artifact tool
        if is_html_artifact_request(clean_prompt):
            html_prompt = f"Create a self-contained, beautifully styled modern HTML snippet (no external JS scripts) for: {clean_prompt}."
            messages = [
                {"role": "system", "content": "Return raw HTML inside <style> and <div> tags. Do NOT use markdown code fences."},
                {"role": "user", "content": html_prompt}
            ]
            html_content = self.provider.generate_completion(messages=messages, model=self.model, temperature=0.3)
            html_content = html_content.replace("```html", "").replace("```", "").strip()

            artifact = {
                "title": f"HTML Component: {clean_prompt[:40]}",
                "artifact_type": "html",
                "content": html_content
            }
            answer_text = f"I have generated the HTML artifact for **'{clean_prompt}'**. You can inspect the preview, view source code, copy, or download it in the side panel."
            return answer_text, citations, artifact

        # 7. Synthesize grounded answer
        # If Anthropic provider is active and credentials available, invoke agent tool loop
        if getattr(self.provider, "provider_id", "") == "anthropic" and hasattr(self.provider, "run_agent_tool_loop"):
            try:
                agent_messages = [{"role": "user", "content": clean_prompt}]
                response_text = self.provider.run_agent_tool_loop(
                    messages=agent_messages,
                    tools=AGENT_TOOLS,
                    tool_handler_callback=self.handle_tool_call,
                    model=self.model
                )
                final_citations = format_citations(self._active_citations) if self._active_citations else citations
                return response_text, final_citations, self._active_artifact
            except Exception as e:
                logger.warning(f"Anthropic agent tool loop fallback to direct completion: {e}")

        # Standard RAG synthesis
        evidence_block = ""
        for idx, c in enumerate(relevant_chunks, 1):
            evidence_block += f"\n[Evidence {idx} - Guest: {c['guest']} | Episode: {c['episode_title']}]\n{c['snippet']}\n"

        system_prompt = (
            "You are The Lenny Growth Assistant. Ground your answer strictly in the provided transcript evidence.\n"
            "Answer the user's question directly, clearly, and concisely.\n"
            "DO NOT dump raw transcript excerpts or repeat the evidence word-for-word. Synthesize an articulate response citing the guest and episode.\n\n"
            f"AVAILABLE TRANSCRIPT EVIDENCE:\n{evidence_block}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history_messages[-4:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": clean_prompt})

        response_text = self.provider.generate_completion(messages=messages, model=self.model, temperature=0.5)

        # Auto-create Markdown artifact for structured long responses
        artifact = None
        if len(response_text) > 800 or "###" in response_text:
            artifact = {
                "title": f"Growth Strategy: {clean_prompt[:40]}",
                "artifact_type": "markdown",
                "content": response_text
            }

        return response_text, citations, artifact

    def run_with_agent_sdk(
        self,
        prompt: str,
        custom_provider: Any = None,
        max_iterations: int = 5
    ) -> Tuple[str, List[Dict[str, Any]], Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Directly executes the autonomous agent cycle using the Pi Coding Agent SDK / Anthropic Claude Agent SDK harness.
        Dispatches all tool calls through real ToolRegistry schemas and handlers, returning (response_text, citations, artifact, event_trace).
        """
        from pi_agent.agent import Agent as PiAgent, AgentConfig as PiAgentConfig, Sandbox as PiSandbox
        from pi_agent.tools.base import Tool as PiTool
        from pi_agent.tools.registry import ToolRegistry as PiToolRegistry

        collected_chunks = []
        collected_artifacts = []
        events_trace = []

        def on_event(ev_type: str, payload: Any):
            events_trace.append({"event": ev_type, "payload": payload})

        def search_handler(args: Dict[str, Any], sandbox: Any) -> str:
            q = args.get("query", "")
            k = args.get("top_k", 4)
            chunks = search_chunks(self.db, query=q, top_k=k)
            collected_chunks.extend(chunks)
            if not chunks:
                return "No transcript matches found."
            lines = [f"Guest: {c['guest']} | Episode: {c['episode_title']}\nSnippet: {c['snippet']}" for c in chunks]
            return "\n\n".join(lines)

        def essay_handler(args: Dict[str, Any], sandbox: Any) -> str:
            topic = args.get("topic", "")
            chunks = search_chunks(self.db, query=topic, top_k=4)
            collected_chunks.extend(chunks)
            essay, artifact = generate_ship30_essay(self.provider, topic, chunks, model=self.model)
            if artifact:
                collected_artifacts.append(artifact)
            return essay

        def artifact_handler(args: Dict[str, Any], sandbox: Any) -> str:
            artifact = {
                "title": args.get("title", "Artifact"),
                "artifact_type": args.get("artifact_type", "markdown"),
                "content": args.get("content", "")
            }
            collected_artifacts.append(artifact)
            return f"Artifact '{artifact['title']}' recorded successfully."

        tools = [
            PiTool(
                name="search_transcripts",
                description="Searches Lenny's Podcast transcript chunks using vector similarity.",
                input_schema=AGENT_TOOLS[0]["input_schema"],
                handler=search_handler
            ),
            PiTool(
                name="generate_ship30_essay",
                description="Generates a structured ~1,250 word Ship 30 for 30 style growth essay based on transcript evidence.",
                input_schema=AGENT_TOOLS[1]["input_schema"],
                handler=essay_handler
            ),
            PiTool(
                name="create_artifact",
                description="Generates a Markdown or HTML artifact snippet for rendering in the workspace side panel.",
                input_schema=AGENT_TOOLS[2]["input_schema"],
                handler=artifact_handler
            )
        ]

        registry = PiToolRegistry(tools=tools)
        sandbox = PiSandbox(root="/tmp")
        config = PiAgentConfig(
            model=self.model or "default-model",
            provider="custom" if custom_provider else "anthropic",
            auto_approve=True,
            stream=False,
            max_iterations=max_iterations,
            system_prompt="You are The Lenny Growth Assistant. Ground your work strictly using the provided tools."
        )

        agent = PiAgent(
            provider=custom_provider or self.provider,
            registry=registry,
            sandbox=sandbox,
            config=config,
            on_event=on_event
        )

        final_response = agent.run(prompt)
        citations = format_citations(collected_chunks)
        artifact = collected_artifacts[0] if collected_artifacts else None
        return final_response, citations, artifact, events_trace


def execute_agent_rag(
    db: Session,
    provider: BaseLLMProvider,
    prompt: str,
    history_messages: List[Dict[str, str]] = None,
    model: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Helper entry point delegating to LennyGrowthAgent class."""
    agent = LennyGrowthAgent(db=db, provider=provider, model=model)
    return agent.run(prompt=prompt, history_messages=history_messages)

