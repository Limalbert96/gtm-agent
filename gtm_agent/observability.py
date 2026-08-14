"""Optional OpenTelemetry export for the agent's telemetry.

Google ADK instruments agent invocations, LLM calls, and tool calls with
OpenTelemetry spans (the same data the `adk web` "Trace" view shows). This module
registers OTLP exporters for all three OTel signals - traces, metrics, and logs -
so they flow to any OTLP-compatible backend: New Relic, Grafana, Honeycomb, an
OpenTelemetry Collector, etc.

There is NOTHING to edit in this file to point it at a backend, and no backend
hostname appears here. Configuration is entirely environment-driven, using the
standard OTel env vars:

    OTEL_EXPORTER_OTLP_ENDPOINT   turns everything on (base URL, no /v1/... path)
    OTEL_EXPORTER_OTLP_HEADERS    auth - just the API key (see _normalize_headers)
    OTEL_SERVICE_NAME             service name (default "gtm-agent")

Per-signal opt-outs, for when one is noisy or your backend doesn't take it:

    GTM_OTEL_METRICS=0            skip the metrics pipeline
    GTM_OTEL_LOGS=0               skip the logs pipeline
    GTM_OTEL_LOG_LEVEL=WARNING    minimum level shipped as logs (default INFO)

Install the exporter deps with `pip install -r requirements-otel.txt`; the
Dockerfile already includes them. See the "Observability" section of README.md for
backend-specific settings (New Relic's regional endpoints, which key to use, and
the delta-temporality preference for metrics).
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


def _flag(name: str, default: bool = True) -> bool:
    """Read a boolean-ish env var ("0"/"false"/"no"/"off" are False)."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off")


# The header name a bare key is sent as. New Relic's is "api-key".
_BARE_KEY_HEADER = "api-key"


def _normalize_headers() -> None:
    """Let OTEL_EXPORTER_OTLP_HEADERS hold nothing but the API key.

    OTLP defines that variable as a comma-separated list of `name=value` HTTP
    headers, so a New Relic key strictly has to be written `api-key=<key>`. That
    doubled `=` reads like a typo next to scalar vars like OTEL_SERVICE_NAME, and
    getting it wrong fails silently -- the SDK logs "Header format invalid!", sends
    no auth header, and every export 403s while the app looks perfectly healthy.

    So a value with no `=` is treated as a bare key and expanded to
    "api-key=<key>". A value that already contains `=` passes through untouched, so
    the spec form, multi-header values, and other backends' header names
    (e.g. "x-honeycomb-team=<key>") all keep working as specified.

    Per-signal variants (OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS}_HEADERS) are left
    alone: reaching for one of those means you know the spec, so use its form.
    """
    var = "OTEL_EXPORTER_OTLP_HEADERS"
    raw = os.environ.get(var, "").strip()
    if not raw or "=" in raw:
        return

    os.environ[var] = f"{_BARE_KEY_HEADER}={raw}"
    # Never log the key itself.
    print(f"[observability] {var}: bare key expanded to '{_BARE_KEY_HEADER}=<key>'")


def configure_telemetry() -> bool:
    """Register OTLP exporters for traces, metrics, and logs.

    Returns True if at least one signal was configured, False if skipped (not
    enabled, or the SDK isn't installed). Safe to call more than once; only the
    first call takes effect.
    """
    global _CONFIGURED
    if _CONFIGURED or not _should_enable():
        return _CONFIGURED

    # Must run before any exporter is constructed -- they read the env at init.
    _normalize_headers()

    try:
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        print(
            "[observability] OTLP endpoint set but OpenTelemetry SDK is not "
            "installed. Run: pip install -r requirements-otel.txt  (telemetry disabled)."
        )
        return False

    # Resource.create() also merges OTEL_RESOURCE_ATTRIBUTES from the env, so
    # things like deployment.environment can be set without touching code.
    service_name = os.environ.get("OTEL_SERVICE_NAME", "gtm-agent")
    resource = Resource.create({"service.name": service_name})

    signals = []
    if _configure_traces(resource):
        signals.append("traces")
    if _flag("GTM_OTEL_METRICS") and _configure_metrics(resource):
        signals.append("metrics")
    if _flag("GTM_OTEL_LOGS") and _configure_logs(resource):
        signals.append("logs")

    if not signals:
        print(
            "[observability] OTLP endpoint set but no exporter could be loaded. "
            "Run: pip install -r requirements-otel.txt  (telemetry disabled)."
        )
        return False

    endpoint = (
        os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or "(default)"
    )
    print(
        f"[observability] OTel enabled -> {endpoint} "
        f"(service.name={service_name}, signals={'+'.join(signals)})"
    )
    _CONFIGURED = True
    return True


def _configure_traces(resource) -> bool:
    """Spans: ADK's agent/LLM/tool instrumentation."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return False

    provider = TracerProvider(resource=resource)
    # The exporters read OTEL_EXPORTER_OTLP_ENDPOINT / _HEADERS from the env.
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    return True


def _configure_metrics(resource) -> bool:
    """Metrics: whatever instrumentation emits. ADK is trace-first, so this
    pipeline is mostly a destination for anything you add yourself."""
    try:
        from opentelemetry import metrics
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    except ImportError:
        return False

    # Export interval comes from OTEL_METRIC_EXPORT_INTERVAL (default 60s).
    reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
    return True


def _configure_logs(resource) -> bool:
    """Logs: ship stdlib `logging` records over OTLP, correlated to the active
    span (the SDK stamps trace_id/span_id on each record automatically)."""
    try:
        # The SDK still exposes the logs pipeline under a private module path.
        # It's stable in practice, but guard the import so an SDK reshuffle can
        # never break app startup.
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.exporter.otlp.proto.http._log_exporter import (
            OTLPLogExporter,
        )
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    except ImportError:
        return False

    import logging

    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    set_logger_provider(provider)

    level_name = os.environ.get("GTM_OTEL_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.addHandler(LoggingHandler(level=level, logger_provider=provider))
    # The root logger defaults to WARNING, which would drop INFO records before
    # the handler ever sees them. Only ever loosen it, never tighten.
    if root.level == logging.NOTSET or root.level > level:
        root.setLevel(level)
    # Keeping the floor at INFO also avoids a feedback loop: the exporter's own
    # HTTP client (urllib3) logs at DEBUG, which would otherwise generate logs
    # about sending logs.
    return True


# Back-compat: this module used to export traces only.
configure_tracing = configure_telemetry
