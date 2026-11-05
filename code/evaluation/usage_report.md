# ERASIGHT Token Usage and Cost Report

This report covers the final full-dataset run that produced `output.csv` (518 requests).

## Summary
The decisions behind `output.csv` come from the deterministic engine and make **no model calls**. The optional advisory layer (`python code/advise.py --model`) asked **Groq / openai/gpt-oss-120b** for a second opinion on cases the deterministic triggers flagged. It only writes `explanations.json`; it cannot change `output.csv`. The figures below are for that single full-dataset advisory run; the mini-dataset demo is listed separately and excluded.

| Item | Value |
|---|---|
| Model providers and names used at run time | Groq: openai/gpt-oss-120b (advisory layer only) |
| Model calls | 6 |
| Input tokens | 1514 |
| Output tokens | 1757 |
| Total tokens | 3271 |
| Average tokens per request (total tokens / 518 requests) | 6.3 |
| Average tokens per model call | 545 |
| Estimated total cost | $0.0013 |
| Price assumption (USD per million tokens) | input 0.15, output 0.6 (checked against Groq's official model page on 2026-11-05: input $0.15, output $0.60 per million tokens) |
| Estimated cost per request | $0.000002 |

## Per-model breakdown
| Model | Calls | Input tokens | Output tokens | Total tokens | Estimated cost |
|---|---|---|---|---|---|
| Groq openai/gpt-oss-120b (full-dataset run) | 6 | 1514 | 1757 | 3271 | $0.0013 |
| **Overall (full-dataset run)** | 6 | 1514 | 1757 | 3271 | $0.0013 |

## Separate: mini-dataset demo (NOT part of the totals above)
A lookalike-email demo on the small mini dataset, used only to show the advisory layer working. 3 calls, 915 input and 670 output tokens (1585 total, about $0.0005).

## Run characteristics (measured)
| Item | Value |
|---|---|
| Requests | 518 |
| Dataset and evidence load | 0.1 s |
| Analysis of all requests | 1.1 s (2.2 ms per request) |
| Network access by the decision pipeline | None |

## Note on development tooling
The code was written with an AI coding assistant (Claude Code). That usage is development tooling, not part of the
submitted agent's run, and is recorded in the session transcript (`log.txt`) rather than measured here.
To refresh this file after a model run: `python code/advise.py --model` then `python code/evaluation/generate_reports.py`.

## Downloadable HTML usage report

The source report lives at `code/evaluation/usage_report.md` in this checkout; there is no root `evaluation/usage_report.md`. The existing results above are preserved.

The investigation Communication panel now provides **Model Usage Report** (HTML download) and **Send usage report to Slack**. Both use the local session; Slack sharing additionally requires the existing CSRF token, configured webhook, private-file bot permissions and channel membership. Downloading does not require Slack configuration.

The HTML reads only the fixed aggregate logs `advisor_usage.json` and `advisor_usage_demo.json`; it never invokes a model, reads prompts, or sends per-case identities. Exact arithmetic from the currently recorded counts and the historical price assumption above gives:

| Scope | Successful calls | Input tokens | Output tokens | Total tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| Deterministic 518-case decision pipeline | 0 | 0 | 0 | 0 | 0.00 |
| Full-dataset optional advisory | 6 | 1514 | 1757 | 3271 | 0.00128130 |
| Separate mini-dataset advisory | 3 | 915 | 670 | 1585 | 0.00053925 |
| All recorded advisory runs combined | 9 | 2429 | 2427 | 4856 | 0.00182055 |

Both logs record zero failed calls. The combined row describes separate advisory runs, not the decision pipeline or its per-request cost. Recorded rates apply only to Groq / openai/gpt-oss-120b: input USD 0.15 and output USD 0.60 per million tokens. They are historical assumptions, not newly verified current prices or a provider bill.

Neither aggregate log records a run timestamp, and the mini log does not record its dataset request count. These fields display **Not recorded**; file timestamps and HTML generation time are not substituted. Missing/invalid logs, missing token breakdowns and unknown model prices also display **Not recorded**; unknown values propagate to totals and prevent a complete cost estimate. The current log schema counts successful advisory calls separately from failed calls; HTTP retry attempts are not separately recorded. Legacy clients defaulted absent provider usage fields to zero, so a recorded zero alone does not prove the provider returned usage metadata. No new advisory run was performed for this feature.
