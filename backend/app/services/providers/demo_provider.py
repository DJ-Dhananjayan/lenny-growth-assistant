import logging
from typing import List, Dict, Optional
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

# Complete ~1,250-word Ship 30 for 30 Growth Essay
SHIP30_FULL_ESSAY = """# The Founder-Led Growth Playbook: Why Conventional Product Management Is Dead

Most venture-backed technology companies fail for a simple, uncomfortable reason: they ship their internal org charts rather than cohesive user experiences.

For the past fifteen years, Silicon Valley dogma taught founders to delegate product vision as early as possible. The conventional playbook was simple: hire seasoned executives, step back, write exhaustive product requirements documents (PRDs), run two-week sprint ceremonies, and let middle managers orchestrate the roadmap.

The result? Bloated software, decelerating growth, alienated users, and billions of dollars in wasted capital.

Across hundreds of in-depth conversations on *Lenny's Podcast*, the world's most effective operators—including **Brian Chesky**, **Shreyas Doshi**, **Elad Gil**, and **Elena Verna**—have revealed an entirely different truth. Sustainable high-growth companies are not built by bureaucratic delegation. They are engineered through relentless attention to detail, ruthless leverage prioritization, disciplined distribution engines, and autonomous product-led growth loops.

This essay breaks down the four foundational pillars of modern product growth and outlines an immediate execution framework for product managers and founders.

---

## The Core Problem: The Failure of Conventional Management

The traditional product management paradigm was inherited from 20th-century consumer packaged goods companies. In software, however, customer expectations evolve in real-time, competitive moats erode overnight, and distribution advantages compound exponentially.

When product managers spend 70% of their working hours synchronizing roadmaps, managing Jira tickets, and facilitating cross-functional consensus, they lose touch with the customer's actual pain. Product teams end up optimizing for output—number of tickets closed, features shipped, and slides presented—rather than actual business leverage.

As companies scale past 50 employees, organizational silos form. Marketing blames Product for poor feature adoption; Product blames Engineering for missed deadlines; Sales demands custom enterprise features that derail the core platform. Without a singular, cohesive vision guiding every touchpoint, the user experience becomes fragmented and confusing.

To break out of this stagnation trap, high-growth leaders must adopt a modern operator mindset anchored in four proven pillars.

---

## Pillar 1: Founder-Led Mode and Design-Led Culture

The first breakthrough came from Airbnb's radical operational transformation. As **Brian Chesky** (co-founder and CEO of Airbnb) explained on *Lenny's Podcast*, conventional management advice nearly broke the company:

> *"When Airbnb scaled to thousands of employees, conventional advice told us to hire experienced executives, delegate everything, and get out of the way. But by 2019, our product momentum slowed down, costs ballooned, and we were shipping org charts instead of cohesive products. I realized that a founder cannot simply delegate product vision."*

To restore velocity, Airbnb pioneered what the tech industry now calls **Founder-Led Mode**:

1. **Staying in the Details**: Leaders must refuse to accept high-level dashboard summaries. They must inspect the actual pixels, walk through user onboarding flows directly, and treat product design as a core strategic discipline rather than aesthetic polish.
2. **Merging PM with Product Marketing**: Airbnb abolished standalone, specification-only product management roles. Product managers were merged with product marketers and held strictly accountable for end-to-end positioning, market education, and user adoption.
3. **Synchronized Biannual Releases**: Instead of dozens of uncoordinated micro-launches, Airbnb shifted to two major launch moments per year. This forced marketing, engineering, design, and executive leadership to align on shared strategic milestones.

**The Rule**: You cannot delegate what you do not deeply understand. If leadership is detached from the craft, the product will inevitably lose its soul.

---

## Pillar 2: The LNO Prioritization Architecture

Even with executive alignment, product managers frequently experience severe burnout because they attempt to execute every task at 100% perfection. Former Stripe and Twitter product leader **Shreyas Doshi** transformed modern product execution by introducing the **LNO Framework**:

Most operators drown in work because they treat all tasks as equally important. In reality, product tasks fall into three asymmetrical leverage categories:

- **Leverage Tasks (L)**: Initiatives where extraordinary execution yields a 10x disproportionate return. This includes defining product positioning, choosing core platform architectures, structuring pricing models, and identifying growth loops. Operators should invest **80% of their creative energy** here and demand uncompromising 10/10 excellence.
- **Neutral Tasks (N)**: Standard operational responsibilities where solid execution is expected and sufficient (e.g., routine spec writing, standard stakeholder updates, sprint reviews). Aim for **7/10 quality**. Attempting 10/10 perfection on Neutral tasks is wasted leverage.
- **Overhead Tasks (O)**: Administrative compliance, routine status reports, and clerical requirements. Operators should complete these as quickly as possible at a passable **5/10 quality**.

As Shreyas Doshi noted on *Lenny's Podcast*, spending equal effort on Overhead tasks as Leverage tasks actively destroys your high-leverage impact. High-performance operators ruthlessly protect their calendar for L tasks and aggressively compress O tasks.

---

## Pillar 3: Distribution Engines Beat Product Quality

A dangerous myth persists among engineering-heavy startups: *"If we build a superior product, customers will naturally discover it."*

Investor and author **Elad Gil** (*High Growth Handbook*) dismantled this misconception on *Lenny's Podcast*:

> *"Early on, product quality matters most. But as a market matures, distribution beats product quality 9 times out of 10. A good product with great distribution will defeat a great product with weak distribution every single time."*

Founders must establish their primary distribution engine before aggressively hiring headcount:

- **Identify the Single Dominant Loop**: Is your company powered by self-serve Product-Led Growth (PLG), enterprise account-based sales, or programmatic content SEO loops? Attempting to execute all three distribution channels simultaneously at Series A dilutes focus and burns runway.
- **Optimize Unit Economics Early**: A distribution loop is only scalable if Customer Acquisition Cost (CAC) and Payback Period allow for continuous reinvestment.
- **Layer Secondary Channels Sequentially**: Only once the primary acquisition loop achieves predictable repeatability should teams layer on supplementary channels.

---

## Pillar 4: Product-Led Growth Velocity and Time to Value

In modern software, modern buyers refuse to sit through 60-minute sales presentations before experiencing product utility. As growth executive and advisor **Elena Verna** (Miro, Amplitude, SurveyMonkey) shared on *Lenny's Podcast*:

> *"True Product-Led Growth means the product itself is the primary driver of acquisition, retention, and expansion. If users cannot derive value independently without talking to a salesperson, you do not have PLG; you have sales-assisted self-serve."*

Elena outlines three essential metrics for monitoring PLG health:

1. **Time to Value (TTV)**: Must be measured in **minutes, not days**. If a new registrant does not reach the core 'aha-moment' during their initial session, approximately 80% will churn permanently.
2. **Natural Rate of Growth (NRG)**: The percentage of revenue expansion generated exclusively through self-serve organic product adoption, independent of paid marketing spend.
3. **Expansion Loops**: Product architecture where individual end-user utility naturally invites colleagues, generates public artifacts, or triggers multi-player team workflows.

---

## Actionable Execution Checklist: Ship This Tomorrow

To apply these frameworks immediately within your organization:

1. **Backlog Audit**: Tag every item on your current quarterly roadmap as Leverage (L), Neutral (N), or Overhead (O). Cut or delegate half of the O tasks.
2. **Onboarding Funnel Compression**: Audit your sign-up flow. Remove every optional form field, friction point, or forced verification until Time to Value drops below three minutes.
3. **Direct Product Reviews**: Schedule weekly craft walkthroughs where founders and leads inspect user touchpoints directly, embodying Founder-Led Mode.
4. **Primary Channel Commitment**: Pick your single dominant distribution engine (PLG self-serve, outbound sales, or programmatic SEO) and pause secondary distractions.
5. **Measure Natural Rate of Growth (NRG)**: Calculate your baseline self-serve organic growth rate and establish it as a primary executive KPI.
"""


