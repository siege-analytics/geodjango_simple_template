from locations.models import *

# logging

import logging

logger = logging.getLogger("django")


def create_united_states_address(
    primary_number: str, street_name: str, city_name: str, state_abbreviation: str, zip5
):

    simple_address = (
        f"{primary_number} {street_name} {city_name} {state_abbreviation} {zip5}"
    )

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
