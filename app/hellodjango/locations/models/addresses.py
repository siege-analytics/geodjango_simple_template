from __future__ import unicode_literals
from django.contrib.gis.db import models

# This address definition is based on the Smarty Streets definition for now

class United_States_Address(models.Model):

    # This is an address in the US


    primary_number=models.CharField(
        max_length=250, null=True, blank=True, default=None)
    street_name=models.CharField(
        max_length=250, null=True, blank=True, default=None)
    street_suffix=models.CharField(
        max_length=250, null=True, blank=True, default=None)
    city_name=models.CharField(
        max_length=250, null=True, blank=True, default=None)
    default_city_name=models.CharField(
        max_length=250, null=True, blank=True, default=None)
    state_abbreviation=models.CharField(
        max_length=2, null=True, blank=True, default=None)
    zip5=(models.CharField
          (max_length=5, null=True, blank=True, default=None))
    plus4_code=models.CharField(max_length=4, null=True, blank=True, default=None),
    delivery_point=models.CharField(max_length=99, null=True, blank=True, default=None)
    delivery_point_check_digit=models.CharField(max_length=99, null=True, blank=True, default=None)
    record_type=models.CharField(max_length=250, null=True, blank=True, default=None)
    zip_type=models.CharField(max_length=250, null=True, blank=True, default=None)
    county_fips=models.CharField(max_length=250, null=True, blank=True, default=None)
    county_name=models.CharField(max_length=250, null=True, blank=True, default=None)
    carrier_route=models.CharField(max_length=250, null=True, blank=True, default=None)
    congressional_district=models.CharField(max_length=250, null=True, blank=True, default=None)
    rdi=models.CharField(max_length=250, null=True, blank=True, default=None)
    elot_sequence=models.CharField(max_length=250, null=True, blank=True, default=None)
    elot_sort=models.CharField(max_length=250, null=True, blank=True, default=None)
    latitude=models.FloatField(null=True, blank=True, default=None),
    longitude=models.FloatField(null=True, blank=True, default=None),
    coordinate_license=models.CharField(max_length=250, null=True, blank=True, default=None)
    precision=models.CharField(max_length=250, null=True, blank=True, default=None)
    time_zone=models.CharField(max_length=250, null=True, blank=True, default=None)
    utc_offset=models.CharField(max_length=250, null=True, blank=True, default=None)

    geom=models.PointField(srid=4326,null=True, blank=True, default=None)