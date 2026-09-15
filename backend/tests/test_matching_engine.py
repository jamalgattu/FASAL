from datetime import date, timedelta

from app.models.enums import QualityGrade
from app.services import matching_engine
from app.services.matching_engine import MatchWeights
from tests.conftest import make_farmer, make_buyer, make_crop, make_listing, make_requirement


def test_crop_mismatch_is_excluded(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    potato = make_crop(db_session, "Potato")
    wheat = make_crop(db_session, "Wheat")

    make_listing(db_session, farmer, wheat, quantity=1000)
    requirement = make_requirement(db_session, buyer, potato, quantity=500)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert candidates == []


def test_quality_below_requirement_is_excluded(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    make_listing(db_session, farmer, crop, grade=QualityGrade.C)
    requirement = make_requirement(db_session, buyer, crop, required_grade=QualityGrade.A)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert candidates == []


def test_quality_at_or_above_requirement_is_included(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    make_listing(db_session, farmer, crop, grade=QualityGrade.A)
    requirement = make_requirement(db_session, buyer, crop, required_grade=QualityGrade.B)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert len(candidates) == 1
    # Exceeding the requirement scores slightly below an exact match, but is
    # still a valid candidate.
    assert 0.8 <= candidates[0].factors.quality_score < 1.0


def test_listing_not_available_in_time_is_excluded(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    make_listing(db_session, farmer, crop, available_in_days=20)
    requirement = make_requirement(db_session, buyer, crop, required_in_days=5)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert candidates == []


def test_price_at_or_below_acceptable_scores_perfectly(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    make_listing(db_session, farmer, crop, price=15)
    requirement = make_requirement(db_session, buyer, crop, acceptable_price=20)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert candidates[0].factors.price_score == 1.0


def test_price_above_acceptable_is_penalized_but_not_excluded(db_session):
    farmer = make_farmer(db_session)
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    make_listing(db_session, farmer, crop, price=30)  # 50% over the acceptable price
    requirement = make_requirement(db_session, buyer, crop, acceptable_price=20)

    candidates = matching_engine.find_candidates(db_session, requirement)
    assert len(candidates) == 1
    assert 0.0 <= candidates[0].factors.price_score < 1.0


def test_closer_supplier_scores_higher_on_distance(db_session):
    buyer = make_buyer(db_session, lat=26.85, lng=80.95)
    crop = make_crop(db_session)

    near_farmer = make_farmer(db_session, lat=26.90, lng=80.96)  # ~5km away
    far_farmer = make_farmer(db_session, lat=30.00, lng=79.00)  # far away

    make_listing(db_session, near_farmer, crop, price=15)
    make_listing(db_session, far_farmer, crop, price=15)
    requirement = make_requirement(db_session, buyer, crop, acceptable_price=20)

    candidates = matching_engine.find_candidates(db_session, requirement)
    by_distance = sorted(candidates, key=lambda c: c.distance_km)
    assert by_distance[0].factors.distance_score > by_distance[-1].factors.distance_score


def test_does_not_simply_pick_the_cheapest_supplier(db_session):
    """A pricier-but-closer, higher-quality supplier should be able to
    out-rank a cheap-but-distant, minimum-quality one."""
    buyer = make_buyer(db_session, lat=26.85, lng=80.95)
    crop = make_crop(db_session)

    cheap_far_farmer = make_farmer(db_session, lat=31.0, lng=77.0)  # very far
    pricier_near_farmer = make_farmer(db_session, lat=26.86, lng=80.96)  # very close

    make_listing(db_session, cheap_far_farmer, crop, price=10, grade=QualityGrade.B)
    make_listing(db_session, pricier_near_farmer, crop, price=19, grade=QualityGrade.A)

    requirement = make_requirement(db_session, buyer, crop, acceptable_price=20, required_grade=QualityGrade.B)

    candidates = matching_engine.find_candidates(db_session, requirement)
    top = candidates[0]
    assert top.listing.farmer_id == pricier_near_farmer.id, (
        "Expected the closer, higher-quality supplier to win despite being more expensive"
    )


def test_weights_are_configurable_and_change_ranking(db_session):
    buyer = make_buyer(db_session, lat=26.85, lng=80.95)
    crop = make_crop(db_session)

    cheap_far_farmer = make_farmer(db_session, lat=31.0, lng=77.0)
    pricier_near_farmer = make_farmer(db_session, lat=26.86, lng=80.96)

    make_listing(db_session, cheap_far_farmer, crop, price=10, grade=QualityGrade.B)
    make_listing(db_session, pricier_near_farmer, crop, price=19, grade=QualityGrade.A)

    requirement = make_requirement(db_session, buyer, crop, acceptable_price=20, required_grade=QualityGrade.B)

    # Weight price extremely heavily, distance/quality barely at all.
    price_heavy_weights = MatchWeights(price=0.9, distance=0.025, quality=0.025, availability=0.025, reliability=0.025)
    candidates = matching_engine.find_candidates(db_session, requirement, weights=price_heavy_weights)
    assert candidates[0].listing.farmer_id == cheap_far_farmer.id


def test_weights_are_normalized_when_they_dont_sum_to_one():
    weights = MatchWeights(price=1, distance=1, quality=1, availability=1, reliability=1)
    normalized = weights.normalized()
    total = (
        normalized.price + normalized.distance + normalized.quality + normalized.availability + normalized.reliability
    )
    assert abs(total - 1.0) < 1e-9
    assert abs(normalized.price - 0.2) < 1e-9


def test_allocation_splits_demand_across_multiple_suppliers(db_session):
    """Mirrors the spec's example: 2000kg demand split across three
    suppliers of 500kg / 800kg / 700kg."""
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)

    farmer_a = make_farmer(db_session)
    farmer_b = make_farmer(db_session)
    farmer_c = make_farmer(db_session)

    make_listing(db_session, farmer_a, crop, quantity=500, price=15)
    make_listing(db_session, farmer_b, crop, quantity=800, price=15)
    make_listing(db_session, farmer_c, crop, quantity=700, price=15)

    requirement = make_requirement(db_session, buyer, crop, quantity=2000, acceptable_price=20)

    result = matching_engine.allocate_supply(db_session, requirement)

    assert result.fully_allocated is True
    assert len(result.allocations) == 3
    assert sum(a.allocated_quantity for a in result.allocations) == 2000


def test_allocation_reports_partial_fulfillment_when_supply_is_short(db_session):
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)
    farmer = make_farmer(db_session)

    make_listing(db_session, farmer, crop, quantity=300, price=15)
    requirement = make_requirement(db_session, buyer, crop, quantity=2000, acceptable_price=20)

    result = matching_engine.allocate_supply(db_session, requirement)

    assert result.fully_allocated is False
    assert result.requirement_remaining_quantity == 1700
    assert len(result.allocations) == 1
    assert result.allocations[0].allocated_quantity == 300


def test_allocation_prioritizes_highest_scoring_suppliers_first(db_session):
    buyer = make_buyer(db_session, lat=26.85, lng=80.95)
    crop = make_crop(db_session)

    best_farmer = make_farmer(db_session, lat=26.86, lng=80.96)  # close, cheap
    worst_farmer = make_farmer(db_session, lat=31.0, lng=77.0)  # far, expensive

    make_listing(db_session, best_farmer, crop, quantity=100, price=12)
    make_listing(db_session, worst_farmer, crop, quantity=2000, price=19.9)

    requirement = make_requirement(db_session, buyer, crop, quantity=150, acceptable_price=20)

    result = matching_engine.allocate_supply(db_session, requirement)

    # The 100kg from the best-scoring farmer should be fully used before
    # dipping into the worse-scoring one for the remaining 50kg.
    assert result.allocations[0].listing.farmer_id == best_farmer.id
    assert result.allocations[0].allocated_quantity == 100
    assert result.allocations[1].listing.farmer_id == worst_farmer.id
    assert result.allocations[1].allocated_quantity == 50


def test_each_allocation_includes_score_factors_and_explanation(db_session):
    buyer = make_buyer(db_session)
    crop = make_crop(db_session)
    farmer = make_farmer(db_session)
    make_listing(db_session, farmer, crop, quantity=500, price=15)
    requirement = make_requirement(db_session, buyer, crop, quantity=200, acceptable_price=20)

    result = matching_engine.allocate_supply(db_session, requirement)
    allocation = result.allocations[0]

    assert allocation.match_score > 0
    assert 0 <= allocation.factors.price_score <= 1
    assert 0 <= allocation.factors.distance_score <= 1
    assert 0 <= allocation.factors.quality_score <= 1
    assert 0 <= allocation.factors.availability_score <= 1
    assert 0 <= allocation.factors.reliability_score <= 1
    assert isinstance(allocation.explanation, str) and len(allocation.explanation) > 0
    assert len(allocation.reasons) > 0
