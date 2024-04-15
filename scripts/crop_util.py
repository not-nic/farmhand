import os, json
from app import database
from models.crop import Crop


def load_crops():
    """
    Load crop information json into the database on app start.
    no return
    """
    crops_file_path = os.path.join('app', 'crops.json')

    try:
        with open(crops_file_path, 'r') as file:
            crop_data = json.load(file)

            for crop in crop_data["crops"]:

                existing_crop = Crop.query.filter_by(crop_type=crop["type"]).first()

                if existing_crop:
                    print(f"[INFO]: {existing_crop.crop_type} already exists.")
                else:
                    crop = Crop(
                        crop_type=crop["type"],
                        nitrogen_level=crop["nitrogenLevel"],
                        growth_stages=crop["growthStages"],
                        yield_per_ha=crop["yieldPerHa"],
                        seeds_per_ha=crop["seedsPerHa"],
                        price_per_tonne=crop["price"],
                        root_crop=crop["rootCrop"]
                    )

                    print(f"[INFO]: Added {crop.crop_type} to database.")
                    database.session.add(crop)

            database.session.commit()
            print("[INFO]: All Crops added")
    except FileNotFoundError:
        print(f"'crops.json' does not exist.")
