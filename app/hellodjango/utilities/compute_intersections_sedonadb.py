"""
Compute Geographic Intersections with SedonaDB

Uses SedonaDB (in-process Arrow-based DB) for vectorized spatial operations
Much faster than sequential PostGIS queries!

Requirements:
    pip install 'apache-sedona[db]'

Usage:
    from utilities.compute_intersections_sedonadb import compute_county_cd_intersections
    
    result = compute_county_cd_intersections(year=2020)
    # Saves to: fixtures/county_cd_intersections_2020.parquet
"""

import geopandas as gpd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def compute_county_cd_intersections(year=2020, state_fips=None, output_dir="fixtures"):
    """
    Compute County-CD intersections using SedonaDB (vectorized!)
    
    Args:
        year: Census year (2010 or 2020)
        state_fips: Optional - compute for single state only
        output_dir: Where to save Parquet fixtures
    
    Returns:
        str: Path to output Parquet file
    """
    try:
        import sedona.db as sdb
    except ImportError:
        raise ImportError(
            "SedonaDB not installed. Install with: pip install 'apache-sedona[db]'"
        )
    
    logger.info(f"Computing County-CD intersections using SedonaDB (year={year})")
    
    # Connect to SedonaDB
    sd = sdb.connect()
    
    # Load counties from Django
    from locations.models.census.tiger import (
        United_States_Census_County,
        United_States_Census_Congressional_District
    )
    
    logger.info("Loading counties from Django...")
    counties_qs = United_States_Census_County.objects.filter(year=year)
    if state_fips:
        counties_qs = counties_qs.filter(statefp=state_fips)
    
    counties_gdf = gpd.GeoDataFrame.from_records(
        counties_qs.values('geoid', 'statefp', 'name', 'namelsad', 'aland'),
        geometry=list(counties_qs.values_list('geom', flat=True))
    )
    
    logger.info("Loading congressional districts from Django...")
    cds_qs = United_States_Census_Congressional_District.objects.filter(year=year)
    if state_fips:
        cds_qs = cds_qs.filter(statefp=state_fips)
    
    cds_gdf = gpd.GeoDataFrame.from_records(
        cds_qs.values('geoid', 'statefp', 'namelsad', 'aland'),
        geometry=list(cds_qs.values_list('geom', flat=True))
    )
    
    logger.info(f"Loaded {len(counties_gdf)} counties, {len(cds_gdf)} CDs")
    
    # Register in SedonaDB
    sd.register("counties", counties_gdf)
    sd.register("cds", cds_gdf)
    
    logger.info("Computing intersections with SedonaDB SQL (vectorized!)...")
    
    # Compute intersections with SQL (FAST - Arrow-based vectorized operations!)
    intersections_df = sd.sql("""
        SELECT 
            c.geoid AS county_geoid,
            c.statefp AS county_statefp,
            c.name AS county_name,
            c.namelsad AS county_namelsad,
            c.aland AS county_area,
            d.geoid AS cd_geoid,
            d.namelsad AS cd_namelsad,
            d.aland AS cd_area,
            ST_Intersection(c.geometry, d.geometry) AS intersection_geom,
            ST_Area(ST_Intersection(c.geometry, d.geometry)) AS intersection_area,
            (ST_Area(ST_Intersection(c.geometry, d.geometry)) / c.aland) * 100 AS pct_of_county,
            (ST_Area(ST_Intersection(c.geometry, d.geometry)) / d.aland) * 100 AS pct_of_cd,
            CASE 
                WHEN (ST_Area(ST_Intersection(c.geometry, d.geometry)) / c.aland) > 50.0 THEN true
                ELSE false
            END AS is_dominant
        FROM counties c
        JOIN cds d
        ON ST_Intersects(c.geometry, d.geometry)
        WHERE (ST_Area(ST_Intersection(c.geometry, d.geometry)) / c.aland) >= 1.0
           OR (ST_Area(ST_Intersection(c.geometry, d.geometry)) / d.aland) >= 1.0
    """).to_pandas()
    
    # Classify relationships
    def classify_relationship(row):
        if row['pct_of_county'] >= 99.9:
            return 'CD_IN_COUNTY'
        elif row['pct_of_cd'] >= 99.9:
            return 'COUNTY_IN_CD'
        else:
            return 'SPLIT'
    
    intersections_df['relationship'] = intersections_df.apply(classify_relationship, axis=1)
    intersections_df['year'] = year
    
    logger.info(f"✅ Computed {len(intersections_df)} intersections")
    
    # Save as Parquet fixture
    output_path = Path(output_dir) / f"county_cd_intersections_{year}.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    intersections_df.to_parquet(output_path)
    
    logger.info(f"✅ Saved to {output_path}")
    
    # Summary statistics
    split_counties = intersections_df.groupby('county_geoid').size()
    multi_cd_counties = split_counties[split_counties > 1]
    
    logger.info(f"Summary:")
    logger.info(f"  Total intersections: {len(intersections_df)}")
    logger.info(f"  Counties split between multiple CDs: {len(multi_cd_counties)}")
    logger.info(f"  Relationship breakdown:")
    logger.info(f"    {(intersections_df['relationship'] == 'COUNTY_IN_CD').sum()} counties fully within CDs")
    logger.info(f"    {(intersections_df['relationship'] == 'CD_IN_COUNTY').sum()} CDs fully within counties")
    logger.info(f"    {(intersections_df['relationship'] == 'SPLIT').sum()} split relationships")
    
    return str(output_path)


