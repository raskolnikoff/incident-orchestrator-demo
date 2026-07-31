# Data Dictionary

All files in this directory are synthetic, generated (where structured) by
`scripts/generate_dataset.py` with a fixed random seed (`42`) for full
reproducibility, or hand-authored (where narrative). See
`dataset/evidence_manifest.yaml` for how records map to evidence IDs.

## `application_logs.jsonl`

One JSON object per line.

| Field | Type | Description |
|---|---|---|
| `timestamp` | string (ISO 8601 UTC) | Event time |
| `log_id` | string | Unique log record identifier |
| `evidence_id` | string | Evidence bucket, see `evidence_manifest.yaml` |
| `service` | string | One of `checkout-api`, `payment-orchestration`, `fraud-decision`, `promotion-service`, `web-storefront`, `mobile-app` |
| `region` | string | `NA`, `EU`, or `APAC` |
| `app_version` | string | Application version, e.g. `3.11.4` or `3.12.0` |
| `payment_method` | string or null | `visa`, `mastercard`, `amex`, `paypal`, `apple_pay`, `google_pay`, or null if not applicable to the service |
| `provider` | string or null | `ProviderAlpha`, `ProviderBeta`, or null |
| `level` | string | `INFO`, `WARN`, or `ERROR` |
| `error_class` | string or null | e.g. `TIMEOUT`, `NETWORK_ERROR`, `DECLINE_FRAUD`, `CONFIG_MISMATCH`, `VALIDATION_ERROR`, `CHECKOUT_RETRY_EXCEEDED`, or null for non-error entries |
| `http_status` | integer | HTTP-style status code associated with the operation |
| `latency_ms` | integer | Operation latency in milliseconds |
| `retry_count` | integer | Number of client-side retries observed for this operation |
| `request_id` | string | Per-request identifier |
| `correlation_id` | string | Correlation identifier for cross-system tracing |
| `sampled` | boolean | True if this record was captured under log sampling (coverage caveat) |
| `message` | string | Human-readable log message |

## `api_gateway_logs.csv`

| Column | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 UTC | Request time |
| `request_id` | string | Gateway request identifier |
| `evidence_id` | string | Evidence bucket |
| `region` | string | `NA`, `EU`, `APAC` |
| `edge_node` | string | CDN edge node identifier |
| `endpoint` | string | Requested API path |
| `method` | string | HTTP method |
| `http_status` | integer | HTTP status code |
| `latency_ms` | integer | Response latency |
| `cache_status` | string | `HIT`, `MISS`, or `STALE` |
| `app_version` | string | Client application version |
| `correlation_id` | string | Correlation identifier |

## `hourly_kpis.csv`

One row per (date, hour, region).

| Column | Type | Description |
|---|---|---|
| `date` | date | `2026-07-29` (baseline) or `2026-07-30` (incident day) |
| `hour_utc` | string | Two-digit hour, `00`–`23` |
| `region` | string | `NA`, `EU`, `APAC` |
| `evidence_id` | string | Evidence bucket |
| `sessions` | integer | Storefront/app sessions in the hour |
| `checkout_attempts` | integer | Checkout submissions attempted |
| `checkout_authorized` | integer | Checkout submissions authorized |
| `checkout_declined` | integer | Checkout submissions declined (fraud or issuer) |
| `checkout_errors` | integer | Checkout submissions failing with a technical error |
| `auth_success_rate` | float | `checkout_authorized / checkout_attempts` |
| `avg_latency_ms` | integer | Average checkout submission latency |
| `campaign_active` | boolean | Whether a marketing campaign was active in this region/hour |

## `payment_metrics.csv`

One row per (region, payment method, 2-hour bucket) on the incident day.

| Column | Type | Description |
|---|---|---|
| `date` | date | `2026-07-30` |
| `time_bucket_start_utc` | string | Start of the 2-hour bucket, e.g. `10:00` |
| `evidence_id` | string | Evidence bucket |
| `region` | string | `NA`, `EU`, `APAC` |
| `payment_method` | string | Payment method |
| `provider` | string | `ProviderAlpha` or `ProviderBeta` |
| `attempts` | integer | Authorization attempts |
| `authorized` | integer | Successful authorizations |
| `declined_fraud` | integer | Declines attributed to fraud rules |
| `declined_issuer` | integer | Declines attributed to the issuing bank |
| `timeouts` | integer | Requests that timed out |
| `gateway_errors` | integer | Requests failing with a gateway-level error |
| `avg_latency_ms` | integer | Average authorization latency |
| `auth_rate` | float | `authorized / attempts` |

## `customer_feedback.csv`

| Column | Type | Description |
|---|---|---|
| `feedback_id` | string | Unique feedback record identifier |
| `evidence_id` | string | Evidence bucket |
| `timestamp_reported` | ISO 8601 UTC | When the customer reported the issue |
| `region` | string | `NA`, `EU`, `APAC` |
| `channel` | string | `support_ticket`, `app_store_review`, `social_media`, `live_chat` |
| `payment_method` | string | Payment method mentioned, if any |
| `symptom_category` | string | Analyst-assigned symptom bucket |
| `sentiment` | string | `negative` or `neutral` |
| `delay_hours_est` | float | Estimated hours between the failure event and the report being filed |
| `free_text` | string | Synthetic customer-style complaint text |

## `campaign_schedule.csv`

| Column | Type | Description |
|---|---|---|
| `campaign_id` | string | Campaign identifier |
| `name` | string | Campaign name |
| `region` | string | Target region |
| `start_utc` / `end_utc` | ISO 8601 UTC | Campaign send window |
| `channel` | string | Marketing channel(s) |
| `expected_traffic_uplift_pct` | integer | Planned traffic uplift estimate |
| `evidence_id` | string | Evidence bucket (`CAMPAIGN-001` for all rows) |
| `notes` | string | Free-text context |

## Narrative files

`incident_brief.md`, `release_notes.md`, `fraud_rule_change.md`,
`vendor_email.md`, `internal_chat.md`, `incident_history.md`,
`operating_procedure.md` are hand-authored Markdown documents. Each is
cited by one or more evidence IDs in `evidence_manifest.yaml`; see that
file for the authoritative mapping.

## `evidence_manifest.yaml`

The evidence catalog. See the file's own header comment for its (Python
stdlib-parseable) format, and `schemas/evidence_manifest.schema.json` for
the logical schema.
