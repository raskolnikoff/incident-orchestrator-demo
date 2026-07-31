# Incident History — Context for Pattern Recognition (`HIST-001`)

> Synthetic data. All prior incidents referenced here are fictional and
> created for the OIOF demo dataset.

Three prior Northstar Commerce incidents from the preceding twelve months
are summarized below for pattern context only. **Historical base rates are
useful context for prioritizing investigation effort — they are not
evidence about the cause of the current incident** and must not be cited
as if they were.

| Incident ID | Date | Summary | Resolved cause |
|---|---|---|---|
| INC-2025-1104-CHECKOUT | 2025-11-04 | Checkout authorization dip in NA during a peak sales event | Payment-provider-side capacity degradation (ProviderAlpha), acknowledged by vendor after 6 hours |
| INC-2026-0212-CHECKOUT | 2026-02-12 | Brief global authorization dip, ~40 minutes | Payment-provider-side degradation (ProviderBeta), self-resolved |
| INC-2026-0521-CDN | 2026-05-21 | Stale promotion pricing displayed intermittently in APAC and EU | CDN cache-invalidation regression following a config rollout; required manual purge |

## Why this context matters, and why it's dangerous

Two of the last three related incidents were ultimately payment-provider
issues, and the current incident includes a provider-timeout signal
(`LOG-APP-002`) — this is a legitimate reason to prioritize the provider
hypothesis (`H1`) for early investigation effort. It is **not** a reason to
treat `H1` as more likely to be correct than the evidence in the current
incident actually supports; base-rate reasoning can anchor investigators
toward a familiar answer and away from a genuinely different or
multi-cause situation, which is part of what makes this incident's
evidence set deliberately ambiguous (see `dataset/incident_brief.md`,
"Why this is not a single-cause incident").

Note also that a CDN-caching regression (`INC-2026-0521-CDN`) is in this
same history, and the current incident includes an active CDN change
(`CDN-001`) with observed staleness (`GW-API-002`, `GW-API-003`) — so
history offers precedent for *both* `H1` and `H4`, without resolving which
(if either, or both) applies here.