def compute_vtd_cd_intersections(year=2020, state_fips=None, output_dir="fixtures"):
    """
    Compute VTD-CD intersections using SedonaDB
    
    Args:
        year: Census year (2010 or 2020)
        state_fips: Optional - compute for single state only
        output_dir: Where to save Parquet fixtures
    
    Returns:
        str: Path to output Parquet file
    """
    try:
        import sedona.db as sdb
    except ImportError:
        raise ImportError(
            "SedonaDB not installed. Install with: pip install 'apache-sedona[db]'"
        )
    
    logger.info(f"Computing VTD-CD intersections using SedonaDB (year={year})")
    
    # Connect to SedonaDB
    sd = sdb.connect()
    
    # Load VTDs from Django
    from locations.models.census.tiger import (
        United_States_Census_Voter_Tabulation_District,
        United_States_Census_Congressional_District
    )
    
    logger.info("Loading VTDs from Django...")
    vtds_qs = United_States_Census_Voter_Tabulation_District.objects.filter(year=year)
    if state_fips:
        vtds_qs = vtds_qs.filter(statefp=state_fips)
    
    vtds_gdf = gpd.GeoDataFrame.from_records(
        vtds_qs.values('geoid', 'statefp', 'countyfp', 'namelsad', 'aland'),
        geometry=list(vtds_qs.values_list('geom', flat=True))
    )
    
    logger.info("Loading congressional districts from Django...")
    cds_qs = United_States_Census_Congressional_District.objects.filter(year=year)
    if state_fips:
        cds_qs = cds_qs.filter(statefp=state_fips)
    
    cds_gdf = gpd.GeoDataFrame.from_records(
        cds_qs.values('geoid', 'statefp', 'namelsad', 'aland'),
        geometry=list(cds_qs.values_list('geom', flat=True))
    )
    
    logger.info(f"Loaded {len(vtds_gdf)} VTDs, {len(cds_gdf)} CDs")
    
    # Register in SedonaDB
    sd.register("vtds", vtds_gdf)
    sd.register("cds", cds_gdf)
    
    logger.info("Computing intersections with SedonaDB SQL (vectorized!)...")
    
    # Compute intersections
    intersections_df = sd.sql("""
        SELECT 
            v.geoid AS vtd_geoid,
            v.statefp AS vtd_statefp,
            v.countyfp AS vtd_countyfp,
            v.namelsad AS vtd_namelsad,
            v.aland AS vtd_area,
            d.geoid AS cd_geoid,
            d.namelsad AS cd_namelsad,
            d.aland AS cd_area,
            ST_Intersection(v.geometry, d.geometry) AS intersection_geom,
            ST_Area(ST_Intersection(v.geometry, d.geometry)) AS intersection_area,
            (ST_Area(ST_Intersection(v.geometry, d.geometry)) / v.aland) * 100 AS pct_of_vtd,
            (ST_Area(ST_Intersection(v.geometry, d.geometry)) / d.aland) * 100 AS pct_of_cd,
            CASE 
                WHEN (ST_Area(ST_Intersection(v.geometry, d.geometry)) / v.aland) > 50.0 THEN true
                ELSE false
            END AS is_dominant
        FROM vtds v
        JOIN cds d
        ON ST_Intersects(v.geometry, d.geometry)
        WHERE (ST_Area(ST_Intersection(v.geometry, d.geometry)) / v.aland) >= 1.0
    """).to_pandas()
    
    intersections_df['year'] = year
    
    logger.info(f"✅ Computed {len(intersections_df)} VTD-CD intersections")
    
    # Save as Parquet fixture
    output_path = Path(output_dir) / f"vtd_cd_intersections_{year}.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    intersections_df.to_parquet(output_path)
    
    logger.info(f"✅ Saved to {output_path}")
    
    # Summary statistics
    split_vtds = intersections_df.groupby('vtd_geoid').size()
    multi_cd_vtds = split_vtds[split_vtds > 1]
    
    logger.info(f"Summary:")
    logger.info(f"  Total intersections: {len(intersections_df)}")
    logger.info(f"  VTDs split between multiple CDs: {len(multi_cd_vtds)}")
    logger.info(f"  Dominant assignments: {intersections_df['is_dominant'].sum()}")
    
    return str(output_path)


