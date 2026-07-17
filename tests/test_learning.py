from __future__ import annotations

import json

import pytest

from hibiki.learning import (
    HYPOTHESIS_MINIMUM_POSTS,
    PERIOD_BOUNDARY_MS,
    STRATEGY_MINIMUM_PERIODS,
    STRATEGY_MINIMUM_POSTS,
    LearningWorkflowError,
    evaluate_strategy,
    surface_hypotheses,
    update_hypothesis_status,
)
from hibiki.records import CausalRepositories, HypothesisRecord, OutcomeRecord
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway


def _create_outcomes(
    sekai: FakeSekaiGateway, count: int, *, period_spread: bool = False
) -> list[OutcomeRecord]:
    """Create 7d outcome records for distinct publications."""
    repositories = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
    outcomes: list[OutcomeRecord] = []
    for index in range(count):
        observed_at = (
            index * PERIOD_BOUNDARY_MS if period_spread else index * 1000
        )
        outcome = repositories.outcomes.put(
            OutcomeRecord(
                stable_id=f"publication-{index}:7d",
                publication_external_id=f"hibiki.publication:hibiki:publication-{index}",
                window="7d",
                observed_at=observed_at,
                metrics={"impressions": 100 + index * 10, "likes": index, "replies": index},
                qualified_replies=index,
            )
        )
        outcomes.append(outcome)
    return outcomes


def _hypothesis_response(outcomes: list[OutcomeRecord]) -> str:
    return json.dumps(
        {
            "hypotheses": [
                {
                    "stable_id": "technical-depth-resonates",
                    "statement": "Posts with technical depth get more qualified replies",
                    "evidence_external_ids": [outcome.external_id for outcome in outcomes],
                }
            ]
        }
    )


def _strategy_response() -> str:
    return json.dumps(
        {
            "recommendation": "Increase code-level detail in posts",
            "confidence_bps": 8500,
        }
    )


