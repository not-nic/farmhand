"""
TODO: Field Metrics API.
"""
from typing import Optional

from fastapi import APIRouter

from src.api.constants import FertilizerTypes
from src.api.core.dependencies import CurrentField
from src.api.core.schema.fields.metrics import (
    MetricsResponseModel,
    SeedUsageModel,
    PotentialYieldModel,
    FertilizerUsageModel
)

from src.api.services.metrics import MetricService

router = APIRouter(prefix="/{field_id}/metrics", tags=["Field Metrics"])


@router.get("")
async def get_metrics(field: CurrentField, next_crop: Optional[str] = None) -> MetricsResponseModel:
    """
    TODO: Get endpoint for getting the metrics about a field such as
    profit, costs and other information.
    :return: Pydantic model showing profit, costs and other information.
    """
    metric_service = MetricService()

    fertilizer_usage = await metric_service.calculate_fertilizer_usage(field)
    fertilizer_costs = metric_service.calculate_fertilizer_cost(fertilizer_usage, FertilizerTypes.SOLID)

    seed_usage = await metric_service.calculate_seed_usage(field, next_crop)
    seed_costs = metric_service.estimate_seed_costs(seed_usage)

    potential_yield = await metric_service.calculate_yield(current_field=field, future_crop=next_crop)
    potential_profit = await metric_service.estimate_profit(current_field=field, estimated_yield=potential_yield, future_crop=next_crop)

    return MetricsResponseModel(
        estimated_seed_usage=SeedUsageModel(seed_usage=seed_usage, seed_costs=seed_costs),
        estimated_yield=PotentialYieldModel(potential_yield=potential_yield, potential_profit=potential_profit),
        estimated_fertilizer_usage=FertilizerUsageModel(fertilizer_usage=fertilizer_usage, fertilize_costs=fertilizer_costs)
    )