class DemoProvider(BaseLLMProvider):
    """
    Built-in Demo Provider (Local Synthesis).
    Provides structured, grounded answers across topics without requiring external API keys.
    """

    @property
    def provider_id(self) -> str:
        return "demo"

    @property
    def display_name(self) -> str:
        return "Demo (Local Synthesis)"

    @property
    def provider_type(self) -> str:
        return "local"

    def is_available(self) -> tuple[bool, Optional[str]]:
        return True, None

    def list_models(self) -> List[str]:
        return ["demo-synthesis-v1"]

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        user_msg = ""
        system_msg = ""
        for m in messages:
            if m["role"] == "user":
                user_msg = m["content"]
            elif m["role"] == "system":
                system_msg += m["content"] + "\n"

        lowered = user_msg.lower()

        # HTML Artifact generation request
        if "html" in lowered or "dashboard" in lowered or "card" in lowered or "widget" in lowered:
            return """<style>
.metric-card {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border: 1px solid #334155;
  color: #ffffff;
  padding: 24px;
  border-radius: 12px;
  font-family: system-ui, -apple-system, sans-serif;
  max-width: 440px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}
.metric-header { font-size: 13px; text-transform: uppercase; color: #818cf8; letter-spacing: 1px; font-weight: 600; }
.metric-value { font-size: 38px; font-weight: 800; margin: 10px 0 6px; color: #6366f1; }
.metric-badge { display: inline-block; background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 12px; padding: 3px 8px; border-radius: 4px; font-weight: 600; margin-bottom: 12px; }
.metric-sub { font-size: 13px; color: #94a3b8; line-height: 1.5; }
.kpi-row { display: flex; justify-content: space-between; margin-top: 16px; padding-top: 14px; border-top: 1px solid #334155; font-size: 12px; color: #cbd5e1; }
</style>
<div class="metric-card">
  <div class="metric-header">Product-Led Growth (PLG) Engine</div>
  <div class="metric-value">84.2%</div>
  <div class="metric-badge">↑ +18.4% YoY</div>
  <div class="metric-sub">Natural Rate of Growth (NRG) — Derived from self-serve product loops without sales intervention.</div>
  <div class="kpi-row">
    <div><strong>Time to Value:</strong> 2.4 mins</div>
    <div><strong>Expansion:</strong> 132% NRR</div>
  </div>
</div>"""

        # Ship 30 for 30 Essay generation request (~1,250 words)
        if "ship 30" in lowered or "essay" in lowered or "article" in lowered:
            return SHIP30_FULL_ESSAY

        # Shreyas Doshi / LNO Framework questions
        if "lno" in lowered or "shreyas" in lowered or "leverage" in lowered or "priorit" in lowered:
            return """According to **Shreyas Doshi** (former Product Leader at Stripe and Twitter) on *Lenny's Podcast*, the **LNO Framework** helps product managers escape the trap of trying to achieve 10/10 perfection on every task.

The framework categorizes all work into three distinct tiers:

1. **Leverage Tasks (L)**:
   - High-impact initiatives where extraordinary execution produces 10x outcomes (e.g., core product strategy, positioning, architectural choices).
   - **Guideline**: Dedicate ~80% of your creative energy here and aim for 10/10 excellence.

2. **Neutral Tasks (N)**:
   - Standard operational tasks where solid execution is expected and sufficient (e.g., routine feature specs, status updates).
   - **Guideline**: Aim for 7/10 quality. Striving for 10/10 here is wasted leverage.

3. **Overhead Tasks (O)**:
   - Administrative and low-impact requirements (e.g., expense reports, routine check-ins).
   - **Guideline**: Complete these as quickly as possible at a passable 5/10 quality. Equal effort on Overhead tasks directly degrades your high-leverage impact."""

        # Brian Chesky / Airbnb / Founder-Led Mode questions
        if "chesky" in lowered or "airbnb" in lowered or "founder" in lowered or "design" in lowered:
            return """As **Brian Chesky** (co-founder & CEO of Airbnb) explained on *Lenny's Podcast*, Airbnb transitioned to **Founder-Led Mode** after discovering that conventional executive delegation diluted product quality:

Key principles of Airbnb's Founder-Led Mode:
• **Staying in the Details**: Rather than delegating product decisions, leadership reviews products directly and treats design as a core strategic discipline.
• **Merging PM and Product Marketing**: Traditional PM roles were abolished in favor of product marketing managers who own both feature specs and market adoption.
• **Synchronized Release Cycles**: Airbnb shifted from fragmented weekly releases to two major, coordinated annual launch moments, aligning the entire company around focused themes."""

        # Elena Verna / PLG questions
        if "elena" in lowered or "verna" in lowered or "plg" in lowered or "growth loop" in lowered:
            return """According to growth advisor **Elena Verna** on *Lenny's Podcast*, true **Product-Led Growth (PLG)** occurs when the product itself—not human sales teams—drives acquisition, retention, and monetization.

Elena emphasizes three critical metrics:
• **Time to Value (TTV)**: Must be measured in minutes, not days. If users do not experience the core aha-moment in their first session, 80% never return.
• **Natural Rate of Growth (NRG)**: Measures how fast revenue expands purely from self-serve product usage without paid marketing.
• **Expansion Efficiency**: How effectively product usage leads to team invites, collaboration loops, and natural tier upgrades."""

        # Elad Gil / Scaling questions
        if "elad" in lowered or "gil" in lowered or "distribution" in lowered or "scale" in lowered:
            return """As **Elad Gil** (author of *High Growth Handbook*) emphasized on *Lenny's Podcast*, early-stage founders often over-index on product features while ignoring distribution:

• **Distribution Beats Product**: A good product with outstanding distribution defeats a great product with weak distribution 9 out of 10 times.
• **Channel Focus**: Founders should identify and optimize one primary distribution engine (PLG self-serve, enterprise sales, or programmatic content loops) before diluting focus across multiple channels."""

        # General product synthesis
        return """Based on strategic insights from **Lenny's Podcast**, world-class product teams succeed by focusing on:
1. **High-Leverage Execution**: Applying Shreyas Doshi's LNO framework to prioritize 10x strategic bets.
2. **Founder & Design Rigor**: Following Brian Chesky's model of staying in product details rather than delegating vision.
3. **Product-Led Velocity**: Elena Verna's emphasis on compressing Time to Value (TTV) into minutes and cultivating self-serve growth loops."""
