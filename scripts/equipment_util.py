import os, traceback
import xml.etree.ElementTree as ET
from flask import Blueprint, jsonify, send_from_directory
from models.vehicle import Vehicle
from app import database, app
from PIL import Image

equipment_util = Blueprint("equipment_util", __name__, url_prefix="/equipment")


def collect_equipment():
    """
    Traverse the file system for all vehicles and equipment adding them to the database,
    if the static directory is not populated.

    """
    equipment_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Farming Simulator 22\\data\\vehicles"
    static_directory = "static"
    invalid_file_count = 0
    valid_file_count = 0

    if os.path.exists(equipment_path):
        if is_images_created(static_directory):
            for root, directories, files in os.walk(equipment_path):
                for file in files:

                    vehicle = Vehicle(
                        model="",
                        brand="",
                        category="",
                        price=0,
                        power=0,
                        img_url=""
                    )

                    if file.endswith(".xml"):

                        file_path = os.path.join(root, file)

                        if is_invalid_file(root, file):
                            print(f"[IGNORING INVALID FILE]: {file_path}")
                            invalid_file_count = invalid_file_count + 1
                            continue

                        print(f"[PARSING VALID FILE]: {file_path}")
                        valid_file_count = valid_file_count + 1

                        tree = ET.parse(file_path)
                        root_element = tree.getroot()

                        # Extract data from the storeData section
                        store_data = root_element.find(".//storeData")

                        if store_data:
                            vehicle.model = clean_xml_value(store_data.find("name").text)
                            vehicle.brand = store_data.find("brand").text
                            vehicle.category = store_data.find("category").text
                            vehicle.power = get_power_value(store_data)
                            vehicle.price = int(store_data.find("price").text) if (store_data.find("price")
                                                                                   is not None) else 0

                            image_element = store_data.find("image")
                            if image_element is not None:
                                image_path = image_element.text
                                filename = os.path.basename(image_path)
                                new_filename = os.path.splitext(filename)[0] + ".dds"
                                vehicle.img_url = convert_store_image(os.path.join(root, new_filename))

                            if has_configuration(root_element):
                                handle_configurations(root_element, vehicle)
                            else:
                                database.session.add(vehicle)
                        else:
                            try:
                                raise ValueError(f"store_data is empty. - {file_path}")
                            except ValueError as e:
                                print("An error occurred:", e)
                                traceback.print_exc()
        else:
            print("Equipment already collected, ignoring.")

    database.session.commit()
    return jsonify({"message": f"{valid_file_count} Valid XML Files, {invalid_file_count} Invalid XML files"}), 200


def handle_configurations(root, vehicle):
    """
    if a vehicle has a motorConfig (Different tractor variant) loop over each config creating a new vehicle,
    with a new price.
    :param root: root of the XML file
    :param vehicle: the 'base' vehicle found in collect_vehicles
    """
    motor_configurations = root.findall(".//motorConfigurations/motorConfiguration")

    for config in motor_configurations:
        config_price = int(config.attrib.get("price") or 0)

        vehicle_configuration = Vehicle(
            model=clean_xml_value(config.attrib.get("name", vehicle.model)),
            brand=vehicle.brand,
            category=vehicle.category,
            price=vehicle.price + config_price,
            power=int(config.attrib.get("hp", vehicle.power)),
            img_url=vehicle.img_url
        )

        database.session.add(vehicle_configuration)


def has_configuration(root):
    """
    Check if a vehicle has a motor configuration to create a variant in handle_configurations

    :param root: the root XML element.
    :return: (bool) if the motorConfiguration exists
    """
    motor_configuration = root.find(".//motorConfigurations")

    if motor_configuration is not None:
        return True
    else:
        return False


def clean_xml_value(name):
    """
    'Clean up' the xml names removing any invalid characters and replacing them with an ASCII equivalent.

    :param name: The value to be cleaned up.
    :return: (str) the name with replaced characters
    """

    replacements = {
        '\u2011': '-'
    }

    return ''.join(replacements.get(character, character) for character in name)


def convert_store_image(dds_input_path):
    try:
        dds_image = Image.open(dds_input_path)
        rgba_image = dds_image.convert("RGBA")

        output_folder = "static"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_image_name = os.path.splitext(os.path.basename(dds_input_path))[0] + ".webp"
        output_image_path = os.path.join(output_folder, output_image_name)

        rgba_image.save(output_image_path, "WEBP")

        return output_image_path

    except Exception as e:
        print("conversion failed:", e)
        return None


def get_power_value(store_data):
    """
    Get either the power of a vehicle, or the power required power needed from an implement.

    :param store_data: storeData XML element.
    :return: Return either required value or none.
    """
    power_element = store_data.find("specs/power")
    if power_element is not None:
        return int(power_element.text)

    needed_power = store_data.find("specs/neededPower")
    if needed_power is not None:
        return int(needed_power.text)

    return None


def is_invalid_file(root, file):
    """
    Check if the file should be ignored, i.e. sounds.xml or bundle files which reference
    whole xml files already parsed.

    :param root: The root directory of the file.
    :param file: the file name.
    :return: (bool) True if the file should be ignored, False if it should be parsed
    """

    ignored_directories = ["sounds", "cars"]
    ignored_files = ["Bundle", "store", "Light"]

    # Check if the root directory contains any of the ignore_directories
    if any(directory in root.split(os.path.sep) for directory in ignored_directories):
        return True

    # Check if the file name contains any of the strings in ignore_files_contain
    if any(keyword in file for keyword in ignored_files):
        return True


def is_images_created(static_directory):
    """
    Check if the static directory is empty.
    """
    return len(os.listdir(static_directory)) == 0


@equipment_util.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@equipment_util.route('/vehicles')
def get_all_vehicles():
    vehicles = Vehicle.query.all()
    vehicles_json = []

    for vehicle in vehicles:
        vehicle_dict = {
            'id': vehicle.id,
            'model': vehicle.model,
            'brand': vehicle.brand,
            'category': vehicle.category,
            'img_url': vehicle.img_url,
            'price': vehicle.price,
            'power': vehicle.power
        }

        vehicles_json.append(vehicle_dict)

    return jsonify(vehicles_json)
