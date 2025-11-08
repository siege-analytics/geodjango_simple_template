# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class United_States_Census_Tract(models.Model):
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)
    geoid = models.CharField(max_length=11)
    geoidfq = models.CharField(max_length=20)
    name = models.CharField(max_length=7)
    namelsad = models.CharField(max_length=20)
    mtfcc = models.CharField(max_length=5)
    funcstat = models.CharField(max_length=1)
    aland = models.BigIntegerField()
    awater = models.BigIntegerField()
    intptlat = models.CharField(max_length=11)
    intptlon = models.CharField(max_length=12)

    # geom fields

    geom = models.MultiPolygonField(srid=4269)

    # year
    year = models.IntegerField()
    
    # ==== INTER-RELATIONS: Hierarchical ForeignKeys ====
    state = models.ForeignKey(
        'United_States_Census_State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracts',
        db_constraint=False,
        help_text="Parent state"
    )
    
    county = models.ForeignKey(
        'United_States_Census_County',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracts',
        db_constraint=False,
        help_text="Parent county"
    )

    # representative string

    def __str__(self):
        representative_string = self.namelsad
        return representative_string
    
    def populate_parent_relationships(self):
        """Populate state and county FKs"""
        from .state import United_States_Census_State
        from .county import United_States_Census_County
        
        self.state = United_States_Census_State.objects.filter(
            statefp=self.statefp,
            year=self.year
        ).first()
        
        self.county = United_States_Census_County.objects.filter(
            statefp=self.statefp,
            countyfp=self.countyfp,
            year=self.year
        ).first()
        
        if self.state and self.county:
            self.save()
            return True
        return False


# Auto-generated `LayerMapping` dictionary for United_States_Census_Tract model
united_states_census_tract_mapping = {
    "statefp": "STATEFP",
    "countyfp": "COUNTYFP",
    "tractce": "TRACTCE",
    "geoid": "GEOID",
    "geoidfq": "GEOIDFQ",
    "name": "NAME",
    "namelsad": "NAMELSAD",
    "mtfcc": "MTFCC",
    "funcstat": "FUNCSTAT",
    "aland": "ALAND",
    "awater": "AWATER",
    "intptlat": "INTPTLAT",
    "intptlon": "INTPTLON",
    "geom": "MULTIPOLYGON",
}
