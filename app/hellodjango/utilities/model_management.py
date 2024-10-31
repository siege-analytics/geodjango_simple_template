from locations.models import *

# logging

import logging

logger = logging.getLogger("django")


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
