"""
Geographic Intersection Models

Pre-computed spatial relationships between geographic units
Stores intersection geometries and overlap percentages for fast queries
"""

from django.contrib.gis.db import models


class CountyCongressionalDistrictIntersection(models.Model):
    """
    Pre-computed County-CD intersections
    
    Use Case: "Which CDs overlap with this county?"
    
    Example: San Francisco County (06075) is split between:
        - CA-11: 42.3% of county
        - CA-12: 57.7% of county
    """
    
    county = models.ForeignKey(
        'United_States_Census_County',
        on_delete=models.CASCADE,
        related_name='cd_intersections'
    )
    
    cd = models.ForeignKey(
        'United_States_Census_Congressional_District',
        on_delete=models.CASCADE,
        related_name='county_intersections'
    )
    
    year = models.IntegerField(
        help_text="Census year (both county and CD must match)"
    )
    
    # ==== Intersection Geometry ====
    intersection_geom = models.MultiPolygonField(
        srid=4269,
        help_text="The actual intersection geometry (for mapping!)"
    )
    
    # ==== Overlap Metrics ====
    intersection_area_sqm = models.BigIntegerField(
        help_text="Area of intersection (square meters)"
    )
    
    pct_of_county = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% of County area that overlaps with CD"
    )
    
    pct_of_cd = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% of CD area that overlaps with County"
    )
    
    # ==== Classification ====
    relationship = models.CharField(
        max_length=20,
        choices=[
            ('COUNTY_IN_CD', 'County fully within CD'),
            ('CD_IN_COUNTY', 'CD fully within county'),
            ('SPLIT', 'County split between CDs'),
        ],
        help_text="Type of spatial relationship"
    )
    
    is_dominant = models.BooleanField(
        default=False,
        help_text="True if this CD contains >50% of county (for attribution)"
    )
    
    # ==== Metadata ====
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'geo_intersection_county_cd'
        verbose_name = 'County-CD Intersection'
        verbose_name_plural = 'County-CD Intersections'
        unique_together = [['county', 'cd', 'year']]
        indexes = [
            models.Index(fields=['year', 'county']),
            models.Index(fields=['year', 'cd']),
            models.Index(fields=['relationship']),
            models.Index(fields=['is_dominant']),
            models.Index(fields=['pct_of_county']),
        ]
        ordering = ['county', '-pct_of_county']
    
    def __str__(self):
        return f"{self.county.namelsad} ∩ {self.cd.namelsad} ({self.pct_of_county:.1f}% of county)"