def load_intersection_fixtures(fixture_path, intersection_type='county-cd'):
    """
    Load pre-computed intersection fixtures into Django
    
    Args:
        fixture_path: Path to Parquet fixture file
        intersection_type: 'county-cd' or 'vtd-cd'
    
    Returns:
        int: Number of intersections loaded
    """
    import pyarrow.parquet as pq
    from django.db import transaction
    
    logger.info(f"Loading intersection fixtures from {fixture_path}")
    
    # Read Parquet
    df = pq.read_table(fixture_path).to_pandas()
    
    if intersection_type == 'county-cd':
        from locations.models.intersections import CountyCongressionalDistrictIntersection
        from locations.models.census.tiger import (
            United_States_Census_County,
            United_States_Census_Congressional_District
        )
        
        # Build FK lookups
        year = df['year'].iloc[0]
        county_lookup = {c.geoid: c for c in United_States_Census_County.objects.filter(year=year)}
        cd_lookup = {c.geoid: c for c in United_States_Census_Congressional_District.objects.filter(year=year)}
        
        # Create objects
        objects = []
        for _, row in df.iterrows():
            county = county_lookup.get(row['county_geoid'])
            cd = cd_lookup.get(row['cd_geoid'])
            
            if not county or not cd:
                continue
            
            objects.append(CountyCongressionalDistrictIntersection(
                county=county,
                cd=cd,
                year=row['year'],
                intersection_geom=row['intersection_geom'],
                intersection_area_sqm=int(row['intersection_area']),
                pct_of_county=round(row['pct_of_county'], 2),
                pct_of_cd=round(row['pct_of_cd'], 2),
                relationship=row['relationship'],
                is_dominant=row['is_dominant']
            ))
        
        # Bulk insert
        with transaction.atomic():
            CountyCongressionalDistrictIntersection.objects.bulk_create(
                objects,
                batch_size=1000,
                ignore_conflicts=True
            )
        
        logger.info(f"✅ Loaded {len(objects)} County-CD intersections")
        return len(objects)
    
    elif intersection_type == 'vtd-cd':
        # Similar for VTD-CD
        from locations.models.intersections import VTDCongressionalDistrictIntersection
        # ... (same pattern)
        pass


if __name__ == "__main__":
    """
    Standalone script for testing
    
    Usage:
        cd app/hellodjango
        python -c "from utilities.compute_intersections_sedonadb import *; compute_county_cd_intersections(2020)"
    """
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hellodjango.settings')
    django.setup()
    
    # Compute for California (test)
    result = compute_county_cd_intersections(year=2020, state_fips='06')
    print(f"✅ Fixture saved: {result}")

