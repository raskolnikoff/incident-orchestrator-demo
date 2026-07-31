#!/usr/bin/env python3
"""
generate_dataset.py — Deterministic synthetic dataset generator for the
Operational Incident Orchestration Framework (OIOF) demo.

Generates every raw evidence file under dataset/ for the fictional
"Intermittent Checkout Authorization Degradation" incident at the fictional
company Northstar Commerce. All data is synthetic and generated from a fixed
random seed so the repository is fully reproducible.

Run:
    python3 scripts/generate_dataset.py

This script is idempotent: running it again regenerates byte-identical
output (given the same Python version's json/csv formatting), because all
randomness is drawn from a single seeded random.Random instance in a fixed
call order.

It intentionally encodes several overlapping, partially-contradictory signals
so that no single hypothesis about the incident's root cause is trivially
provable from the data alone:

  H1 - Payment-provider (ProviderAlpha) latency/timeout degradation
  H2 - Regression introduced by the checkout-api 3.12.0 release
  H3 - EU fraud-rule update causing false declines
  H4 - Stale CDN cache for the checkout-config endpoint

See dataset/evidence_manifest.yaml for the evidence catalog these records
are tagged against, and dataset/incident_brief.md for the narrative.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

SEED = 42
RND = random.Random(SEED)

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "dataset"

REGIONS = ["NA", "EU", "APAC"]
PAYMENT_METHODS = ["visa", "mastercard", "amex", "paypal", "apple_pay", "google_pay"]
DIGITAL_WALLETS = {"paypal", "apple_pay", "google_pay"}

BASELINE_DATE = "2026-07-29"
INCIDENT_DATE = "2026-07-30"

# Key event timestamps (UTC), embedded consistently across all generated files.
EVT_CDN_CONFIG_CHANGE = "2026-07-30T07:15:00Z"
EVT_RELEASE_CANARY_NA = "2026-07-30T08:00:00Z"
EVT_RELEASE_FULL_FLEET = "2026-07-30T09:00:00Z"
EVT_FRAUD_RULE_EU = "2026-07-30T09:30:00Z"
EVT_CAMPAIGN_START = "2026-07-30T10:00:00Z"
EVT_PROVIDER_STRESS_START = "2026-07-30T11:00:00Z"
EVT_INCIDENT_DETECTED = "2026-07-30T11:40:00Z"
EVT_PROVIDER_STRESS_END = "2026-07-30T15:00:00Z"
EVT_CAMPAIGN_END = "2026-07-30T16:00:00Z"


def iso(date: str, hour: int, minute: int, second: int) -> str:
    return f"{date}T{hour:02d}:{minute:02d}:{second:02d}Z"


def rand_time(date: str, hour_start: float, hour_end: float) -> tuple[str, int, int, int]:
    """Return (iso_timestamp, hour, minute, second) uniformly within [hour_start, hour_end)."""
    total_seconds = RND.uniform(hour_start * 3600, hour_end * 3600)
    h = int(total_seconds // 3600) % 24
    rem = int(total_seconds % 3600)
    m = rem // 60
    s = rem % 60
    return iso(date, h, m, s), h, m, s


def region_provider(region: str, method: str) -> str:
    """Deterministic-ish provider routing rule used to derive realistic fields."""
    if region == "APAC":
        return "ProviderBeta" if RND.random() < 0.80 else "ProviderAlpha"
    # NA / EU: ProviderAlpha is primary for cards, ProviderBeta favoured for wallets
    if method in DIGITAL_WALLETS:
        return "ProviderAlpha" if RND.random() < 0.55 else "ProviderBeta"
    return "ProviderAlpha" if RND.random() < 0.85 else "ProviderBeta"


# ---------------------------------------------------------------------------
# application_logs.jsonl
# ---------------------------------------------------------------------------

APP_LOG_SERVICES_CORE = ["checkout-api", "payment-orchestration", "fraud-decision"]

def gen_application_logs() -> list[dict]:
    rows: list[dict] = []
    counter = 0

    def next_ids(region: str) -> tuple[str, str]:
        nonlocal counter
        counter += 1
        return f"req-{region.lower()}-{counter:06d}", f"corr-{counter:06d}"

    def base_row(evidence_id, date, hour_range, region, service, app_version,
                 payment_method, provider, level, error_class, http_status,
                 latency_ms, retry_count, message, sampled=False):
        ts, h, m, s = rand_time(date, *hour_range)
        req_id, corr_id = next_ids(region)
        return {
            "timestamp": ts,
            "log_id": f"LOGAPP-{len(rows) + 1:06d}",
            "evidence_id": evidence_id,
            "service": service,
            "region": region,
            "app_version": app_version,
            "payment_method": payment_method,
            "provider": provider,
            "level": level,
            "error_class": error_class,
            "http_status": http_status,
            "latency_ms": latency_ms,
            "retry_count": retry_count,
            "request_id": req_id,
            "correlation_id": corr_id,
            "sampled": sampled,
            "message": message,
        }

    # LOG-APP-001: baseline day control, all regions, healthy mixed services
    for _ in range(40):
        region = RND.choice(REGIONS)
        service = RND.choice(APP_LOG_SERVICES_CORE)
        method = RND.choice(PAYMENT_METHODS) if service != "fraud-decision" else None
        provider = region_provider(region, method) if method else None
        latency = int(RND.gauss(160, 40))
        rows.append(base_row(
            "LOG-APP-001", BASELINE_DATE, (0, 24), region, service, "3.11.4",
            method, provider, "INFO", None, 200, max(40, latency), 0,
            f"{service} request completed normally in {max(40, latency)}ms."
        ))

    # LOG-APP-002: ProviderAlpha timeouts, NA+EU, incident window 11:00-15:00
    for _ in range(45):
        region = RND.choice(["NA", "EU"])
        method = RND.choice(PAYMENT_METHODS)
        is_timeout = RND.random() < 0.60
        latency = int(RND.gauss(4300, 500)) if is_timeout else int(RND.gauss(650, 150))
        rows.append(base_row(
            "LOG-APP-002", INCIDENT_DATE, (11, 15), region, "payment-orchestration",
            RND.choice(["3.11.4", "3.12.0"]), method, "ProviderAlpha",
            "ERROR" if is_timeout else "WARN",
            "TIMEOUT" if is_timeout else "NETWORK_ERROR",
            504 if is_timeout else 502,
            max(latency, 200), RND.choice([0, 1, 1, 2]),
            (f"Payment authorization request to ProviderAlpha timed out after "
             f"{max(latency, 200)}ms." if is_timeout else
             f"Payment authorization request to ProviderAlpha failed with transient "
             f"network error after {max(latency, 200)}ms.")
        ))

    # LOG-APP-003: ProviderBeta, all regions, incident day - healthy control
    for _ in range(35):
        region = RND.choice(REGIONS)
        method = RND.choice(PAYMENT_METHODS)
        latency = max(60, int(RND.gauss(210, 60)))
        rows.append(base_row(
            "LOG-APP-003", INCIDENT_DATE, (0, 24), region, "payment-orchestration",
            RND.choice(["3.11.4", "3.12.0"]), method, "ProviderBeta", "INFO", None,
            200, latency, 0,
            f"Payment authorization request to ProviderBeta completed in {latency}ms."
        ))

    # LOG-APP-004: fraud-decision EU, post 09:30 - elevated false declines
    for _ in range(30):
        method = RND.choice(PAYMENT_METHODS)
        is_decline = RND.random() < 0.55
        rows.append(base_row(
            "LOG-APP-004", INCIDENT_DATE, (9.5, 24), "EU", "fraud-decision",
            RND.choice(["3.11.4", "3.12.0"]), method, None,
            "WARN" if is_decline else "INFO",
            "DECLINE_FRAUD" if is_decline else None,
            200, max(40, int(RND.gauss(110, 30))), 0,
            ("Transaction declined by fraud rule set FR-2026-118 "
             "(velocity threshold exceeded)." if is_decline else
             "Transaction passed fraud evaluation.")
        ))

    # LOG-APP-005: fraud-decision control (EU pre-09:30, and NA/APAC all day)
    for _ in range(30):
        if RND.random() < 0.4:
            region, hour_range = "EU", (0, 9.5)
        else:
            region, hour_range = RND.choice(["NA", "APAC"]), (0, 24)
        method = RND.choice(PAYMENT_METHODS)
        is_decline = RND.random() < 0.08
        rows.append(base_row(
            "LOG-APP-005", INCIDENT_DATE, hour_range, region, "fraud-decision",
            RND.choice(["3.11.4", "3.12.0"]), method, None,
            "WARN" if is_decline else "INFO",
            "DECLINE_FRAUD" if is_decline else None,
            200, max(40, int(RND.gauss(105, 25))), 0,
            ("Transaction declined by fraud rule set (pre-existing threshold)."
             if is_decline else "Transaction passed fraud evaluation.")
        ))

    # LOG-APP-006: CONFIG_MISMATCH, APAC (heavier) + NA (lighter), post 07:15
    for _ in range(28):
        region = "APAC" if RND.random() < 0.75 else "NA"
        service = RND.choice(["checkout-api", "promotion-service"])
        is_mismatch = RND.random() < 0.65
        rows.append(base_row(
            "LOG-APP-006", INCIDENT_DATE, (7.25, 24), region, service,
            RND.choice(["3.11.4", "3.12.0"]), None, None,
            "ERROR" if is_mismatch else "WARN",
            "CONFIG_MISMATCH" if is_mismatch else "VALIDATION_ERROR",
            409 if is_mismatch else 422, max(50, int(RND.gauss(180, 50))), 0,
            ("Checkout configuration signature mismatch detected; edge-cached "
             "checkout-config payload does not match origin version." if is_mismatch
             else "Promotion payload validation warning during checkout render.")
        ))

    # LOG-APP-007: CHECKOUT_RETRY_EXCEEDED on 3.12.0, all regions, post release
    for _ in range(32):
        region = RND.choice(REGIONS)
        method = RND.choice(PAYMENT_METHODS)
        is_retry_issue = RND.random() < 0.55
        retries = RND.choice([3, 4, 5, 6]) if is_retry_issue else RND.choice([0, 1])
        rows.append(base_row(
            "LOG-APP-007", INCIDENT_DATE, (9, 24), region, "checkout-api", "3.12.0",
            method, region_provider(region, method),
            "ERROR" if is_retry_issue else "INFO",
            "CHECKOUT_RETRY_EXCEEDED" if is_retry_issue else None,
            409 if is_retry_issue else 200, max(80, int(RND.gauss(900, 300))), retries,
            ("Checkout submission exceeded automatic retry budget "
             f"({retries} attempts) before client abandonment." if is_retry_issue
             else "Checkout submission completed within retry budget.")
        ))

    # LOG-APP-008: 3.11.4 control / stragglers on checkout-api
    for _ in range(25):
        region = RND.choice(REGIONS)
        method = RND.choice(PAYMENT_METHODS)
        rows.append(base_row(
            "LOG-APP-008", INCIDENT_DATE, (0, 24), region, "checkout-api", "3.11.4",
            method, region_provider(region, method), "INFO", None, 200,
            max(60, int(RND.gauss(230, 60))), RND.choice([0, 0, 1]),
            "Checkout submission completed within retry budget."
        ))

    # LOG-APP-009: web-storefront / mobile-app general traffic, all day
    for _ in range(30):
        region = RND.choice(REGIONS)
        service = RND.choice(["web-storefront", "mobile-app"])
        rows.append(base_row(
            "LOG-APP-009", INCIDENT_DATE, (0, 24), region, service,
            RND.choice(["3.11.4", "3.12.0"]), None, None, "INFO", None, 200,
            max(30, int(RND.gauss(140, 40))), 0,
            f"{service} page rendered successfully."
        ))

    # LOG-APP-010: APAC log-volume gap 13:00-14:00 (sampling / pipeline gap)
    for _ in range(5):
        method = RND.choice(PAYMENT_METHODS)
        rows.append(base_row(
            "LOG-APP-010", INCIDENT_DATE, (13, 14), "APAC", "checkout-api", "3.12.0",
            method, region_provider("APAC", method), "INFO", None, 200,
            max(60, int(RND.gauss(200, 50))), 0,
            "Checkout submission completed within retry budget.", sampled=True
        ))

    rows.sort(key=lambda r: r["timestamp"])
    for i, r in enumerate(rows, start=1):
        r["log_id"] = f"LOGAPP-{i:06d}"
    return rows


# ---------------------------------------------------------------------------
# api_gateway_logs.csv
# ---------------------------------------------------------------------------

def gen_api_gateway_logs() -> list[dict]:
    rows: list[dict] = []
    counter = 0

    def next_req(region: str) -> str:
        nonlocal counter
        counter += 1
        return f"gwreq-{region.lower()}-{counter:06d}"

    def add(evidence_id, date, hour_range, region, endpoint, method_http,
            http_status, latency_ms, cache_status, edge_node, app_version):
        ts, *_ = rand_time(date, *hour_range)
        rows.append({
            "timestamp": ts,
            "request_id": next_req(region),
            "evidence_id": evidence_id,
            "region": region,
            "edge_node": edge_node,
            "endpoint": endpoint,
            "method": method_http,
            "http_status": http_status,
            "latency_ms": latency_ms,
            "cache_status": cache_status,
            "app_version": app_version,
            "correlation_id": f"corr-gw-{counter:06d}",
        })

    ENDPOINTS = ["/api/checkout/config", "/api/checkout/submit", "/api/cart/items",
                 "/api/promotions/active", "/api/session/refresh"]

    # GW-API-001: baseline day control
    for _ in range(30):
        region = RND.choice(REGIONS)
        add("GW-API-001", BASELINE_DATE, (0, 24), region, RND.choice(ENDPOINTS),
            "GET", 200, max(20, int(RND.gauss(90, 25))), "HIT",
            f"edge-{region.lower()}-{RND.randint(1, 6):02d}", "3.11.4")

    # GW-API-002: checkout-config STALE cache, APAC edges, post 07:15
    apac_stale_edges = [f"edge-apac-{n:02d}" for n in (1, 2, 3)]
    for _ in range(30):
        stale = RND.random() < 0.7
        add("GW-API-002", INCIDENT_DATE, (7.25, 24), "APAC", "/api/checkout/config",
            "GET", 200 if stale else 200,
            max(20, int(RND.gauss(95, 20))),
            "STALE" if stale else "MISS",
            RND.choice(apac_stale_edges), RND.choice(["3.11.4", "3.12.0"]))

    # GW-API-003: checkout-config STALE cache, NA edges (smaller subset)
    na_stale_edges = [f"edge-na-{n:02d}" for n in (4,)]
    for _ in range(15):
        stale = RND.random() < 0.5
        add("GW-API-003", INCIDENT_DATE, (7.25, 24), "NA", "/api/checkout/config",
            "GET", 200, max(20, int(RND.gauss(95, 20))),
            "STALE" if stale else "HIT",
            RND.choice(na_stale_edges), RND.choice(["3.11.4", "3.12.0"]))

    # GW-API-004: checkout-config normal HIT/MISS EU control (unaffected edges)
    for _ in range(25):
        add("GW-API-004", INCIDENT_DATE, (0, 24), "EU", "/api/checkout/config",
            "GET", 200, max(20, int(RND.gauss(85, 20))),
            RND.choice(["HIT", "HIT", "MISS"]),
            f"edge-eu-{RND.randint(1, 6):02d}", RND.choice(["3.11.4", "3.12.0"]))

    # GW-API-005: general checkout-api gateway traffic, incident day, campaign load
    for _ in range(50):
        region = RND.choice(REGIONS)
        endpoint = RND.choice(ENDPOINTS)
        elevated = RND.random() < 0.25
        add("GW-API-005", INCIDENT_DATE, (10, 20), region, endpoint,
            RND.choice(["GET", "POST"]),
            503 if elevated else 200,
            max(40, int(RND.gauss(520, 180))) if elevated else max(30, int(RND.gauss(150, 50))),
            RND.choice(["HIT", "MISS"]),
            f"edge-{region.lower()}-{RND.randint(1, 6):02d}",
            RND.choice(["3.11.4", "3.12.0"]))

    # GW-API-006: pre-campaign baseline traffic within incident day (00:00-10:00)
    for _ in range(30):
        region = RND.choice(REGIONS)
        add("GW-API-006", INCIDENT_DATE, (0, 10), region, RND.choice(ENDPOINTS),
            "GET", 200, max(20, int(RND.gauss(95, 25))), RND.choice(["HIT", "MISS"]),
            f"edge-{region.lower()}-{RND.randint(1, 6):02d}", "3.11.4")

    rows.sort(key=lambda r: r["timestamp"])
    return rows


# ---------------------------------------------------------------------------
# hourly_kpis.csv
# ---------------------------------------------------------------------------

def gen_hourly_kpis() -> list[dict]:
    rows: list[dict] = []
    for date in (BASELINE_DATE, INCIDENT_DATE):
        for region in REGIONS:
            for hour in range(24):
                if date == BASELINE_DATE:
                    evidence_id = "KPI-HOURLY-001"
                elif region == "NA":
                    evidence_id = "KPI-HOURLY-002"
                elif region == "EU":
                    evidence_id = "KPI-HOURLY-003"
                else:
                    evidence_id = "KPI-HOURLY-004"

                base_sessions = {"NA": 4200, "EU": 3300, "APAC": 2100}[region]
                campaign_active = (date == INCIDENT_DATE and 10 <= hour < 16
                                    and region in ("NA", "EU"))
                daypart_factor = 1.0 + 0.6 * (1 - abs(hour - 14) / 14)
                sessions = int(base_sessions * daypart_factor * RND.uniform(0.92, 1.08))
                if campaign_active:
                    sessions = int(sessions * RND.uniform(1.35, 1.65))

                attempts = int(sessions * RND.uniform(0.34, 0.40))

                # Baseline auth-success rate
                base_rate = RND.uniform(0.965, 0.978)
                rate = base_rate
                if date == INCIDENT_DATE:
                    if region in ("NA", "EU") and 11 <= hour < 15:
                        rate -= RND.uniform(0.05, 0.09)  # ProviderAlpha stress
                    if region == "EU" and hour >= 10:
                        rate -= RND.uniform(0.015, 0.035)  # fraud rule effect
                    if region == "APAC" and hour >= 8:
                        rate -= RND.uniform(0.01, 0.025)  # CDN config mismatch effect
                    if region in ("NA", "EU") and 10 <= hour < 16:
                        rate -= RND.uniform(0.0, 0.01)  # campaign volume/capacity edge effect
                rate = max(0.80, min(0.985, rate))

                authorized = int(attempts * rate)
                remainder = attempts - authorized
                declined = int(remainder * RND.uniform(0.55, 0.75))
                errors = remainder - declined
                avg_latency = int(RND.gauss(
                    260 if (date == INCIDENT_DATE and region in ("NA", "EU") and 11 <= hour < 15)
                    else 150, 35))

                rows.append({
                    "date": date,
                    "hour_utc": f"{hour:02d}",
                    "region": region,
                    "evidence_id": evidence_id,
                    "sessions": sessions,
                    "checkout_attempts": attempts,
                    "checkout_authorized": authorized,
                    "checkout_declined": declined,
                    "checkout_errors": max(errors, 0),
                    "auth_success_rate": round(authorized / attempts, 4) if attempts else 0,
                    "avg_latency_ms": max(60, avg_latency),
                    "campaign_active": campaign_active,
                })
    return rows


# ---------------------------------------------------------------------------
# payment_metrics.csv
# ---------------------------------------------------------------------------

def gen_payment_metrics() -> list[dict]:
    rows: list[dict] = []
    bucket_starts = list(range(0, 24, 2))  # 12 two-hour buckets

    for region in REGIONS:
        for method in PAYMENT_METHODS:
            provider = region_provider(region, method)
            for bucket_start in bucket_starts:
                bucket_end = bucket_start + 2
                in_stress_window = EVT_PROVIDER_STRESS_START[11:13] <= f"{bucket_start:02d}" and bucket_start < 16
                # Evidence-id classification (priority order matters)
                if bucket_start < 8:
                    evidence_id = "PAY-METRIC-005"  # pre-event baseline within incident day
                elif provider == "ProviderAlpha" and region in ("NA", "EU") and 10 <= bucket_start < 16:
                    evidence_id = "PAY-METRIC-001"  # provider stress window
                elif provider == "ProviderBeta":
                    evidence_id = "PAY-METRIC-002"  # healthy provider control
                elif region == "EU" and bucket_start >= 10:
                    evidence_id = "PAY-METRIC-003"  # EU fraud-rule window
                elif region in ("NA", "APAC") and bucket_start >= 10:
                    evidence_id = "PAY-METRIC-004"  # non-EU fraud control
                elif region == "APAC":
                    evidence_id = "PAY-METRIC-007"
                else:
                    evidence_id = "PAY-METRIC-006"  # general per-method breakdown

                base_attempts = {"NA": 260, "EU": 210, "APAC": 140}[region]
                method_share = {
                    "visa": 0.30, "mastercard": 0.25, "amex": 0.10,
                    "paypal": 0.15, "apple_pay": 0.12, "google_pay": 0.08,
                }[method]
                campaign_boost = 1.5 if (region in ("NA", "EU") and 10 <= bucket_start < 16) else 1.0
                attempts = max(5, int(base_attempts * method_share * campaign_boost * RND.uniform(0.85, 1.15)))

                timeout_rate = 0.02
                if provider == "ProviderAlpha" and region in ("NA", "EU") and 10 <= bucket_start < 16:
                    timeout_rate = RND.uniform(0.14, 0.22)
                elif provider == "ProviderAlpha":
                    timeout_rate = RND.uniform(0.02, 0.04)
                else:
                    timeout_rate = RND.uniform(0.005, 0.02)

                fraud_decline_rate = 0.03
                if region == "EU" and bucket_start >= 10:
                    fraud_decline_rate = RND.uniform(0.11, 0.19)
                else:
                    fraud_decline_rate = RND.uniform(0.02, 0.05)

                issuer_decline_rate = RND.uniform(0.02, 0.05)
                gateway_error_rate = RND.uniform(0.01, 0.03)
                if region == "APAC" and bucket_start >= 8:
                    gateway_error_rate += RND.uniform(0.01, 0.03)  # CDN config-mismatch spillover

                timeouts = int(attempts * timeout_rate)
                declined_fraud = int(attempts * fraud_decline_rate)
                declined_issuer = int(attempts * issuer_decline_rate)
                gateway_errors = int(attempts * gateway_error_rate)
                authorized = max(0, attempts - timeouts - declined_fraud - declined_issuer - gateway_errors)

                avg_latency = int(RND.gauss(
                    600 if evidence_id == "PAY-METRIC-001" else 180, 60))

                rows.append({
                    "date": INCIDENT_DATE,
                    "time_bucket_start_utc": f"{bucket_start:02d}:00",
                    "evidence_id": evidence_id,
                    "region": region,
                    "payment_method": method,
                    "provider": provider,
                    "attempts": attempts,
                    "authorized": authorized,
                    "declined_fraud": declined_fraud,
                    "declined_issuer": declined_issuer,
                    "timeouts": timeouts,
                    "gateway_errors": gateway_errors,
                    "avg_latency_ms": max(50, avg_latency),
                    "auth_rate": round(authorized / attempts, 4) if attempts else 0,
                })
    return rows


# ---------------------------------------------------------------------------
# customer_feedback.csv
# ---------------------------------------------------------------------------

NA_TEMPLATES = [
    "My {method} card was declined at checkout but my bank shows no attempt. Order never completed.",
    "Tried to pay with {method}, got 'transaction could not be completed' three times in a row.",
    "Checkout kept spinning and then said my {method} payment failed. I was charged twice on my statement.",
    "Payment declined immediately for {method}, no reason given. Works fine on other sites.",
]
EU_TEMPLATES = [
    "Card ({method}) rejected at checkout, message said 'please contact your bank' — bank confirms no issue.",
    "My usual {method} card suddenly stopped working on your site today, worked yesterday.",
    "Got a fraud warning message when trying to pay with {method}, but this is my normal card.",
    "Payment blocked with {method}, very frustrating as I use this card here every week.",
]
APAC_TEMPLATES = [
    "Checkout page showed an error about invalid configuration, could not complete order with {method}.",
    "App crashed during checkout, page said something about session/config error.",
    "Promo code disappeared and checkout page looked outdated, then payment with {method} failed.",
    "Getting a strange error page when trying to check out, tried refreshing several times.",
]
SLOW_TEMPLATES = [
    "Checkout spinner just kept loading for over a minute before failing with {method}.",
    "Site felt very slow during checkout today, payment with {method} eventually timed out.",
    "Page hung on 'processing payment' for ages then errored out.",
]
AMBIGUOUS_TEMPLATES = [
    "Not sure what happened but my order didn't go through, tried twice with different cards.",
    "Something weird with checkout today, hard to describe, just didn't work properly.",
    "Order failed, then succeeded on retry an hour later. Confusing experience.",
    "Mixed results — first attempt failed, second one worked fine, no idea why.",
]

CHANNELS = ["support_ticket", "app_store_review", "social_media", "live_chat"]


def gen_customer_feedback() -> list[dict]:
    rows: list[dict] = []
    fid = 0

    def add(evidence_id, region, hour_range, symptom, template_list, delay_range, sentiment):
        nonlocal fid
        fid += 1
        ts, *_ = rand_time(INCIDENT_DATE, *hour_range)
        method = RND.choice(PAYMENT_METHODS)
        text = RND.choice(template_list).format(method=method.replace("_", " "))
        rows.append({
            "feedback_id": f"CS-{fid:04d}",
            "evidence_id": evidence_id,
            "timestamp_reported": ts,
            "region": region,
            "channel": RND.choice(CHANNELS),
            "payment_method": method,
            "symptom_category": symptom,
            "sentiment": sentiment,
            "delay_hours_est": round(RND.uniform(*delay_range), 1),
            "free_text": text,
        })

    for _ in range(8):
        add("CS-FEEDBACK-001", "NA", (11, 18), "declined_payment", NA_TEMPLATES, (0.2, 3.0), "negative")
    for _ in range(8):
        add("CS-FEEDBACK-002", "EU", (10, 20), "declined_payment_fraud_like", EU_TEMPLATES, (0.2, 4.0), "negative")
    for _ in range(7):
        add("CS-FEEDBACK-003", "APAC", (8, 22), "config_or_page_error", APAC_TEMPLATES, (0.3, 5.0), "negative")
    for _ in range(8):
        add("CS-FEEDBACK-004", RND.choice(REGIONS), (10, 20), "slow_checkout_timeout", SLOW_TEMPLATES, (0.2, 2.5), "negative")
    for _ in range(5):
        add("CS-FEEDBACK-005", RND.choice(REGIONS), (11, 16), "delayed_report", RND.choice([NA_TEMPLATES, EU_TEMPLATES, SLOW_TEMPLATES]), (6.0, 18.0), "negative")
    for _ in range(4):
        add("CS-FEEDBACK-006", RND.choice(REGIONS), (9, 22), "ambiguous_mixed", AMBIGUOUS_TEMPLATES, (0.5, 6.0), "neutral")

    rows.sort(key=lambda r: r["timestamp_reported"])
    return rows


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    # lineterminator="\n" is required: csv.writer defaults to "\r\n"
    # regardless of platform, which would make output depend on git's
    # core.autocrlf normalization at commit time rather than being
    # deterministic on disk. See CI safety notes in .gitattributes.
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    app_logs = gen_application_logs()
    write_jsonl(DATASET_DIR / "application_logs.jsonl", app_logs)
    print(f"application_logs.jsonl: {len(app_logs)} records")

    gw_logs = gen_api_gateway_logs()
    write_csv(DATASET_DIR / "api_gateway_logs.csv", gw_logs, [
        "timestamp", "request_id", "evidence_id", "region", "edge_node", "endpoint",
        "method", "http_status", "latency_ms", "cache_status", "app_version", "correlation_id",
    ])
    print(f"api_gateway_logs.csv: {len(gw_logs)} rows")

    kpis = gen_hourly_kpis()
    write_csv(DATASET_DIR / "hourly_kpis.csv", kpis, [
        "date", "hour_utc", "region", "evidence_id", "sessions", "checkout_attempts",
        "checkout_authorized", "checkout_declined", "checkout_errors",
        "auth_success_rate", "avg_latency_ms", "campaign_active",
    ])
    print(f"hourly_kpis.csv: {len(kpis)} rows")

    pay = gen_payment_metrics()
    write_csv(DATASET_DIR / "payment_metrics.csv", pay, [
        "date", "time_bucket_start_utc", "evidence_id", "region", "payment_method",
        "provider", "attempts", "authorized", "declined_fraud", "declined_issuer",
        "timeouts", "gateway_errors", "avg_latency_ms", "auth_rate",
    ])
    print(f"payment_metrics.csv: {len(pay)} rows")

    fb = gen_customer_feedback()
    write_csv(DATASET_DIR / "customer_feedback.csv", fb, [
        "feedback_id", "evidence_id", "timestamp_reported", "region", "channel",
        "payment_method", "symptom_category", "sentiment", "delay_hours_est", "free_text",
    ])
    print(f"customer_feedback.csv: {len(fb)} rows")


if __name__ == "__main__":
    main()
