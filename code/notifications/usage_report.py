"""Read recorded advisory accounting only; never run a model or inspect credentials."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from html import escape
from pathlib import Path

EVALUATION = Path(__file__).resolve().parents[1] / 'evaluation'
# Historical assumption already recorded in evaluation/usage_report.md, not a live quote.
PRICES = {('Groq', 'openai/gpt-oss-120b'): (Decimal('0.15'), Decimal('0.60'))}


def count(value):
    return value if type(value) is int and value >= 0 else None


def recorded_run(path: Path, scope: str) -> dict:
    try:
        if path.stat().st_size > 1024 * 1024:
            raise ValueError()
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError()
    except (OSError, ValueError, UnicodeError):
        data = {}
    provider, model = data.get('provider'), data.get('model')
    provider = provider[:160] if isinstance(provider, str) else None
    model = model[:160] if isinstance(model, str) else None
    inp, out = count(data.get('input_tokens')), count(data.get('output_tokens'))
    total = inp + out if inp is not None and out is not None else count(data.get('total_tokens'))
    prices = PRICES.get((provider, model))
    cost = ((Decimal(inp) * prices[0] + Decimal(out) * prices[1]) / 1_000_000
            if prices and inp is not None and out is not None else None)
    # Neither file modification times nor the report-generation time prove when a run happened.
    timestamp = data.get('run_timestamp')
    try:
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).isoformat()
    except (ValueError, TypeError, AttributeError):
        timestamp = None
    return dict(scope=scope, source=path.name, provider=provider, model=model,
                calls=count(data.get('calls')), failed_calls=count(data.get('failed_calls')),
                input_tokens=inp, output_tokens=out, total_tokens=total,
                prices=prices, cost=cost, timestamp=timestamp)


def totals(rows: list[dict]) -> dict:
    # Unknown data must propagate; a partial sum must never masquerade as a grand total.
    result = {}
    for key in ('calls', 'failed_calls', 'input_tokens', 'output_tokens', 'total_tokens', 'cost'):
        values = [row[key] for row in rows]
        result[key] = sum(values) if all(v is not None for v in values) else None
    return result


def html_usage_report(dataset_count: int, directory: Path = EVALUATION) -> bytes:
    main = recorded_run(directory / 'advisor_usage.json', 'Recorded full-dataset advisory; 518 requests (usage_report.md)')
    demo = recorded_run(directory / 'advisor_usage_demo.json', 'Separate mini-dataset advisory; request count not recorded')
    rows = [main, demo]

    def show(value):
        return escape(str(value)) if value is not None else 'Not recorded'

    def money(value):
        return f'${value:.8f}' if value is not None else 'Not recorded'

    def summary(label, value):
        return ('<tr><th>' + escape(label) + '</th>' + ''.join('<td>' + show(value[k]) + '</td>'
                for k in ('calls', 'failed_calls', 'input_tokens', 'output_tokens', 'total_tokens'))
                + '<td>' + money(value['cost']) + '</td></tr>')

    sections = ''
    for row in rows:
        prices = row['prices'] or (None, None)
        sections += (f'<section><h2>{show(row["scope"])}</h2><p>Source: {show(row["source"])}<br>'
                     f'Run timestamp: {show(row["timestamp"])}</p><table><thead><tr><th>Provider</th><th>Model</th>'
                     '<th>API calls (recorded successful)</th><th>Failed calls</th><th>Input tokens</th><th>Output tokens</th>'
                     '<th>Total tokens</th><th>Input USD / million</th><th>Output USD / million</th><th>Estimated USD</th>'
                     '</tr></thead><tbody><tr>'
                     + ''.join(f'<td>{show(row[k])}</td>' for k in
                               ('provider', 'model', 'calls', 'failed_calls', 'input_tokens', 'output_tokens', 'total_tokens'))
                     + f'<td>{show(prices[0])}</td><td>{show(prices[1])}</td><td>{money(row["cost"])}</td>'
                     '</tr></tbody></table></section>')
    headings = ('<tr><th>Scope</th><th>Successful calls</th><th>Failed calls</th><th>Input tokens</th>'
                '<th>Output tokens</th><th>Total tokens</th><th>Estimated USD</th></tr>')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; '
            'base-uri \'none\'; form-action \'none\'">'
            '<title>EraSight Model Usage &amp; Cost Report</title><style>'
            'body{font:15px/1.6 system-ui,sans-serif;color:#182534;background:#f4f6f8;margin:0;padding:32px}'
            'main{max-width:1200px;margin:auto;background:white;padding:32px;border-top:6px solid #15766c}'
            'h2{color:#15766c}section{overflow-x:auto;margin:24px 0}table{border-collapse:collapse;width:100%}'
            'th,td{text-align:left;padding:10px;border-bottom:1px solid #dce3e8;overflow-wrap:anywhere}'
            'th{background:#eef5f4}@media print{body,main{padding:0;background:white}}'
            '</style></head><body><main><h1>EraSight — Model Usage &amp; Cost Report</h1>'
            f'<p>Report generated: {escape(datetime.now(timezone.utc).isoformat())}. This is not a run timestamp.</p>'
            f'<section><h2>Deterministic investigation pipeline — {dataset_count} cases</h2>'
            '<p>No LLM provider or model. API calls: 0; input tokens: 0; output tokens: 0; total tokens: 0; '
            'LLM cost: $0.00. The optional advisory layer cannot change output.csv. '
            'These are model costs only, excluding hosting, OCR and development tooling. Run timestamp: Not recorded.</p></section>'
            + sections + '<section><h2>Totals by scope</h2><table><thead>' + headings + '</thead><tbody>'
            + summary('Full-dataset advisory only (mini demo excluded)', totals([main]))
            + summary('Separate mini demo only', totals([demo]))
            + summary('Grand total — all recorded advisory runs above', totals(rows))
            + '</tbody></table></section><section><h2>Accounting and limitations</h2>'
            '<p>Groq openai/gpt-oss-120b pricing uses the historical assumption recorded in '
            'code/evaluation/usage_report.md: $0.15 input and $0.60 output per million tokens, recorded 2026-11-05. '
            'Prices are estimates, not a bill or a current price quote. Other model prices are Not recorded. '
            'Unknown token breakdowns or prices produce no cost estimate. Missing or invalid logs display Not recorded. '
            'Successful and failed calls are shown separately; retry HTTP attempts and unreported provider usage '
            'are not recoverable from these aggregate logs. Legacy clients defaulted omitted provider token counts '
            'to zero, so recorded zeroes cannot prove a provider supplied usage metadata. '
            'The mini demo is excluded from full-dataset totals. Grand totals combine separate runs and must not '
            'be interpreted as the deterministic pipeline cost. Per-case prompts, evidence and identifiers are excluded.</p>'
            '</section></main></body></html>').encode('utf-8')
