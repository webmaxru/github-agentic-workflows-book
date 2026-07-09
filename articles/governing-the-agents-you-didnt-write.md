<!--
Newsletter article — 2 of 2 (companion: the-prompt-that-compiles.md)
Angle: Enterprise governance
Audience: agentengineering.co — builders and practitioners of agentic systems, past the hype
Source: "GitHub Agentic Workflows" interactive book (this repo), targeting gh aw v0.81.6 (Public Preview)
Shape: Problem -> Solution, getting-started level
Length: ~750 words (body)
-->

# Governing the Agents You Didn't Write

*Agent fleets don't stall on capability. They stall on the two questions every leader eventually asks: what will this cost, and what is it allowed to do?*

The pilot always goes well. One team wires up an agent that reviews pull requests, or triages issues, or keeps a changelog honest, and it works well enough that people want it everywhere. So it spreads — a copy here, a fork there — until one morning it is running in forty repositories and two questions land on your desk at once. Finance wants to know what the model bill is going to be. Security wants to know what, exactly, these things are allowed to touch.

Neither question has a good answer, because the thing that spread was a prompt in a box. And you cannot govern English. A prompt has no version you can pin, no permission surface to set policy against, no audit trail when it does something you didn't expect. This — not model quality — is why agentic automation stalls the moment it leaves one enthusiast's repository. The capability was never the risk. The absence of a control plane was.

**GitHub Agentic Workflows answers by making intent compile into something you can govern.** You author a workflow as Markdown, and `gh aw compile` turns it into a `.lock.yml` — a pinned, reviewable GitHub Actions workflow. That compiled artifact *is* the control plane. It is diffable, it lives in version control, and it pins its dependencies to exact commit SHAs, so what runs in production is precisely what someone reviewed. The agent inside runs read-only; every write is proposed as structured output and applied by a separate, permission-scoped job. A tricked model can still misbehave, but its blast radius is whatever that second job is narrowly allowed to do — not the credentials of the whole workflow.

That reframes both questions from hope into settings.

*What will it cost?* Agentic work has a budget in a way CI never did — each run spends a variable amount of inference depending on how much the agent reads, reasons, and retries. gh-aw denominates that in AI Credits and hands you a dial. `max-ai-credits` sets a per-run budget (1000 by default), with steering messages as a run crosses 80, 90, 95 and 99 percent. Its sibling `max-daily-ai-credits` caps a rolling 24-hour total and, when a workflow runs hot, "warns, creates an issue, skips the agent job." A looping agent stops itself. Spend becomes a number you set, not a surprise you find on an invoice — and org-wide defaults apply the same ceilings to every repo without anyone editing a workflow.

*What is it allowed to do?* Here the harder surface is not the model but its **supply chain**. The skills, prompts and plugins an agent consumes are executable context — an unreviewed one is an injection vector wearing a dependency's clothes. The Agent Package Manager (APM) treats those skills as packages "with the same governance primitives that enterprises require for code dependencies." Three controls do the work. Every package is pinned to an exact SHA in an `apm.lock.yaml`, so "there is no drift between what was reviewed and what actually runs," and install-time scanning flags hidden-Unicode tricks — homoglyphs, bidirectional overrides, zero-width joiners — that smuggle invisible instructions into a prompt. An `apm-policy.yml` in the org's `.github` repository sets an allowlist of what any repo may consume. And that policy inherits *tighten-only* down the enterprise → org → repo chain: a child can narrow the list or escalate enforcement, never relax what a parent locked. Governance travels with the fleet instead of depending on forty teams remembering to be careful.

The payoff shows up at exactly the scale that used to be terrifying. Among the public-preview adopters, a single gh-aw review agent has been cloned into more than 215 repositories — the kind of sprawl that is a nightmare when the unit is an ungoverned prompt and a non-event when it is a pinned, budgeted, policy-bound workflow. Change the source, recompile, and the fleet moves together.

There is a quiet proof of the model in how this argument reached you: the book these pieces draw from was itself produced by a governed fleet of agents, pinned and policy-bound through the same package manager it describes. The lesson underneath is the one enterprises have been waiting for. You don't make agents safe to scale by trusting them more. You make them safe by compiling their intent into infrastructure you can already review, price, and pin — and by treating everything they consume like the dependency it is.
