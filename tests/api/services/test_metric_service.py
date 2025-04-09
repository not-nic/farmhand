"""
Metrics Service Unit Tests.
"""

import pytest

from src.api.constants import FSData, Difficulty, FertilizerTypes
from src.api.core.db.models import Field, FieldCrop, Crop, Farm
from src.api.services.metrics import MetricService
from src.api.services.metrics.utils import calculate_fertilizer_usage_by_time, calculate_fertilizer_kg


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_database", "unit_test_user", "mock_crop_data")
class TestMetricService:

    @pytest.fixture
    def farm(self, farms):
        """
        Single farm fixture
        :param farms: farms fixture.
        """
        return farms[0]

    @pytest.fixture
    def field(self, fields) -> Field:
        """
        Single field fixture
        :param fields: fields fixture.
        """
        base_fields, _ = fields
        return Field.get(base_fields[0].id)

    @pytest.fixture
    def precision_farming_field(self, fields) -> Field:
        """
        Single precision_farming field fixture
        :param fields: fields fixture.
        """
        _, precision_farming_fields = fields
        return Field.get(precision_farming_fields[0].id)

    @pytest.fixture
    def valid_crop(self, field, precision_farming_field) -> None:
        """
        Create a valid field crop
        """
        FieldCrop.create(field_id=field.id, crop_id=1)
        FieldCrop.create(field_id=precision_farming_field.id, crop_id=1)

    @pytest.fixture
    def edge_case_crop(self, field, precision_farming_field) -> None:
        """
        Create a valid field crop
        """
        FieldCrop.create(field_id=field.id, crop_id=4)
        FieldCrop.create(field_id=precision_farming_field.id, crop_id=4)

    @pytest.fixture
    def invalid_crop(self, field, precision_farming_field) -> None:
        """
        Create an invalid field crop
        """
        FieldCrop.create(field_id=field.id, crop_id=50)
        FieldCrop.create(field_id=precision_farming_field.id, crop_id=50)

    async def test_calculate_yield_on_base_field_type(
            self,
            field: Field,
            valid_crop
    ):
        """
        Test that yield can be calculated on a base game field and
        return the expected results by getting the yield_improvement_score
        from the field fixture.
        :param field: field fixture
        """
        metrics_service = MetricService()
        actual_yield = await metrics_service.calculate_yield(field)

        yield_improvement_value = 17800.0  # magic number for tests instead of calculating yield again
        expected_yield = field.size * yield_improvement_value

        assert actual_yield == expected_yield

    async def test_calculate_yield_on_precision_farming_field_type(
            self,
            precision_farming_field: Field,
            valid_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return the expected results by getting the yield_improvement_score
        from the field fixture.
        :param precision_farming_field: field fixture
        """
        metrics_service = MetricService()
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        yield_improvement_value = 17800.0  # magic number for tests instead of calculating yield again
        expected_yield = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield

    async def test_calculate_yield_on_precision_farming_field_with_edge_case_crop(
            self,
            precision_farming_field: Field,
            edge_case_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return 0 for edge case crops.
        from the field fixture.
        :param precision_farming_field: field fixture
        :param edge_case_crop: edge case crop fixture
        """
        metrics_service = MetricService()
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        assert actual_yield == 0

    async def test_calculate_yield_on_precision_farming_field_with_excess_nitrogen(
            self,
            precision_farming_field: Field,
            valid_crop
    ):
        """
        Test that yield can be calculated on a precision farming field and
        return the correct yield for excess nitrogen
        from the field fixture.
        :param precision_farming_field: field fixture
        :param valid_crop: valid crop fixture
        """
        precision_farming_field.precision_farming_field.nitrogen_level = 250
        metrics_service = MetricService()
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        yield_improvement_value = 16999.0  # magic number for tests instead of calculating yield again
        expected_yield = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield

    @pytest.mark.parametrize("ph_level, expected_yield", [
        (9.0, 16465.0),
        (0.0, 16465.0),
    ])
    async def test_calculate_yield_on_precision_farming_field_with_different_ph_levels(
            self,
            precision_farming_field: Field,
            valid_crop,
            ph_level: float,
            expected_yield: float
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
        metrics_service = MetricService()
        actual_yield = await metrics_service.calculate_yield(precision_farming_field)

        yield_improvement_value = 16465.0
        expected_yield_calculated = precision_farming_field.size * yield_improvement_value

        assert actual_yield == expected_yield_calculated

    @pytest.mark.parametrize("difficulty, expected_multiplier", [
        (Difficulty.EASY, Difficulty.EASY.value),
        (Difficulty.MEDIUM, Difficulty.MEDIUM.value),
        (Difficulty.HARD, Difficulty.HARD.value)
    ])
    async def test_estimate_profit_with_difficulties(
            self,
            farm: Farm,
            field: Field,
            valid_crop,
            difficulty: Difficulty,
            expected_multiplier: float
    ):
        """
        Test estimating the profit for a field with farm difficulty levels.
        :param farm: the farm object
        :param field: the field object
        :param valid_crop: fixture to create a valid crop
        :param difficulty: the difficulty level for the test
        :param expected_multiplier: the expected multiplier based on difficulty
        """
        farm.difficulty = difficulty

        metrics_service = MetricService()
        field_yield = await metrics_service.calculate_yield(field)
        actual_profit = await metrics_service.estimate_profit(field, field_yield)
        expected_profit = (field_yield * field.current_crop().crop.price) * expected_multiplier

        assert actual_profit == expected_profit

    async def test_calculate_seed_usage(self, field: Field, valid_crop):
        """
        Test that when the seed usage is calculated for a field
        and its crop the correct value is returned.
        :param field: field fixture
        :param
        """
        metrics_service = MetricService()

        result = await metrics_service.calculate_seed_usage(field)
        expected_seed_usage = Crop.get(1).seeds_per_ha * field.size

        assert result == expected_seed_usage

    async def test_calculate_seed_usage_for_future_crop(self, field: Field, valid_crop):
        """
        Test that when the seed usage is calculated for a field
        and a future crop the correct result is returned.
        :param field: field fixture
        """
        metrics_service = MetricService()

        future_crop = Crop.get_by_type("Maize")
        result = await metrics_service.calculate_seed_usage(field, future_crop=future_crop.type)
        expected_seed_usage = future_crop.seeds_per_ha * field.size

        assert result == expected_seed_usage
        assert field.current_crop().crop_id != future_crop.id

    async def test_calculate_seed_usage_with_invalid_crop(self, field: Field, invalid_crop):
        """
        test that when calculating the seed usage with an invalid crop
        a ValueError is raised.
        :param field: field fixture.
        """
        metrics_service = MetricService()

        with pytest.raises(ValueError, match=f"Invalid crop: '{field.current_crop().crop_id}' not found"):
            await metrics_service.calculate_seed_usage(field)

    async def test_estimate_seed_costs(self, field: Field, valid_crop):
        """
        test that the seed costs are correctly calculated.
        :param field: field fixture
        """
        metrics_service = MetricService()
        usage = await metrics_service.calculate_seed_usage(field)

        result = metrics_service.estimate_seed_costs(usage)
        expected_result = usage * FSData.BASE_SEED_PRICE.value

        assert result == expected_result

    async def test_calculate_base_game_fertilizer_usage(self, field: Field):
        """
        Test calculating the fertilizer usage on a base game field,
        by calculating the size of the fixture's field against the
        base 'SOLID' fertilizer type.
        :param field: the field fixture.
        """
        metrics_service = MetricService()
        result = await metrics_service.calculate_fertilizer_usage(field)
        expected_result = calculate_fertilizer_usage_by_time(
            field_size=field.size,
            fertilizer_type=FertilizerTypes.SOLID,
        )

        assert result == expected_result

    async def test_calculate_precision_farming_field_fertilizer_usage(self, precision_farming_field: Field):
        """
        Test calculating the fertilizer usage on a precision farming field,
        by calculating against the fields nitrogen level.
        :param precision_farming_field: the field fixture.
        """
        precision_farming_field.precision_farming_field.nitrogen_level = 10

        metrics_service = MetricService()
        result = await metrics_service.calculate_fertilizer_usage(precision_farming_field)

        expected_result = calculate_fertilizer_kg(
            rate=precision_farming_field.precision_farming_field.nitrogen_level,
            field_size=precision_farming_field.size,
        ) / FSData.SOLID_FERTILIZER_DENSITY.value

        assert result == expected_result

    async def test_fertilizer_usage_by_time_with_invalid_fertilizer_type(self, field: Field):
        """
        Test calculating the fertilizer usage with an invalid fertilizer type.
        :param field: the field fixture.
        """
        with pytest.raises(ValueError, match="Invalid fertilizer type. Expected: "):
            calculate_fertilizer_usage_by_time(
                field_size=field.size,
                fertilizer_type="invalid-type",
            )

