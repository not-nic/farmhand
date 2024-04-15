from flask import Blueprint, request, jsonify
from app import database
from sqlalchemy.exc import IntegrityError
from models.field import Field
from models.field_crop import FieldCrop, GrowthTense

fields = Blueprint("fields_blueprint", __name__, url_prefix="/api")


@fields.route("/field", methods=["POST"])
def create_field():
    """
    Create a field entry in the database, from the POST request.
    :return: (str) 200 response if a field is created successfully.
    """
    data = request.get_json()

    required_attributes = ["field_number", "ground_type", "soil_type", "nitrogen_level",
                           "ph_level", "plowed", "rolled", "weeded", "mulched"]

    if not all(field in data for field in required_attributes):
        return jsonify({"error": "Missing required JSON fields."}), 400

    empty_attributes = [field for field in required_attributes if data.get(field) in (None, '')]
    if empty_attributes:
        return jsonify({"error": f"The following values are empty: {', '.join(empty_attributes)}."}), 400

    try:
        new_field = Field(
            number=data["field_number"],
            ground_type=data["ground_type"],
            soil_type=data["soil_type"],
            nitrogen_level=data["nitrogen_level"],
            ph_level=data["ph_level"],
            plowed=data["plowed"],
            rolled=data["rolled"],
            weeded=data["weeded"],
            mulched=data["mulched"]
        )

        database.session.add(new_field)
        database.session.commit()

        return jsonify({"message": "Field created successfully"}), 200
    except IntegrityError:
        database.session.rollback()
        return jsonify({"error": f"Field {data['field_number']} already exists."}), 400


@fields.route("/crop", methods=["POST"])
def add_crop():
    """
    Create a crop entry in the database, from the POST request.
    :return: (str) 200 response if a crop is created successfully.
    """
    data = request.get_json()

    field_number = data["field_number"]

    new_crop = FieldCrop(
        type=data["type"],
        growth_stage=data["growth_stage"],
        growth_tense=data["growth_tense"],
        field_id=field_number,
    )

    field = Field.query.filter_by(number=field_number).first()

    if field:
        database.session.add(new_crop)
        database.session.commit()

        return jsonify({"message": "Crop created successfully"}), 200
    else:
        return jsonify({"message": f"No field created for field {field_number}"}), 400


@fields.route("/field/<number>", methods=["PATCH"])
def update_field(number: int):
    """
    Send a PATCH request to update a value in the field table.
    :param number: The number of the field to update.
    :return: (str) 200 or 400 message depending on success or failure.
    """
    data = request.get_json()

    try:
        field = Field.query.filter_by(number=number).first()

        if field:
            # loop over keys & values present in the patch request
            for key, value in data.items():
                # check if a key exists in the field object and update it.
                if hasattr(field, key):
                    setattr(field, key, value)

            database.session.commit()

            return jsonify({"message": f"Field {number} updated successfully."}), 200
        else:
            return jsonify({"error": f"Field with ID {number} not found."}),

    except IntegrityError:
        database.session.rollback()
        return jsonify({"error": f"Failed to update field {number}."}), 400


@fields.route("/field", methods=["GET"])
def get_all_crops():
    """
    Get all crops from the database and return them as a json object.
    :return: (Field) Return a list of created fields & crops.
    """
    field_query = Field.query.all()
    all_fields = []

    if field_query:
        for field in field_query:
            all_fields.append(field_response_object(field))

        return jsonify(all_fields), 200
    else:
        return jsonify({"error": "Fields not found"})


@fields.route("/field/<number>", methods=["GET"])
def get_field_crop(number: int):
    """
    Retrieve a Field object & its crops from the database given its field number.
    :return: (Field) Return a json object of the requested field & crop.
    """
    field = Field.query.filter_by(number=number).first()

    if field:
        return jsonify(field_response_object(field)), 200
    else:
        return jsonify({"error": "Field not found"})


@fields.route("/field/<number>", methods=["DELETE"])
def delete_field(number: int):
    """
    Delete a field by its field number.
    :param number: the number of the field to be deleted
    :return: (str) success or error message.
    """
    field = Field.query.filter_by(number=number).first()

    if field:

        # delete crops associated with field first.
        for crop in field.crops:
            database.session.delete(crop)

        database.session.delete(field)
        database.session.commit()

        return jsonify({"message": f"Field {number} has been deleted."})
    else:
        return jsonify({"message": f"Field {number} doesn't exist."})


@fields.route("/field/past/<number>", methods=["GET"])
def get_past_crops(number: int):
    """
    get all the past crops for a field number
    :param number: the number of the field to retrieve the crops from
    :return: (dict) of past crops
    """
    return get_crops_by_tense(number, GrowthTense.PAST), 200


@fields.route("/field/present/<number>", methods=["GET"])
def get_present_crops(number: int):
    """
    get all the present crops for a field number
    :param number: the number of the field to retrieve the crops from
    :return: (dict) of present crops
    """
    return get_crops_by_tense(number, GrowthTense.PRESENT), 200


@fields.route("/field/future/<number>", methods=["GET"])
def get_future_crops(number: int):
    """
    get all the future crops for a field number
    :param number: the number of the field to retrieve the crops from
    :return: (dict) of future crops
    """
    return get_crops_by_tense(number, GrowthTense.FUTURE), 200


def field_response_object(field: Field) -> dict:
    """
    json response object of a field.
    :param field: The field to be converted into Json.
    :return: (dict) a dict of the field values.
    """
    return {
        "number": field.number,
        "ground_type": field.ground_type,
        "soil_type": field.soil_type,
        "nitrogen_level": field.nitrogen_level,
        "ph_level": field.ph_level,
        "plowed": field.plowed,
        "rolled": field.rolled,
        "mulched": field.mulched,
        "crops": [get_crop_details(crop) for crop in field.crops]
    }


def get_crop_details(crop: FieldCrop) -> dict:
    """
    json response object of a crop.
    :param crop: The crop to be converted into Json.
    :return: (dict) a dict of the crop values.
    """
    return {
        "type": crop.type,
        "growth_stage": crop.growth_stage,
        "growth_tense": crop.growth_tense.value,
        "field_id": crop.field_id
    }


def get_crops_by_tense(number: int, tense: GrowthTense):
    """
    return
    :param tense: if the function should return the PAST, PRESENT or FUTURE crops
    :param number: the number of the field to retrieve the crops from
    :return: (dict) of crops by their tense crops
    """
    field = Field.query.filter_by(number=number).first()
    future_crops = []

    if field:
        for crop in field.crops:
            if crop.growth_tense == tense:
                future_crops.append(get_crop_details(crop))

    return jsonify(future_crops)
