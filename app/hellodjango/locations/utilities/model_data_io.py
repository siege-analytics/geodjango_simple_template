from locations.models import *


def create_address_from_supplied_data(
    primary_number: str, street_name: str, city_name: str, state_abbreviation: str, zip5
) -> United_States_Address:

    simple_address = (
        f"{primary_number} {street_name} {city_name} {state_abbreviation} {zip5}"
    )
    message = ""
    message += f"Trying to create an address for {simple_address}"
    logging.info(message)

    try:
        us_address = United_States_Address(
            primary_number=row["number"],
            street_name=concatenated_street_name,
            city_name=row["city"],
            state_abbreviation=row["state"],
            zip5=row["zip"],
        )
        us_address.save()
        message = ""
        message += f"Successfully created an address for {simple_address}"
        logging.info(message)
        return us_address

    except Exception as e:
        message = ""
        message += f"Failed to create an address for {simple_address}: {e}"
        return False
