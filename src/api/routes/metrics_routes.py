"""
TODO: Field Metrics API.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/{field_id}/metrics", tags=["Field Metrics"])


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
