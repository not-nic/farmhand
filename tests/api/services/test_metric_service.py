"""
Metrics Service Unit Tests.
"""

import pytest

from src.api.constants import Difficulty, FertilizerTypes, FSData
from src.api.core.db.models import FieldCrop
from src.api.core.repositories import CropRepository, FieldCropRepository
from src.api.services.metrics import MetricService
from src.api.services.metrics.utils import (
    calculate_fertilizer_kg,
    calculate_fertilizer_usage_by_time,
)


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "unit_test_user", "mock_crop_data")
class TestMetricService:
    @pytest.fixture
    def valid_crop(self, db, base_game_field, precision_farming_field) -> None:
        """Fixture of a normal valid crop."""
        field_crop_repository = FieldCropRepository(db)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=1)
        field_crop_repository.create(field_id=precision_farming_field.id, crop_id=1)

    @pytest.fixture
    def edge_case_crop(self, db, base_game_field, precision_farming_field) -> None:
        """Fixture of an edge case crop (one with 0 nitrogen)."""

        field_crop_repository = FieldCropRepository(db)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=4)
        field_crop_repository.create(field_id=precision_farming_field.id, crop_id=4)

    @pytest.fixture
    def invalid_crop(self, db, base_game_field, precision_farming_field) -> None:
        """Fixture of a crop that doesn't exist."""

        field_crop_repository = FieldCropRepository(db)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=50)
        field_crop_repository.create(field_id=precision_farming_field.id, crop_id=50)

    async def test_calculate_yield_on_base_field_type(self, db, base_game_field, valid_crop):
        """
        Test that yield can be calculated on a base game field and
        return the expected results by getting the yield_improvement_score
        from the field fixture.
        :param base_game_field: base game field fixture.
        """

        metrics_service = MetricService(db)
        actual_yield = await metrics_service.calculate_yield(base_game_field)

        # magic number for tests instead of calculating yield again
        yield_improvement_value = 17800.0
        expected_yield = base_game_field.size * yield_improvement_value

        assert actual_yield == expected_yield

    async def test_calculate_yield_on_precision_farming_field_type(
        self, db, precision_farming_field, valid_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return the expected results by getting the yield_improvement_score
        from the field fixture.
        :param precision_farming_field: field fixture
        """

        metrics_service = MetricService(db)
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        # magic number for tests instead of calculating yield again
        yield_improvement_value = 17800.0
        expected_yield = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield

    async def test_calculate_yield_on_precision_farming_field_with_edge_case_crop(
        self, db, precision_farming_field, edge_case_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return 0 for edge case crops.
        from the field fixture.
        :param precision_farming_field: field fixture
        :param edge_case_crop: edge case crop fixture
        """

        metrics_service = MetricService(db)
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        assert actual_yield == 0

    async def test_calculate_yield_on_precision_farming_field_with_excess_nitrogen(
        self, db, precision_farming_field, valid_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return the correct yield for excess nitrogen
        from the field fixture.
        :param precision_farming_field: field fixture
        :param valid_crop: valid crop fixture
        """
        precision_farming_field.precision_farming_field.nitrogen_level = 250
        metrics_service = MetricService(db)
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        # magic number for tests instead of calculating yield again
        yield_improvement_value = 16999.0
        expected_yield = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield

    @pytest.mark.parametrize(
        "ph_level, expected_yield",
        [
            (9.0, 16465.0),
            (0.0, 16465.0),
        ],
    )
    async def test_calculate_yield_on_precision_farming_field_with_different_ph_levels(
        self, db, precision_farming_field, valid_crop, ph_level: float, expected_yield: float
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return the correct yield for various pH levels (both excess and reduced).
        :param precision_farming_field: field fixture
        :param valid_crop: valid crop fixture
        :param ph_level: pH level to test with
        :param expected_yield: the expected yield for the given pH level
        """

        precision_farming_field.precision_farming_field.ph_level = ph_level
        metrics_service = MetricService(db)
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        yield_improvement_value = 16465.0
        expected_yield_calculated = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield_calculated

    @pytest.mark.parametrize(
        "difficulty, expected_multiplier",
        [
            (Difficulty.EASY, Difficulty.EASY.multiplier),
            (Difficulty.MEDIUM, Difficulty.MEDIUM.multiplier),
            (Difficulty.HARD, Difficulty.HARD.multiplier),
        ],
    )
    async def test_estimate_profit_with_difficulties(
        self, db, farm, base_game_field, valid_crop, difficulty, expected_multiplier
    ):
        """
        Test estimating the profit for a field with farm difficulty levels.
        :param farm: the farm object
        :param base_game_field: base game field fixture.
        :param valid_crop: fixture to create a valid crop
        :param difficulty: the difficulty level for the test
        :param expected_multiplier: the expected multiplier based on difficulty
        """

        farm.difficulty = difficulty

        metrics_service = MetricService(db)
        field_yield = await metrics_service.calculate_yield(base_game_field)
        actual_profit = await metrics_service.estimate_profit(base_game_field, field_yield)
        current_crop: FieldCrop = base_game_field.current_crop()

        expected_profit = (field_yield * current_crop.crop.price) * expected_multiplier

        assert actual_profit == expected_profit

    async def test_calculate_seed_usage(self, db, base_game_field, valid_crop):
        """
        Test that when the seed usage is calculated for a field
        and its crop the correct value is returned.
        :param base_game_field: base game field fixture.
        :param valid_crop: valid crop fixture.
        """

        metrics_service = MetricService(db)
        crop_repository = CropRepository(db)

        result = await metrics_service.calculate_seed_usage(base_game_field)
        expected_seed_usage = crop_repository.get_by_id(1).seeds_per_ha * base_game_field.size

        assert result == expected_seed_usage

    async def test_calculate_seed_usage_for_future_crop(self, db, base_game_field, valid_crop):
        """
        Test that when the seed usage is calculated for a field
        and a future crop the correct result is returned.
        :param base_game_field: base game field fixture.
        :param valid_crop: valid crop fixture.
        """

        metrics_service = MetricService(db)
        crop_repository = CropRepository(db)

        future_crop = crop_repository.get_by_type("Maize")
        result = await metrics_service.calculate_seed_usage(
            base_game_field, future_crop=future_crop.type
        )
        expected_seed_usage = future_crop.seeds_per_ha * base_game_field.size

        assert result == expected_seed_usage
        assert base_game_field.current_crop().crop_id != future_crop.id

    async def test_calculate_seed_usage_with_invalid_crop(self, db, base_game_field, invalid_crop):
        """
        test that when calculating the seed usage with an invalid crop
        a ValueError is raised.
        :param base_game_field: base game field fixture.
        :param invalid_crop: invalid crop fixture.
        """
        metrics_service = MetricService(db)

        with pytest.raises(
            ValueError, match=f"Invalid crop: '{base_game_field.current_crop().crop_id}' not found"
        ):
            await metrics_service.calculate_seed_usage(base_game_field)

    async def test_estimate_seed_costs(self, db, base_game_field, valid_crop):
        """
        test that the seed costs are correctly calculated.
        :param base_game_field: base game field fixture.
        :param valid_crop: valid crop fixture.
        """

        metrics_service = MetricService(db)
        usage = await metrics_service.calculate_seed_usage(base_game_field)

        result = metrics_service.estimate_seed_costs(usage)
        expected_result = usage * FSData.BASE_SEED_PRICE.value

        assert result == expected_result

    async def test_calculate_base_game_fertilizer_usage(self, db, base_game_field):
        """
        Test calculating the fertilizer usage on a base game field,
        by calculating the size of the fixture's field against the
        base 'SOLID' fertilizer type.
        :param base_game_field: base game field fixture.
        """

        metrics_service = MetricService(db)
        result = await metrics_service.calculate_fertilizer_usage(base_game_field)
        expected_result = calculate_fertilizer_usage_by_time(
            field_size=base_game_field.size,
            fertilizer_type=FertilizerTypes.SOLID,
        )

        assert result == expected_result

    async def test_calculate_precision_farming_field_fertilizer_usage(
        self, db, precision_farming_field
    ):
        """
        Test calculating the fertilizer usage on a precision farming field,
        by calculating against the fields nitrogen level.
        :param precision_farming_field: the field fixture.
        """

        precision_farming_field.precision_farming_field.nitrogen_level = 10

        metrics_service = MetricService(db)
        result = await metrics_service.calculate_fertilizer_usage(precision_farming_field)

        expected_result = (
            calculate_fertilizer_kg(
                rate=precision_farming_field.precision_farming_field.nitrogen_level,
                field_size=precision_farming_field.size,
            )
            / FSData.SOLID_FERTILIZER_DENSITY.value
        )

        assert result == expected_result

    async def test_calculate_fertilizer_cost(self, db, base_game_field):
        """
        Test that when calculating the cost to fertilize a field
        it matches the calculation of 'fertilzer' * BASE_FERTILIZER PRICE (1.92)
        :param base_game_field: base game field fixture.
        """

        metrics_service = MetricService(db)
        fertilizer = await metrics_service.calculate_fertilizer_usage(base_game_field)

        result = metrics_service.calculate_fertilizer_cost(
            fertilizer_usage=fertilizer, fertilizer_type=FertilizerTypes.SOLID
        )

        assert result == fertilizer * FSData.BASE_SOLID_FERTILIZER_PRICE.value

    async def test_fertilizer_usage_by_time_with_invalid_fertilizer_type(self, base_game_field):
        """
        Test calculating the fertilizer usage with an invalid fertilizer type.
        :param base_game_field: the field fixture.
        """

        with pytest.raises(ValueError, match="Invalid fertilizer type. Expected: "):
            calculate_fertilizer_usage_by_time(
                field_size=base_game_field.size,
                fertilizer_type="invalid-type",
            )
