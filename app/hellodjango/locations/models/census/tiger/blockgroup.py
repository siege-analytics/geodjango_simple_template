# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class United_States_Census_Block_Group(models.Model):

    # given fields
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)
    blkgrpce = models.CharField(max_length=1)
    geoid = models.CharField(max_length=12)
    geoidfq = models.CharField(max_length=21)
    namelsad = models.CharField(max_length=13)
    mtfcc = models.CharField(max_length=5)
    funcstat = models.CharField(max_length=1)
    aland = models.BigIntegerField()
    awater = models.BigIntegerField()
    intptlat = models.CharField(max_length=11)
    intptlon = models.CharField(max_length=12)

    # Geometry field

    geom = models.PolygonField(srid=4269)

    # year

    year = models.IntegerField()
    
    # ==== INTER-RELATIONS: Hierarchical ForeignKeys ====
    state = models.ForeignKey(
        'United_States_Census_State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='block_groups',
        db_constraint=False,
        help_text="Parent state"
    )
    
    county = models.ForeignKey(
        'United_States_Census_County',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='block_groups',
        db_constraint=False,
        help_text="Parent county"
    )
    
    tract = models.ForeignKey(
        'United_States_Census_Tract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='block_groups',
        db_constraint=False,
        help_text="Parent tract"
    )

    def __str__(self):
        representative_string = self.namelsad
        return representative_string
    
    def populate_parent_relationships(self):
        """Populate state, county, and tract FKs"""
        from .state import United_States_Census_State
        from .county import United_States_Census_County
        from .tract import United_States_Census_Tract
        
        self.state = United_States_Census_State.objects.filter(
            statefp=self.statefp,
            year=self.year
        ).first()
        
        self.county = United_States_Census_County.objects.filter(
            statefp=self.statefp,
            countyfp=self.countyfp,
            year=self.year
        ).first()
        
        self.tract = United_States_Census_Tract.objects.filter(
            statefp=self.statefp,
            countyfp=self.countyfp,
            tractce=self.tractce,
            year=self.year
        ).first()
        
        if self.state and self.county and self.tract:
            self.save()
            return True
        return False


# Auto-generated `LayerMapping` dictionary for US_Census_Block_Group model
# united_states_census_block_group_mapping = {
#     "statefp": "STATEFP",
#     "countyfp": "COUNTYFP",
#     "tractce": "TRACTCE",
#     "blkgrpce": "BLKGRPCE",
#     "geoid": "GEOID",
#     "geoidfq": "GEOIDFQ",
#     "namelsad": "NAMELSAD",
#     "mtfcc": "MTFCC",
#     "funcstat": "FUNCSTAT",
#     "aland": "ALAND",
#     "awater": "AWATER",
#     "intptlat": "INTPTLAT",
#     "intptlon": "INTPTLON",
#     "geom": "POLYGON",
# }
