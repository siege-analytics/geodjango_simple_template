"""
VTD-Congressional District Intersection Model
"""

from django.contrib.gis.db import models


class VTDCongressionalDistrictIntersection(models.Model):
    """
    Pre-computed VTD-CD intersections
    
    Use Case: "This VTD is split between 2 CDs - attribute donors"
    
    Critical for donor attribution in split precincts
    """
    
    vtd = models.ForeignKey(
        'United_States_Census_Voter_Tabulation_District',
        on_delete=models.CASCADE,
        related_name='cd_intersections'
    )
    
    cd = models.ForeignKey(
        'United_States_Census_Congressional_District',
        on_delete=models.CASCADE,
        related_name='vtd_intersections'
    )
    
    year = models.IntegerField()
    
    # ==== Intersection Geometry ====
    intersection_geom = models.MultiPolygonField(
        srid=4269,
        help_text="Part of VTD that's in this CD"
    )
    
    # ==== Overlap Metrics ====
    intersection_area_sqm = models.BigIntegerField()
    
    pct_of_vtd = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% of VTD in this CD (for proportional attribution)"
    )
    
    pct_of_cd = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% of CD covered by this VTD"
    )
    
    # ==== Attribution Helper ====
    is_dominant = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if >50% of VTD is in this CD (dominant for attribution)"
    )
    
    # ==== Metadata ====
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'geo_intersection_vtd_cd'
        verbose_name = 'VTD-CD Intersection'
        verbose_name_plural = 'VTD-CD Intersections'
        unique_together = [['vtd', 'cd', 'year']]
        indexes = [
            models.Index(fields=['year', 'vtd', 'is_dominant']),
            models.Index(fields=['year', 'cd']),
            models.Index(fields=['pct_of_vtd']),
        ]
        ordering = ['vtd', '-pct_of_vtd']
    
    def __str__(self):
        return f"{self.vtd.namelsad} ∩ {self.cd.namelsad} ({self.pct_of_vtd:.1f}% of VTD)"

