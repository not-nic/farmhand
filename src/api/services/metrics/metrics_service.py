"""
Metric Service Module for calculating and managing costs that are associated with fields and farms.
"""

from typing import Optional

from src.api.constants import FSData, FieldTypes, WeedStates, SoilTypes, FertilizerStates, FertilizerTypes
from src.api.core.db.models import Field, Crop
from src.api.core.logger import logger
from src.api.services.crop_service import CropService
from src.api.services.metrics.utils import (
    calculate_fertilizer_kg,
    calculate_fertilizer_usage_by_time
)


class MetricsService:
    """
    Metrics Service:

    This service is responsible for calculating yield, costs and other number-based stats relating
    to a farm and its fields, but could be expanded to handle other numeric values / calculations.
    """

    async def calculate_yield(self, current_field: Field, future_crop: Optional[str] = None) -> float:
        """
        Calculate the yield for a field and its current crop based on the field stats.
        :param current_field: the current field to get stats from
        :param future_crop: another crop that isn't the current field crop.
        :return: (float) of the expected yield
        """
        crop: Crop = await self.get_crop(current_field, future_crop)

        base_yield = crop.yield_per_ha
        expected_yield_per_ha = base_yield + self._calculate_base_yield_increases(base_yield, current_field)

        if current_field.field_type == FieldTypes.BASE_FIELD:
            expected_yield_per_ha += self._calculate_base_game_fertilization(
                base_yield=base_yield,
                fertilized_value=current_field.base_game_field.fertilized.value,
                limed=current_field.base_game_field.limed
            )
        elif current_field.field_type == FieldTypes.PRECISION_FARMING_FIELD:
            expected_yield_per_ha += self._calculate_precision_farming_fertilization(
                base_yield=base_yield,
                nitrogen_level=current_field.precision_farming_field.nitrogen_level,
                ph_level=current_field.precision_farming_field.ph_level,
                soil_type=current_field.precision_farming_field.soil_type,
                crop=crop
            )
        else:
            raise NotImplemented("Field Type not implemented.")

        logger.info(f"Base Yield Per Ha: {base_yield} for Crop: {crop.type}")
        logger.info(f"Improved Yield Per Ha: {expected_yield_per_ha} for Crop: {crop.type}")
        return current_field.size * expected_yield_per_ha

    async def estimate_profit(
        self,
        current_field: Field,
        estimated_yield: float,
        future_crop: Optional[str] = None
    ) -> float:
        """
        Estimate the profit for the crop on a field from the field size, difficulty
        and estimated yield.
        :param current_field: the current field to get the size from
        :param estimated_yield: the estimated yield of the field.
        :param future_crop: the future crop
        :return: (float) of the estimated profit, fixed to 3dp.
        """
        crop: Crop = await self.get_crop(current_field, future_crop)
        difficulty = current_field.farm.difficulty.value
        return round((estimated_yield * crop.price) * difficulty, 3)

    async def calculate_seed_usage(self, current_field: Field, future_crop: Optional[str] = None) -> float:
        """
        Estimate the amount of seeds required to plant a specific crop in a field.
        :param current_field: the current field to check the usage of.
        :param future_crop: make a calculation with the current field and a future crop.
        :return: float of the amount of seeds needed
        """
        crop = await self.get_crop(current_field, future_crop)
        return current_field.size * crop.seeds_per_ha

    @staticmethod
    def estimate_seed_costs(seed_usage: float) -> float:
        """
        Estimate the seed costs for a field by multiplying the seed usage
        by the seed price (£1.26).
        :param seed_usage: estimated seed usage in a particular feed.
        :return: (float) the cost to seed a field.
        """
        return seed_usage * FSData.BASE_SEED_PRICE.value

    @staticmethod
    async def calculate_fertilizer_usage(current_field: Field) -> float:
        """
        Calculate fertilizer usage (litres) for base game or precision farming fields.

        Base Game: Uses working speed and implement width, returns 'SOLID' fertilizer usage.
        Precision Farming: Uses 'SOLID' fertilizer density.

        Results should match if both field stats are identical.

        :param current_field: The current field.
        :return: Fertilizer usage in litres (float).
        """

        if current_field.field_type == FieldTypes.BASE_FIELD:
            return calculate_fertilizer_usage_by_time(
                field_size=current_field.size,
                fertilizer_type=FertilizerTypes.SOLID,
                working_speed=24,
                implement_width=36
            )
        elif current_field.field_type == FieldTypes.PRECISION_FARMING_FIELD:
            total_fertilizer_kg = calculate_fertilizer_kg(
                rate=current_field.precision_farming_field.nitrogen_level,
                field_size=current_field.size
            )

            return total_fertilizer_kg / FSData.SOLID_FERTILIZER_DENSITY.value
        else:
            raise NotImplemented("Field Type not implemented")

    @staticmethod
    def calculate_fertilizer_cost(
        fertilizer_usage: float,
        fertilizer_type: FertilizerTypes
    ) -> float:
        """
        Calculate the fertilizer costs for a field by multiplying the usage in litres
        by the base fertilizer price.
        :param fertilizer_usage: the amount of fertilizer
        :param fertilizer_type: the type of fertilizer to calculate against.
        :return: (float) the price of the fertilizer.
        """
        costs = {
            FertilizerTypes.SOLID: FSData.BASE_SOLID_FERTILIZER_PRICE.value,
            FertilizerTypes.LIQUID: FSData.BASE_LIQUID_FERTILIZER_PRICE.value,
        }

        # get the cost per litre by fertilizer type
        cost_per_liter = costs[fertilizer_type]
        return fertilizer_usage * cost_per_liter if cost_per_liter is not None else None

    def _calculate_base_yield_increases(self, base_yield: float, current_field: Field) -> float:
        """
        Calculates the base yield increases that both field types share such as,
        plowed, rolled, mulched, weeded.
        :param base_yield: the base yield of the crop to calculate increases against.
        :param current_field: the field to get stats from.
        :return: float of the total 'base' increases.
        """
        plowed_increase = self._calculate_bonus(base_yield, current_field.plowed, FSData.PLOWED.value)
        rolled_increase = self._calculate_bonus(base_yield, current_field.rolled, FSData.ROLLED.value)
        mulched_increase = self._calculate_bonus(base_yield, current_field.mulched, FSData.MULCHED.value)
        weeds_increase = self._calculate_bonus(
            base_yield, current_field.weeds in [WeedStates.NO_WEEDS, WeedStates.SPRAYED_WEEDS], FSData.WEEDS.value
        )
        return plowed_increase + rolled_increase + mulched_increase + weeds_increase

    def _calculate_base_game_fertilization(
        self,
        base_yield: float,
        fertilized_value: float,
        limed: bool
    ) -> float:
        """
        Calculates the yield increases for a base game field values (fertilized and limed).
        :param base_yield: the base yield of the crop.
        :param fertilized_value: the amount of fertilizer in the field
        :param limed: bool if the field is limed
        :return: (float) of the base game field increases.
        """
        fertilizer_increase = base_yield * (fertilized_value / 100)
        limed_increase = self._calculate_bonus(base_yield, limed, FSData.LIMED.value)
        return fertilizer_increase + limed_increase

    def _calculate_precision_farming_fertilization(
        self,
        base_yield: float,
        nitrogen_level: int,
        ph_level: float,
        soil_type: SoilTypes,
        crop: Crop
    ) -> float:
        """
        Calculates the yield increases for a precision farming field (nitrogen level, ph level, soil type)
        :param base_yield: the base yield of the crop.
        :param nitrogen_level: the fields nitrogen level
        :param ph_level: the fields ph level
        :param soil_type: the fields soil type
        :param crop: the crop to get its perfect nitrogen level from.
        :return: (float) of the precision farming field increases.
        """
        nitrogen_level_increase = base_yield * (self.nitrogen_level_to_percent(
            nitrogen_level,
            crop.nitrogen_per_kg_ha
        ) / 100)

        ph_increase = base_yield * (self.ph_level_to_percent(ph_level, soil_type) / 100)

        return nitrogen_level_increase + ph_increase

    @staticmethod
    def _calculate_bonus(base_yield: float, condition: bool, factor: float) -> float:
        """
        Calculate the percentage bonus that should be applied to a field value based on the
        FSData Enum stat and condition, i.e. 'PLOWED' & current_field.plowed
        :param base_yield: the base yield of the crop.
        :param condition: the condition to apply i.e. boolean / in etc.
        :param factor: the Enum stat (PLOWED.value which == 15% bonus).
        :return: (float) of the base yield increase or 0 if false.
        """
        return base_yield * (factor / 100) if condition else 0

    @staticmethod
    def nitrogen_level_to_percent(nitrogen_level: int, crop_required_nitrogen: int) -> float:
        """
        Function to convert a nitrogen level into its 'fertilizer' percent
        and apply penalties for too little and too high nitrogen.
        :param nitrogen_level: the nitrogen level of the field
        :param crop_required_nitrogen: the required nitrogen for a given crop.
        :return: (float) the percentage of fertilizer to apply to a field (max 45%).
        """
        logger.info(f"Nitrogen Level: {nitrogen_level} - Crop Perfect Nitrogen: {crop_required_nitrogen}")

        # catch edge cases for grass, oil seed and soybeans that have a 0kg/ha perfect nitrogen
        if crop_required_nitrogen == 0 or crop_required_nitrogen is None:
            return FertilizerStates.ONE_HUNDRED_PERCENT.value

        # Calculate the percentage when the nitrogen level is less than or equal to the perfect nitrogen level
        if nitrogen_level <= crop_required_nitrogen:
            logger.info("Nitrogen level is less than or equal to crops returning up to a 45% percentage (max)")
            nitrogen_percentage = (nitrogen_level / crop_required_nitrogen) * FertilizerStates.ONE_HUNDRED_PERCENT.value
        else:
            # Apply a penalty if the nitrogen level is greater than the perfect nitrogen level
            # Unsure exactly how this calculated in game (will likely need to revisit when PF comes out for FS25)
            logger.info("Nitrogen level is greater than required nitrogen, applying reduction")
            excess = nitrogen_level / crop_required_nitrogen
            nitrogen_percentage = (FertilizerStates.ONE_HUNDRED_PERCENT.value / excess)

        return max(nitrogen_percentage, 0)

    @staticmethod
    def ph_level_to_percent(ph_level: float, soil_type: SoilTypes) -> int:
        """
        Calculate the yield bonus to apply to a field based on its soil type and pH level.
        :param ph_level: the current pH level of the field.
        :param soil_type: the majority soil_type in a field.
        :return: (int) of the pH level bonus percentage.
        """
        # create a dict of the soil type expected pH levels.
        percentage_table = {
            SoilTypes.LOAM: FSData.LOAM_PH_LEVELS.value,
            SoilTypes.SANDY_LOAM: FSData.SANDY_LOAM_PH_LEVELS.value,
            SoilTypes.LOAMY_SAND: FSData.LOAMY_SAND_PH_LEVELS.value,
            SoilTypes.SILTY_CLAY: FSData.SILTY_CLAY_PH_LEVELS.value,
        }

        logger.info(f"pH Level: {ph_level} - Soil Type: {soil_type}")

        if soil_type not in percentage_table:
            logger.info(f"Soil Type: {soil_type} not found, returning 0")
            return 0

        # Get the bonus thresholds for the given soil type
        thresholds = percentage_table[soil_type]
        max_threshold = thresholds[0][0]

        if ph_level > max_threshold:
            logger.info(f"pH Level: {ph_level} exceeds max threshold: {max_threshold}, returning 0")
            return 0

        # iterate over each threshold and bonus and check the pH level is within a threshold
        # and apply its bonus.
        for threshold, bonus in thresholds:
            if ph_level >= threshold:
                logger.info(f"Calculating percentage bonus for pH Level: {ph_level}/{threshold} = {bonus}%")
                return bonus

        return 0

    @staticmethod
    async def get_crop(current_field: Field, future_crop: Optional[str]) -> Crop:
        """
        Util to get either the current crop or a future crop sent with the request.
        :param current_field: the field to get the current crop from
        :param future_crop: get a 'future' crop by its type i.e. wheat.
        :return: (Crop) a crop from the database.
        """
        if future_crop:
            return await CropService.get_crop_by_type(future_crop)
        return await CropService.get_crop_details(current_field.current_crop().crop_id)
