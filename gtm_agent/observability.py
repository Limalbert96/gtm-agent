"""Optional OpenTelemetry export for the agent's traces.

Google ADK instruments agent invocations, LLM calls, and tool calls with
OpenTelemetry spans (the same data the `adk web` "Trace" view shows). This module
registers an OTLP exporter so those spans flow to any OTLP-compatible backend -
New Relic, Grafana Tempo, Honeycomb, Jaeger, an OTel Collector, etc.

It is entirely opt-in and vendor-neutral:

  * Nothing happens unless you set an OTLP endpoint (or GTM_ENABLE_TRACING=1).
  * Configuration uses the STANDARD OpenTelemetry env vars, so there are no
    backend hostnames in this code.
  * If the OTel SDK isn't installed, this no-ops with a one-line hint.

Enable it with, e.g.:

    # New Relic (US datacenter) -- see also the EU endpoint otlp.eu01.nr-data.net
    export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net
    export OTEL_EXPORTER_OTLP_HEADERS="api-key=YOUR_NR_LICENSE_KEY"
    export OTEL_SERVICE_NAME=gtm-agent

    # Or a local OpenTelemetry Collector
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

Install the exporter deps (see requirements-otel.txt):
    pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
"""

from __future__ import annotations

import os

_CONFIGURED = False


def _should_enable() -> bool:
    return bool(
        os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        or os.environ.get("GTM_ENABLE_TRACING") == "1"
    )


def configure_tracing() -> bool:
    """Register an OTLP trace exporter as the global tracer provider.

    Returns True if tracing was configured, False if skipped (not enabled or SDK
    missing). Safe to call more than once; only the first call takes effect.
    """
    global _CONFIGURED
    if _CONFIGURED or not _should_enable():
        return _CONFIGURED

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        print(
            "[observability] OTLP endpoint set but OpenTelemetry SDK is not "
            "installed. Run: pip install -r requirements-otel.txt  (tracing disabled)."
        )
        return False

    service_name = os.environ.get("OTEL_SERVICE_NAME", "gtm-agent")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    # OTLPSpanExporter reads OTEL_EXPORTER_OTLP_ENDPOINT / _HEADERS from the env.
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    endpoint = (
        os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or "(default)"
    )
    print(f"[observability] Tracing enabled -> {endpoint} (service.name={service_name})")
    _CONFIGURED = True
    return True
