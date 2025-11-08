"""
Compute Geographic Intersections

Pre-computes spatial intersections between census units and stores:
- Intersection geometries (for mapping)
- Overlap percentages (for attribution)
- Area measurements

Run once per census year (2010, 2020). Updates only when boundaries change.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from locations.models.census.tiger import (
    United_States_Census_County,
    United_States_Census_Congressional_District,
    United_States_Census_Voter_Tabulation_District
)
from locations.models.intersections import (
    CountyCongressionalDistrictIntersection,
    VTDCongressionalDistrictIntersection
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Pre-compute geographic intersections (County-CD, VTD-CD)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            required=True,
            choices=[2010, 2020],
            help='Census year'
        )
        
        parser.add_argument(
            '--type',
            choices=['county-cd', 'vtd-cd', 'all'],
            default='all',
            help='Intersection type to compute'
        )
        
        parser.add_argument(
            '--state',
            type=str,
            help='State FIPS (e.g., 06 for CA) - compute for single state only'
        )
        
        parser.add_argument(
            '--min-overlap',
            type=float,
            default=1.0,
            help='Minimum overlap percentage to store (default: 1.0%)'
        )
        
        parser.add_argument(
            '--async',
            action='store_true',
            dest='use_async',
            help='Run via Celery (recommended for all states)'
        )
    
    def handle(self, *args, **options):
        year = options['year']
        intersection_type = options['type']
        state_fips = options.get('state')
        min_overlap = options['min_overlap']
        use_async = options.get('use_async')
        
        self.stdout.write(f"Computing intersections for year {year}")
        if state_fips:
            self.stdout.write(f"  State: {state_fips}")
        
        if use_async:
            # Queue Celery tasks
            from locations.tasks import compute_intersections_for_state_task
            
            if state_fips:
                states = [state_fips]
            else:
                # All states
                states = United_States_Census_State.objects.filter(
                    year=year
                ).values_list('statefp', flat=True)
            
            for state in states:
                result = compute_intersections_for_state_task.delay(
                    state_fips=state,
                    year=year,
                    intersection_type=intersection_type,
                    min_overlap=min_overlap
                )
                self.stdout.write(f"  Queued {state}: task {result.id}")
            
            self.stdout.write(self.style.SUCCESS(f"✅ Queued {len(states)} tasks"))
            self.stdout.write("Monitor in Flower: http://localhost:5555")
        
        else:
            # Synchronous
            if intersection_type in ['county-cd', 'all']:
                self.compute_county_cd_intersections(year, state_fips, min_overlap)
            
            if intersection_type in ['vtd-cd', 'all']:
                self.compute_vtd_cd_intersections(year, state_fips, min_overlap)
    
    def compute_county_cd_intersections(self, year, state_fips=None, min_overlap=1.0):
        """Compute County-CD intersections"""
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"Computing County-CD Intersections (year={year})")
        self.stdout.write(f"{'='*70}\n")
        
        # Get counties
        counties = United_States_Census_County.objects.filter(year=year)
        if state_fips:
            counties = counties.filter(statefp=state_fips)
        
        total_counties = counties.count()
        intersections_created = 0
        
        self.stdout.write(f"Processing {total_counties} counties...")
        
        for i, county in enumerate(counties, 1):
            # Find intersecting CDs
            cds = United_States_Census_Congressional_District.objects.filter(
                statefp=county.statefp,
                year=year,
                geom__intersects=county.geom
            )
            
            county_area = county.aland
            
            for cd in cds:
                try:
                    # Calculate intersection
                    intersection_geom = county.geom.intersection(cd.geom)
                    
                    if intersection_geom.empty:
                        continue
                    
                    # Calculate areas
                    intersection_area = intersection_geom.area
                    cd_area = cd.aland
                    
                    # Calculate percentages
                    pct_county = (intersection_area / county_area) * 100 if county_area > 0 else 0
                    pct_cd = (intersection_area / cd_area) * 100 if cd_area > 0 else 0
                    
                    # Skip trivial overlaps
                    if pct_county < min_overlap and pct_cd < min_overlap:
                        continue
                    
                    # Determine relationship
                    if pct_county >= 99.9:
                        relationship = 'CD_IN_COUNTY'
                    elif pct_cd >= 99.9:
                        relationship = 'COUNTY_IN_CD'
                    else:
                        relationship = 'SPLIT'
                    
                    # Determine dominance
                    is_dominant = pct_county > 50.0
                    
                    # Store
                    CountyCongressionalDistrictIntersection.objects.update_or_create(
                        county=county,
                        cd=cd,
                        year=year,
                        defaults={
                            'intersection_geom': intersection_geom,
                            'intersection_area_sqm': int(intersection_area),
                            'pct_of_county': round(pct_county, 2),
                            'pct_of_cd': round(pct_cd, 2),
                            'relationship': relationship,
                            'is_dominant': is_dominant
                        }
                    )
                    
                    intersections_created += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {county.geoid} ∩ {cd.geoid}: {e}"))
            
            # Progress
            if i % 10 == 0:
                self.stdout.write(f"  Progress: {i}/{total_counties} ({i/total_counties*100:.1f}%)")
        
        self.stdout.write(self.style.SUCCESS(f"✅ Created {intersections_created} County-CD intersections"))
    
    def compute_vtd_cd_intersections(self, year, state_fips=None, min_overlap=1.0):
        """Compute VTD-CD intersections"""
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"Computing VTD-CD Intersections (year={year})")
        self.stdout.write(f"{'='*70}\n")
        
        # Get VTDs
        vtds = United_States_Census_Voter_Tabulation_District.objects.filter(year=year)
        if state_fips:
            vtds = vtds.filter(statefp=state_fips)
        
        total_vtds = vtds.count()
        intersections_created = 0
        
        self.stdout.write(f"Processing {total_vtds} VTDs...")
        
        for i, vtd in enumerate(vtds, 1):
            # Find intersecting CDs
            cds = United_States_Census_Congressional_District.objects.filter(
                statefp=vtd.statefp,
                year=year,
                geom__intersects=vtd.geom
            )
            
            vtd_area = vtd.aland
            
            for cd in cds:
                try:
                    # Calculate intersection
                    intersection_geom = vtd.geom.intersection(cd.geom)
                    
                    if intersection_geom.empty:
                        continue
                    
                    # Calculate areas
                    intersection_area = intersection_geom.area
                    cd_area = cd.aland
                    
                    # Calculate percentages
                    pct_vtd = (intersection_area / vtd_area) * 100 if vtd_area > 0 else 0
                    pct_cd = (intersection_area / cd_area) * 100 if cd_area > 0 else 0
                    
                    # Skip trivial overlaps
                    if pct_vtd < min_overlap:
                        continue
                    
                    # Determine dominance (for attribution)
                    is_dominant = pct_vtd > 50.0
                    
                    # Store
                    VTDCongressionalDistrictIntersection.objects.update_or_create(
                        vtd=vtd,
                        cd=cd,
                        year=year,
                        defaults={
                            'intersection_geom': intersection_geom,
                            'intersection_area_sqm': int(intersection_area),
                            'pct_of_vtd': round(pct_vtd, 2),
                            'pct_of_cd': round(pct_cd, 2),
                            'is_dominant': is_dominant
                        }
                    )
                    
                    intersections_created += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {vtd.geoid} ∩ {cd.geoid}: {e}"))
            
            # Progress
            if i % 100 == 0:
                self.stdout.write(f"  Progress: {i}/{total_vtds} ({i/total_vtds*100:.1f}%)")
        
        self.stdout.write(self.style.SUCCESS(f"✅ Created {intersections_created} VTD-CD intersections"))

