# Change Log — 2026-07-30

> Synthetic data. All systems and change records are fictional and created
> for the OIOF demo dataset.

This file documents the two infrastructure/application changes deployed on
the incident day that are cited in the evidence manifest as `REL-001` and
`CDN-001`.

## REL-001 — checkout-api 3.12.0

| Field | Value |
|---|---|
| Change type | Application release |
| Service | checkout-api |
| Version | 3.11.4 → 3.12.0 |
| Rollout plan | Canary: NA only, 08:00 UTC. Full fleet (NA + EU + APAC): 09:00 UTC. |
| Change owner | Checkout Engineering |
| Approval | Standard release process, approved 2026-07-29 |
| Rollback available | Yes — previous version image retained, rollback is a standard deployment operation (see `PROC-001` for approval gate) |

### Summary of changes

- Refactored the checkout submission client to use an updated retry
  policy: submission failures now retry up to 3 times with exponential
  backoff, replacing the previous fixed single-retry behavior.
- Minor UI changes to the checkout confirmation screen (not expected to
  affect backend authorization behavior).
- Updated the promotion-code validation client library to a newer minor
  version.

### Release-owner assessment at time of writing

The retry-policy change was intended to *improve* checkout completion
rates for transient failures. Whether it has instead amplified load on
downstream payment providers under latency (by retrying more aggressively
against an already-slow provider) has not yet been confirmed and requires
correlating `LOG-APP-007` (elevated `CHECKOUT_RETRY_EXCEEDED` on 3.12.0)
against `LOG-APP-002` (ProviderAlpha timeouts). No causal claim is made
here; this is a plausible mechanism, not a conclusion.

---

## CDN-001 — checkout-config cache TTL adjustment

| Field | Value |
|---|---|
| Change type | CDN cache-policy configuration |
| Endpoint | `/api/checkout/config` |
| Change | Cache TTL policy adjusted as part of a routine cache-tiering rollout |
| Scope | Rolled out edge-node-by-edge-node; full global propagation not yet confirmed complete at time of writing |
| Applied | 2026-07-30T07:15:00Z |
| Change owner | Platform / CDN team |
| Rollback available | Yes — cache purge and policy revert are standard CDN operations (see `PROC-001` for approval gate) |

### Summary of changes

The cache TTL for the `/api/checkout/config` endpoint (which serves
checkout-relevant feature flags, supported-payment-method lists, and
active-promotion identifiers to clients) was adjusted to reduce origin
load. The rollout to edge nodes is staged rather than atomic, which is a
known source of transient inconsistency during propagation.

### Platform-team note at time of writing

A subset of edge nodes serving APAC traffic (and a smaller subset serving
NA traffic) have been observed returning `cache_status=STALE` for this
endpoint after the change (`GW-API-002`, `GW-API-003`). No EU edge nodes in
the sampled traffic show this behavior (`GW-API-004`). Whether stale
checkout-config payloads are sufficient on their own to cause the
`CONFIG_MISMATCH` errors observed in `LOG-APP-006`, or are a contributing
factor alongside something else, has not yet been confirmed.
