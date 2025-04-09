"""
Util functions for the metrics service:
    - calculate_working_time: Get the time to work a field in seconds.
    - calculate_fertilizer_usage_by_time: calculate the time to fertilize a field by working time.
"""

from src.api.constants import FertilizerTypes, FSData, FertilizerStates, FertilizerEffect, SoilTypes


def calculate_fertilizer_kg(rate: int, field_size: float) -> float:
    """
    Calculate the fertilizer usage in KG
    :param rate: the rate of fertilizer in kg/ha to apply
    :param field_size: the size of the field
    :return: the fertilizer usage in kg.
    """
    return rate * field_size


def calculate_working_time(size: float, implement_width: float, working_speed: float) -> float:
    """
    Calculates the time (in seconds) taken to work a field with a working speed and
    implement width.
    :param size: the size of the field.
    :param implement_width: the size of the implement in meters
    :param working_speed: the working speed of the vehicle in km/ph
    :return: (float) of the time taken to work the field in seconds.
    """
    # Convert hectares to square meters
    field_area = size * 10_000
    # Convert km/h to m/s
    speed_meters_per_s = (working_speed * 1000) / 3600
    # Calculate the coverage
    coverage_rate = implement_width * speed_meters_per_s
    time_seconds = field_area / coverage_rate
    return time_seconds


def calculate_fertilizer_usage_by_time(
    field_size: float,
    fertilizer_type: FertilizerTypes,
    working_speed: float = 24,
    implement_width: float = 36,
) -> float:
    """
    Calculate fertilizer usage in litres by work time.
    :param field_size: the size of the field.
    :param implement_width: the size of the implement in meters
    :param working_speed: the working speed of the vehicle in km/ph
    :param fertilizer_type: the type of fertilizer to get the usage for.
    :return: (float) of the time taken to work the field in seconds.
    """
    rates = {
        FertilizerTypes.SOLID: FSData.SOLID_FERTILIZER_RATE.value,
        FertilizerTypes.LIQUID: FSData.LIQUID_FERTILIZER_RATE.value,
        FertilizerTypes.MANURE: FSData.MANURE_RATE.value,
        FertilizerTypes.SLURRY: FSData.LIQUID_MANURE_RATE.value,
        FertilizerTypes.DIGESTATE: FSData.DIGESTATE_RATE.value,
    }

    if fertilizer_type not in FertilizerTypes:
        raise ValueError(
            f"Invalid fertilizer type. Expected: {[fertilizer_type for fertilizer_type in FertilizerTypes]}"
        )

    time_seconds = calculate_working_time(
        size=field_size,
        working_speed=working_speed,
        implement_width=implement_width
    )

    fertilizer_usage = (rates[fertilizer_type] * time_seconds) * 1000
    return fertilizer_usage


def get_fertilizer_effect(state: FertilizerStates) -> float:
    """
    Util to get the fertilizer effect (0%, 22.5% and 45%) from the fertilizer
    percentage.
    :param state: the fertilizer state in the base game field
    :return: (float) the fertilizer effect value.
    """
    mapping = {
        FertilizerStates.ZER0_PERCENT.name: FertilizerEffect.NOT_FERTILIZED.value,
        FertilizerStates.FIFTY_PERCENT.name: FertilizerEffect.HALF_FERTILIZED.value,
        FertilizerStates.ONE_HUNDRED_PERCENT.name: FertilizerEffect.FULLY_FERTILIZED.value,
    }

    return mapping.get(state, 0.0)


def get_soil_type_expected_ph(soil_type: SoilTypes) -> list:
    """
    get the expected ph level thresholds by its soil type.
    :param soil_type: the fields soil type
    :return: list of expected pH levels.
    """
    expected_ph_levels = {
        SoilTypes.LOAM: FSData.LOAM_PH_LEVELS.value,
        SoilTypes.SANDY_LOAM: FSData.SANDY_LOAM_PH_LEVELS.value,
        SoilTypes.LOAMY_SAND: FSData.LOAMY_SAND_PH_LEVELS.value,
        SoilTypes.SILTY_CLAY: FSData.SILTY_CLAY_PH_LEVELS.value,
    }

    return expected_ph_levels.get(soil_type, [])
