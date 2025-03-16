from src.api.constants import FarmTypes, WeedStates, SoilTypes, FertilizerStates, FieldTypes
from src.api.core.db_models import User, Crop, Farm, Field, BaseField, PrecisionFarmingField, FieldCrop
from src.api.core.security import Security
from src.api.utils import logger
from src.config import settings


class Fixtures:
    @staticmethod
    def create_service_user() -> User:
        """
        Python fixture to create or update a service-user on startup of the application.
        If the service user already exists, update the username, email, and password.
        :return: (User) the created or updated user.
        """

        logger.info("Creating service user...")

        user_data = {
            "username": settings.SERVICE_USER_USERNAME,
            "email_address": settings.SERVICE_USER_EMAIL,
            "password": Security.get_password_hash(settings.SERVICE_USER_PASSWORD),
            "name": "service-user"
        }

        service_user = User.get_by_username(username=settings.SERVICE_USER_USERNAME)

        if not service_user:
            service_user = User.create(**user_data)
            logger.info(f"Service user created - {service_user.email_address}")
        else:
            logger.info("Service user already exists, updating values if changed.")
            service_user.update(id=service_user.id, **user_data)

        return service_user

    @staticmethod
    def create_field(farm_type, farm_id, number, crop=None, **kwargs):
        """
        Factory method to create fields based on farm type.
        """
        if farm_type == FarmTypes.BASE:
            # Create a BaseField for Base farm type
            field = BaseField.create(
                number=number,
                farm_id=farm_id,
                field_type=FieldTypes.BASE_FIELD.value,
                ground_type=kwargs.get("ground_type"),
                fertilized=kwargs.get("fertilized"),
                limed=kwargs.get("limed"),
                plowed=kwargs.get("plowed"),
                rolled=kwargs.get("rolled"),
                weeds=kwargs.get("weeds"),
                mulched=kwargs.get("mulched")
            )
        elif farm_type == FarmTypes.PRECISION_FARMING:
            # Create a PrecisionFarmingField for Precision Farming farm type
            field = PrecisionFarmingField.create(
                number=number,
                farm_id=farm_id,
                field_type=FieldTypes.PRECISION_FARMING_FIELD,
                ground_type=kwargs.get("ground_type"),
                nitrogen_level=kwargs.get("nitrogen_level"),
                ph_level=kwargs.get("ph_level"),
                soil_type=kwargs.get("soil_type"),
                plowed=kwargs.get("plowed"),
                rolled=kwargs.get("rolled"),
                weeds=kwargs.get("weeds"),
                mulched=kwargs.get("mulched")
            )
        else:
            raise ValueError(f"Unsupported farm type: {farm_type}")

        if crop:
            field_crop = FieldCrop.create(field=field, crop=crop)
            field.crops.append(field_crop)

        return field

    def create_field_and_crops(self) -> None:
        logger.info("CREATING FARM, CROPS and FIELDS as a TEST...")

        service_user = User.get_by_username(settings.SERVICE_USER_USERNAME)

        wheat = Crop.create(name="Wheat")
        corn = Crop.create(name="Corn")

        base_farm = Farm.create(
            name="BASE FARM",
            description="new BASE farm desc",
            owner_id=service_user.id,
            farm_type=FarmTypes.BASE,
            map_name="Oak Bridge Farm",
        )

        precision_farming_farm = Farm.create(
            name="PRECISION FARMING FARM",
            description="new PRECISION FARMING farm desc",
            owner_id=service_user.id,
            farm_type=FarmTypes.PRECISION_FARMING,
            map_name="Oak Bridge Farm",
        )

        self.create_field(
            farm_type=FarmTypes.BASE,
            farm_id=base_farm.id,
            number=1,
            ground_type="ready to harvest",
            fertilized=FertilizerStates.FIFTY_PERCENT,
            limed=False,
            plowed=True,
            rolled=False,
            weeds=WeedStates.LARGE_WEEDS,
            mulched=False,
            crop=wheat
        )

        self.create_field(
            farm_type=FarmTypes.PRECISION_FARMING,
            farm_id=precision_farming_farm.id,
            number=1,
            ground_type="ready to plant",
            nitrogen_level=100,
            ph_level=6.5,
            soil_type=SoilTypes.LOAM,
            plowed=True,
            rolled=False,
            weeds=WeedStates.SMALL_WEEDS,
            mulched=False,
            crop=corn
        )