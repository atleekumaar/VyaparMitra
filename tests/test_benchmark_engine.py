"""
Unit tests for Merchant Peer Benchmarking Engine.
"""

import pytest
from src.analytics.benchmark import BenchmarkEngine, get_benchmark_engine


@pytest.fixture
def engine():
    return BenchmarkEngine()


def test_benchmark_compute_all(engine):
    benchmarks = engine.compute_all_benchmarks()
    assert len(benchmarks) >= 50
    assert "M015" in benchmarks
    assert "M001" in benchmarks


def test_benchmark_metrics_structure(engine):
    b = engine.get_benchmark("M015")
    assert b is not None
    assert b["merchant_id"] == "M015"
    assert b["business_type"] == "Bakery"
    assert 1 <= b["rank"] <= b["peer_count"]
    assert 10 <= b["overall_score"] <= 100
    assert len(b["metrics"]) == 6

    expected_metrics = {
        "repeat_rate",
        "ticket_size",
        "failure_rate",
        "refund_rate",
        "upi_share",
        "monthly_growth",
    }
    metric_names = {m["name"] for m in b["metrics"]}
    assert expected_metrics == metric_names

    for m in b["metrics"]:
        assert 0 <= m["percentile"] <= 100
        assert m["status"] in ("green", "yellow", "red")
        assert len(m["action"]) > 0
        assert m["peer_min"] <= m["peer_median"] <= m["peer_max"]


def test_benchmark_fallback_resolution(engine):
    # M015 is Bakery in Noida. City has only 1 bakery.
    b = engine.get_benchmark("M015")
    assert b["is_fallback_group"] is True
    assert b["fallback_reason"] is not None
    assert b["peer_count"] >= 5


def test_benchmark_whatsapp_digest(engine):
    b = engine.get_benchmark("M015")
    assert b["whatsapp_digest"] is not None
    assert "VyaparMitra Peer Benchmark" in b["whatsapp_digest"]
    assert f"#{b['rank']}" in b["whatsapp_digest"]
    assert f"{b['peer_count']}" in b["whatsapp_digest"]


def test_benchmark_save_and_retrieve(engine, tmp_path):
    temp_engine = BenchmarkEngine(output_dir=str(tmp_path))
    saved_path = temp_engine.save_benchmarks()
    assert saved_path.exists()

    retrieved = temp_engine.get_benchmark("M001")
    assert retrieved is not None
    assert retrieved["merchant_id"] == "M001"
