from app.services.ranking import PROVISIONAL_DAMPENING, calculate_composite_score


def test_ranking_full_score():
    factors = {
        "verified_review_avg": 1.0,
        "completion_rate": 1.0,
        "ppo_conversion_rate": 1.0,
        "learning_score": 1.0,
        "mentorship_score": 1.0,
        "trust_score": 1.0,
        "complaint_rate_penalty": 0.0,
    }
    score = calculate_composite_score(factors, is_provisional=False)
    assert score == 90.0


def test_ranking_provisional_dampening():
    factors = {
        "verified_review_avg": 1.0,
        "completion_rate": 1.0,
        "ppo_conversion_rate": 1.0,
        "learning_score": 1.0,
        "mentorship_score": 1.0,
        "trust_score": 1.0,
        "complaint_rate_penalty": 0.0,
    }
    score = calculate_composite_score(factors, is_provisional=True)
    assert score == round(90.0 * PROVISIONAL_DAMPENING, 2)


def test_ranking_complaint_penalty():
    factors = {
        "verified_review_avg": 0.8,
        "completion_rate": 0.5,
        "ppo_conversion_rate": 0.3,
        "learning_score": 0.7,
        "mentorship_score": 0.6,
        "trust_score": 1.0,
        "complaint_rate_penalty": 0.5,
    }
    score = calculate_composite_score(factors, is_provisional=False)
    assert 0 <= score <= 100
