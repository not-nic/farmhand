"""
Pydantic schema for field metrics
"""

from pydantic import BaseModel


class PotentialYieldModel(BaseModel):
    """
    Pydantic model for the potential yield and profit for
    the crop growing in the field.
    """

    potential_yield: float
    potential_profit: float


class SeedUsageModel(BaseModel):
    """
    Pydantic model for the estimated seed usage and
    costs for planting a crop in a field.
    """

    seed_usage: float
    seed_costs: float


class FertilizerUsageModel(BaseModel):
    """
    Pydantic model for the estimated fertilizer usage
    and costs for fertilizing a field.
    """

    fertilizer_usage: float
    fertilize_costs: float


class MetricsResponseModel(BaseModel):
    """
    Pydantic model to create the metrics response
    """

    estimated_yield: PotentialYieldModel
    estimated_seed_usage: SeedUsageModel
    estimated_fertilizer_usage: FertilizerUsageModel
