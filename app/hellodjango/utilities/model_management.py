from locations.models import *

# logging

import logging

logger = logging.getLogger("django")

# django imports


def create_united_states_address(
    primary_number: str,
    street_name: str,
    city_name: str,
    state_abbreviation: str,
    zip5: str,
    longitude: float = None,
    latitude: float = None,
):

    simple_address = f"{primary_number}; {street_name} ;{city_name} ;{state_abbreviation} ;{zip5} ; {longitude} ; {latitude}"

    message = ""
    message += f"Trying to create an address for {simple_address}"
    logging.info(message)

    try:
        us_address = United_States_Address(
            primary_number=primary_number,
            street_name=street_name,
            city_name=city_name,
            state_abbreviation=state_abbreviation,
            zip5=zip5,
            longitude=longitude,
            latitude=latitude,
        )
        print(us_address)
        us_address.save()
        message = ""
        message += f"Successfully created an address for {simple_address}"
        logging.info(message)
        return us_address

    except Exception as e:
        message = ""
        message += f"Failed to create an address for {simple_address}: {e}"
        return False


def update_model_fields_to_single_value(
    target_model, fields_to_update: list, existing_value, intended_value
) -> bool:

    for field in fields_to_update:
        try:
            target_objects = target_model.objects.filter(field=existing_value)
            # this is what I think should work
            target_objects.update(field=intended_value).update(field=None)

        except Exception as e:
            message = ""
            message += f"Failed to update {field} for {target_model}: {e}"
            logging.error(message)


def update_model_geometry_foreign_keys(
    target_object,
):
    """
    This function takes a GeoDjango object and updates the foreign keys based on the geometry value.
    The foreign keys are spatial relationships, so it is an intersection.
    This function relies on the fact that you have followed OSGeo convention and used "geom" as the name of your
    geometry columns. Have fun refactoring if you haven't.
    :param target_object: this is the object itself
    :return: the object to be saved
    """

    model_keys_and_names = {
        "gid_0": Admin_Level_0,
        "gid_1": Admin_Level_1,
        "gid_2": Admin_Level_2,
        "gid_3": Admin_Level_3,
        "gid_4": Admin_Level_4,
        "gid_5": Admin_Level_5,
    }

    # get all object model fields that we need to test
    target_object_fields = [
        field.name for field in target_object._meta.get_fields(include_parents=True)
    ]
    keys_to_test = [
        tof for tof in target_object_fields if tof in model_keys_and_names.keys()
    ]

    # now we test the values

    for k in keys_to_test:

        foreign_model = model_keys_and_names[k]
        try:
            foreign_geom_object = foreign_model.objects.get(
                geom__intersects=target_object.geom
            )
            # Use getattr/setattr to interact with values of object
            setattr(target_object, k, foreign_geom_object)
        except Exception as e:
            message = ""
            message += f"Failed to update {k} for {target_object}: {e}"
            logging.info(message)

    return target_object
