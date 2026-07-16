from __future__ import annotations

import grpc

from hibiki.contracts import sekai_pb2
from hibiki.records import (
    CausalRepositories,
    HypothesisRecord,
    OutcomeRecord,
    ProposalRecord,
    PublicationRecord,
    SourceRecord,
    sha256_text,
)
from hibiki.schema import register_schema_types
from tests.fakes import FakeSekaiGateway


def test_fake_proposal_lifecycle_round_trips_through_sekai() -> None:
    gateway = FakeSekaiGateway()
    register_schema_types(gateway)
    repositories = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: 1_750_000_000_000)

    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=sha256_text("bounded evidence"),
        )
    )
    proposal = repositories.proposals.put(
        ProposalRecord(
            stable_id="proposal-abc123",
            source_external_id=source.external_id,
            evidence_hash=source.evidence_hash,
            draft="We made retries deterministic.",
            decision_ref="decision-1",
            operation_id="operation-1",
        )
    )
    approved = repositories.proposals.put(proposal.with_status("approved"))
    publication = repositories.publications.put(
        PublicationRecord(
            stable_id="publication-abc123",
            proposal_external_id=approved.external_id,
            final_text=approved.draft,
            approval_id="approval-1",
        )
    )
    outcome = repositories.outcomes.put(
        OutcomeRecord(
            stable_id="publication-abc123:7d",
            publication_external_id=publication.external_id,
            window="7d",
            observed_at=1_750_604_800_000,
            metrics={"impressions": 1200, "likes": 20, "replies": 3},
            qualified_replies=2,
        )
    )
    hypothesis = repositories.hypotheses.put(
        HypothesisRecord(
            stable_id="deterministic-retries",
            statement="Concrete retry invariants attract substantive technical replies.",
            evidence_external_ids=(outcome.external_id,),
        )
    )

    assert repositories.sources.get(source.stable_id) == source
    assert repositories.proposals.get(proposal.stable_id) == approved
    assert repositories.publications.get(publication.stable_id) == publication
    assert repositories.outcomes.get(outcome.stable_id) == outcome
    assert repositories.hypotheses.get(hypothesis.stable_id) == hypothesis
    assert len(gateway.objects) == 5
    assert gateway.object_updates == [proposal.external_id]


def test_identical_retry_is_a_no_op_with_a_stable_object_id() -> None:
    gateway = FakeSekaiGateway()
    repositories = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: 123)
    source = SourceRecord(
        stable_id="example/tenkai@abc123",
        repository="example/tenkai",
        revision="abc123",
        public_url="https://github.com/example/tenkai/commit/abc123",
        evidence_hash=sha256_text("bounded evidence"),
    )

    first = repositories.sources.put(source)
    object_id = next(iter(gateway.objects))
    second = repositories.sources.put(source)

    assert first == second == source
    assert next(iter(gateway.objects)) == object_id
    assert gateway.object_creates == [source.external_id]
    assert gateway.object_updates == []


def test_content_change_updates_the_existing_stable_object() -> None:
    timestamps = iter((100, 200))
    gateway = FakeSekaiGateway()
    repositories = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: next(timestamps))
    proposal = ProposalRecord(
        stable_id="proposal-abc123",
        source_external_id="hibiki.source:hibiki:example/tenkai@abc123",
        evidence_hash=sha256_text("bounded evidence"),
        draft="Initial draft",
    )

    repositories.proposals.put(proposal)
    before = next(iter(gateway.objects.values()))
    repositories.proposals.put(proposal.with_status("approved"))
    after = next(iter(gateway.objects.values()))

    assert after.id == before.id
    assert after.created == before.created == 100
    assert after.updated == 200
    assert gateway.object_updates == [proposal.external_id]


def test_namespace_is_part_of_external_and_object_identity() -> None:
    gateway = FakeSekaiGateway()
    default = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: 100)
    sandbox = CausalRepositories.create(gateway, "sandbox", clock_ms=lambda: 100)
    values = {
        "stable_id": "example/tenkai@abc123",
        "repository": "example/tenkai",
        "revision": "abc123",
        "public_url": "https://github.com/example/tenkai/commit/abc123",
        "evidence_hash": sha256_text("bounded evidence"),
    }

    default_record = default.sources.put(SourceRecord(**values))
    sandbox_record = sandbox.sources.put(SourceRecord(namespace="sandbox", **values))

    assert default_record.external_id != sandbox_record.external_id
    assert len(gateway.objects) == 2
    assert len(set(gateway.objects)) == 2


def test_ambiguous_committed_create_is_reconciled_as_a_retry() -> None:
    class CommittedWriteError(grpc.RpcError):
        def code(self) -> grpc.StatusCode:
            return grpc.StatusCode.UNAVAILABLE

    class AmbiguousCreateGateway(FakeSekaiGateway):
        def create_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
            super().create_object(object_)
            raise CommittedWriteError()

    gateway = AmbiguousCreateGateway()
    repositories = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: 123)
    source = SourceRecord(
        stable_id="example/tenkai@abc123",
        repository="example/tenkai",
        revision="abc123",
        public_url="https://github.com/example/tenkai/commit/abc123",
        evidence_hash=sha256_text("bounded evidence"),
    )

    assert repositories.sources.put(source) == source
    assert gateway.object_creates == [source.external_id]
    assert gateway.object_updates == []
