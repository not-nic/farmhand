"""
TODO: Field Metrics API.
"""
from typing import Optional

from fastapi import APIRouter

from src.api.core.dependencies import CurrentField
from src.api.core.schema.fields.metrics import MetricsResponseModel, SeedUsageModel, PotentialYieldModel, \
    FertilizerUsageModel
from src.api.services.crop_service import CropService

router = APIRouter(prefix="/{field_id}/metrics", tags=["Field Metrics"])
crop_service = CropService()


@router.get("")
async def get_metrics(field: CurrentField, next_crop: Optional[str] = None) -> MetricsResponseModel:
    """
    TODO: Get endpoint for getting the metrics about a field such as
    profit, costs and other information.
    :return: Pydantic model showing profit, costs and other information.
    """
    yield_model = PotentialYieldModel(potential_yield=0, potential_profit=0)
    fertilizer_model = FertilizerUsageModel(fertilizer_usage=0, fertilize_costs=0)

    seed_usage = await crop_service.estimate_seed_usage(field, next_crop)
    seed_costs = crop_service.estimate_seed_costs(seed_usage)

    return MetricsResponseModel(
        estimated_seed_usage=SeedUsageModel(seed_usage=seed_usage, seed_costs=seed_costs),
        estimated_yield=yield_model,
        estimated_fertilizer_usage=fertilizer_model
    )


async def potential_yield_and_profit():
    """
    TODO:
    :return:
    """
    # Profit calculation:
    # - Get the required farm stats: Difficulty
    # - Get the current field crop stats: type -> price_per_litre
    # - Get the total yield calculation (as an argument)
    # - Profit = (price_per_litre * total_yield) * (difficulty_bonus)
    # Yield calculation:
    # - Get the required stats from the field crop: type -> yield_per_ha
    # - Get the required field stats: size, fertilized / nitrogen_level, pH / limed, weed, plowing, mulching, rolling.

    # - if field has a nitrogen level:
    #       calculate bonus as a percentage compared to the correct nitrogen level for the crop
    #       then apply this to the yield.
    # - else:
    #       apply bonuses separately based on fert.

    # - apply all over bonuses, weeded, plowed, mulching etc.
    # - yield_per_ha: (base_yield_per_ha * all bonuses)
    # - total yield: (yield_per_ha * field size)
    pass


async def seeding_usage_and_costs():
    """
    TODO:
    :return:
    """
    # Seed Cost Calculation:
    # - Get the required field stats: size
    # - Get the current field crop stats: type -> seeds_per_ha
    # - Total Seed Usage: (seeds_per_ha * size)
    # - Seed Costs: (get price of seeds / 1000 (to get price of individual seed) * total seed usage