class TestHypothesisSurfacing:
    def test_rejects_fewer_than_minimum_posts(self) -> None:
        sekai = FakeSekaiGateway()
        _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS - 1)
        chisei = FakeChiseiGateway("{}")

        with pytest.raises(LearningWorkflowError, match="at least 3"):
            surface_hypotheses(
                sekai,
                chisei,
                "hibiki.publication:hibiki:publication-0",
                "hibiki",
            )

    def test_surfaces_hypothesis_after_minimum_posts(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway(_hypothesis_response(outcomes))

        result = surface_hypotheses(
            sekai,
            chisei,
            outcomes[0].publication_external_id,
            "hibiki",
            clock_ms=lambda: 500,
        )

        assert len(result.hypotheses) == 1
        expected = "Posts with technical depth get more qualified replies"
        assert result.hypotheses[0].statement == expected
        assert result.hypotheses[0].status == "surfaced"
        assert result.comparable_posts == HYPOTHESIS_MINIMUM_POSTS

    def test_rejects_publication_without_completed_outcome(self) -> None:
        sekai = FakeSekaiGateway()
        _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway("{}")

        with pytest.raises(LearningWorkflowError, match="does not have a completed 7d outcome"):
            surface_hypotheses(
                sekai,
                chisei,
                "hibiki.publication:hibiki:nonexistent",
                "hibiki",
            )

    def test_persists_hypothesis_record_in_sekai(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway(_hypothesis_response(outcomes))

        surface_hypotheses(
            sekai, chisei, outcomes[0].publication_external_id, "hibiki", clock_ms=lambda: 500
        )

        repos = CausalRepositories.create(sekai, "hibiki")
        hypothesis = repos.hypotheses.get("technical-depth-resonates")
        assert hypothesis is not None
        assert hypothesis.status == "surfaced"
        assert hypothesis.statement == "Posts with technical depth get more qualified replies"

    def test_records_surfacing_decision(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway(_hypothesis_response(outcomes))

        surface_hypotheses(
            sekai, chisei, outcomes[0].publication_external_id, "hibiki", clock_ms=lambda: 500
        )

        decisions = [d for d in sekai.decisions.values() if d.actor == "hibiki"]
        assert len(decisions) == 1
        assert decisions[0].action == "hibiki.hypothesis_surfacing"
        assert decisions[0].evidence["comparable_posts"] == str(HYPOTHESIS_MINIMUM_POSTS)

    def test_rejects_invalid_chisei_response(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway(json.dumps({"hypotheses": "not-a-list"}))

        with pytest.raises(LearningWorkflowError, match="not a list"):
            surface_hypotheses(
                sekai, chisei, outcomes[0].publication_external_id, "hibiki"
            )

    def test_rejects_hypothesis_referencing_unknown_evidence(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        bad_response = json.dumps(
            {
                "hypotheses": [
                    {
                        "stable_id": "h1",
                        "statement": "A hypothesis",
                        "evidence_external_ids": ["hibiki.outcome:hibiki:nonexistent:7d"],
                    }
                ]
            }
        )
        chisei = FakeChiseiGateway(bad_response)

        with pytest.raises(LearningWorkflowError, match="invalid or unknown evidence"):
            surface_hypotheses(
                sekai, chisei, outcomes[0].publication_external_id, "hibiki"
            )

    def test_resurfacing_preserves_operator_decisions(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        chisei = FakeChiseiGateway(_hypothesis_response(outcomes))

        # First surfacing
        surface_hypotheses(
            sekai, chisei, outcomes[0].publication_external_id, "hibiki", clock_ms=lambda: 500
        )

        # Operator accepts the hypothesis
        update_hypothesis_status(
            sekai,
            "hibiki.hypothesis:hibiki:technical-depth-resonates",
            "accepted",
            "hibiki",
            clock_ms=lambda: 600,
        )

        # Re-run surfacing — same stable_id returned by Chisei
        chisei2 = FakeChiseiGateway(_hypothesis_response(outcomes))
        result = surface_hypotheses(
            sekai, chisei2, outcomes[0].publication_external_id, "hibiki", clock_ms=lambda: 700
        )

        # The hypothesis should retain its "accepted" status, not be overwritten
        assert result.hypotheses[0].status == "accepted"
        repos = CausalRepositories.create(sekai, "hibiki")
        hypothesis = repos.hypotheses.get("technical-depth-resonates")
        assert hypothesis is not None
        assert hypothesis.status == "accepted"


class TestStrategyEvaluation:
    def test_gates_hypothesis_with_insufficient_posts(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, HYPOTHESIS_MINIMUM_POSTS)
        # Create a surfaced hypothesis referencing only 3 outcomes (below 8-post gate)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Short-form posts resonate more",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
            )
        )
        chisei = FakeChiseiGateway("{}")

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 1
        assert "insufficient posts" in result.gated_hypotheses[0].reason
        assert result.gated_hypotheses[0].posts_evaluated == HYPOTHESIS_MINIMUM_POSTS

    def test_gates_hypothesis_with_single_period(self) -> None:
        sekai = FakeSekaiGateway()
        # 8 posts all in the same period (< 7 days apart)
        outcomes = _create_outcomes(sekai, STRATEGY_MINIMUM_POSTS, period_spread=False)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Technical posts resonate",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
            )
        )
        chisei = FakeChiseiGateway("{}")

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 1
        assert "insufficient periods" in result.gated_hypotheses[0].reason
        assert result.gated_hypotheses[0].periods_covered == 1

    def test_recommends_strategy_when_gates_are_met(self) -> None:
        sekai = FakeSekaiGateway()
        # 8 posts spread across multiple periods
        outcomes = _create_outcomes(sekai, STRATEGY_MINIMUM_POSTS, period_spread=True)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Technical posts resonate",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
            )
        )
        chisei = FakeChiseiGateway(_strategy_response())

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 1
        assert result.recommendations[0].recommendation == "Increase code-level detail in posts"
        assert result.recommendations[0].confidence_bps == 8500
        assert result.recommendations[0].actionable is True
        assert result.recommendations[0].posts_evaluated == STRATEGY_MINIMUM_POSTS
        assert result.recommendations[0].periods_covered >= STRATEGY_MINIMUM_PERIODS
        assert len(result.gated_hypotheses) == 0

    def test_does_not_recommend_from_retired_hypotheses(self) -> None:
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, STRATEGY_MINIMUM_POSTS, period_spread=True)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Technical posts resonate",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
                status="retired",
            )
        )
        chisei = FakeChiseiGateway("{}")

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 0

    def test_accepted_hypotheses_are_excluded_from_strategy(self) -> None:
        """Accepted = operator already decided to act on it; no further
        recommendation is needed.  Strategy evaluation only processes
        'surfaced' hypotheses awaiting a decision."""
        sekai = FakeSekaiGateway()
        outcomes = _create_outcomes(sekai, STRATEGY_MINIMUM_POSTS, period_spread=True)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Technical posts resonate",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
                status="accepted",
            )
        )
        chisei = FakeChiseiGateway("{}")

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 0
        assert not chisei.executed_plans

    def test_empty_when_no_hypotheses_surfaced(self) -> None:
        sekai = FakeSekaiGateway()
        _create_outcomes(sekai, STRATEGY_MINIMUM_POSTS, period_spread=True)
        chisei = FakeChiseiGateway("{}")

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 0
        assert result.comparable_posts == STRATEGY_MINIMUM_POSTS

    def test_insufficient_evidence_cannot_produce_recommendation(self) -> None:
        """Deterministic proof: fewer than 8 posts with fewer than 2 periods
        cannot produce an actionable strategy recommendation."""
        sekai = FakeSekaiGateway()
        # Only 5 posts, single period
        outcomes = _create_outcomes(sekai, 5, period_spread=False)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Any hypothesis",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
            )
        )
        chisei = FakeChiseiGateway(_strategy_response())

        result = evaluate_strategy(sekai, chisei, "hibiki")

        # Even though Chisei would respond with a recommendation,
        # the gates prevent it from being surfaced
        assert len(result.recommendations) == 0
        assert len(result.gated_hypotheses) == 1
        assert not chisei.executed_plans  # Chisei was never called

    def test_single_period_evidence_cannot_alter_strategy(self) -> None:
        """Deterministic proof: evidence from a single period cannot alter strategy
        even when 8+ posts are available."""
        sekai = FakeSekaiGateway()
        # 10 posts but all in same period
        outcomes = _create_outcomes(sekai, 10, period_spread=False)
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 200)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="Single-period hypothesis",
                evidence_external_ids=tuple(o.external_id for o in outcomes),
            )
        )
        chisei = FakeChiseiGateway(_strategy_response())

        result = evaluate_strategy(sekai, chisei, "hibiki")

        assert len(result.recommendations) == 0
        assert result.gated_hypotheses[0].reason.startswith("insufficient periods")
        assert not chisei.executed_plans  # Chisei was never called


