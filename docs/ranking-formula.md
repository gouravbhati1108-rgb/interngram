# Ranking Formula

Interngram company rankings are computed from verified intern feedback and operational metrics.

## Composite Score

```
score = (
  0.25 * verified_review_avg +
  0.15 * completion_rate +
  0.15 * ppo_conversion_rate +
  0.15 * learning_score +
  0.10 * mentorship_score +
  0.10 * trust_score -
  0.10 * complaint_rate_penalty
) * 100
```

All factors are normalized to the 0–1 range before weighting.

## Factor Definitions

| Factor | Source | Normalization |
|--------|--------|---------------|
| verified_review_avg | Approved reviews' recommendation_score | avg / 5 |
| completion_rate | completed applications / total applications | 0–1 |
| ppo_conversion_rate | accepted / completed applications | 0–1 |
| learning_score | Approved reviews' learning_score | avg / 5 |
| mentorship_score | Approved reviews' mentorship_score | avg / 5 |
| trust_score | 1.0 if company verified, else 0.5 | binary |
| complaint_rate_penalty | flagged reviews / total reviews | capped at 1.0 |

## Provisional Badge

Companies with fewer than 3 approved verified reviews receive a provisional badge. Their composite score is multiplied by 0.7 until they reach the threshold.

## Recalculation

- Nightly at 02:00 UTC via APScheduler
- On-demand when reviews are moderated or complaints resolved
- Leaderboard cached in Redis for 5 minutes