class TestHypothesisStatusManagement:
    def test_accept_surfaced_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
            )
        )

        result = update_hypothesis_status(
            sekai,
            "hibiki.hypothesis:hibiki:h1",
            "accepted",
            "hibiki",
            clock_ms=lambda: 200,
        )

        assert result.previous_status == "surfaced"
        assert result.new_status == "accepted"
        assert result.hypothesis.status == "accepted"

    def test_reject_surfaced_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
            )
        )

        result = update_hypothesis_status(
            sekai, "hibiki.hypothesis:hibiki:h1", "rejected", "hibiki", clock_ms=lambda: 200
        )

        assert result.previous_status == "surfaced"
        assert result.new_status == "rejected"

    def test_retire_accepted_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
                status="accepted",
            )
        )

        result = update_hypothesis_status(
            sekai, "hibiki.hypothesis:hibiki:h1", "retired", "hibiki", clock_ms=lambda: 200
        )

        assert result.previous_status == "accepted"
        assert result.new_status == "retired"

    def test_cannot_transition_retired_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
                status="retired",
            )
        )

        with pytest.raises(LearningWorkflowError, match="cannot transition"):
            update_hypothesis_status(
                sekai, "hibiki.hypothesis:hibiki:h1", "accepted", "hibiki"
            )

    def test_cannot_transition_rejected_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
                status="rejected",
            )
        )

        with pytest.raises(LearningWorkflowError, match="cannot transition"):
            update_hypothesis_status(
                sekai, "hibiki.hypothesis:hibiki:h1", "retired", "hibiki"
            )

    def test_rejects_invalid_status(self) -> None:
        sekai = FakeSekaiGateway()

        with pytest.raises(LearningWorkflowError, match="must be accepted, rejected, or retired"):
            update_hypothesis_status(
                sekai, "hibiki.hypothesis:hibiki:h1", "surfaced", "hibiki"
            )

    def test_rejects_nonexistent_hypothesis(self) -> None:
        sekai = FakeSekaiGateway()

        with pytest.raises(LearningWorkflowError, match="was not found"):
            update_hypothesis_status(
                sekai, "hibiki.hypothesis:hibiki:nonexistent", "accepted", "hibiki"
            )

    def test_records_status_decision_in_sekai(self) -> None:
        sekai = FakeSekaiGateway()
        repos = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
        repos.hypotheses.put(
            HypothesisRecord(
                stable_id="h1",
                statement="A hypothesis",
                evidence_external_ids=("hibiki.outcome:hibiki:pub-1:7d",),
            )
        )

        update_hypothesis_status(
            sekai, "hibiki.hypothesis:hibiki:h1", "accepted", "hibiki", clock_ms=lambda: 200
        )

        decisions = [d for d in sekai.decisions.values() if d.actor == "operator"]
        assert len(decisions) == 1
        assert decisions[0].action == "hibiki.hypothesis_accepted"
        assert decisions[0].outcome == "accepted"
        assert decisions[0].evidence["previous_status"] == "surfaced"
