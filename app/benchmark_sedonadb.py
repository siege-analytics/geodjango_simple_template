#!/usr/bin/env python
"""
Benchmark: SedonaDB vs GeoPandas for GADM preprocessing

Tests the core operation: replacing 'NA' strings with NULL in GID columns
"""

import time
import geopandas as gpd
import pandas as pd
import numpy as np

# Path to GADM data
GADM_PATH = '/usr/src/app/data/spatial/vector/gadm_410-levels/gadm_410-levels.gpkg'

def benchmark_geopandas(layer_index=0):
    """Current approach: GeoPandas with NumPy"""
    print(f"\n{'='*60}")
    print("GEOPANDAS APPROACH")
    print(f"{'='*60}")
    
    start = time.time()
    
    # Read
    read_start = time.time()
    gdf = gpd.read_file(GADM_PATH, layer=layer_index)
    read_time = time.time() - read_start
    print(f"✓ Read {len(gdf)} rows in {read_time:.2f}s")
    
    # Transform
    transform_start = time.time()
    columns_to_fix = ['GID_0', 'GID_1', 'GID_2', 'GID_3', 'GID_4', 'GID_5']
    for col in columns_to_fix:
        if col in gdf.columns:
            gdf[col] = gdf[col].replace("NA", np.nan)
    transform_time = time.time() - transform_start
    print(f"✓ Fixed NA values in {transform_time:.2f}s")
    
    # Write to Parquet
    write_start = time.time()
    gdf.to_parquet('/tmp/gadm_geopandas.parquet')
    write_time = time.time() - write_start
    print(f"✓ Wrote Parquet in {write_time:.2f}s")
    
    total = time.time() - start
    print(f"\n📊 TOTAL: {total:.2f}s")
    print(f"   Breakdown: Read={read_time:.2f}s, Transform={transform_time:.2f}s, Write={write_time:.2f}s")
    
    return {
        'total': total,
        'read': read_time,
        'transform': transform_time,
        'write': write_time,
        'rows': len(gdf)
    }


def benchmark_sedonadb(layer_index=0):
    """SedonaDB approach: Arrow + DataFusion"""
    print(f"\n{'='*60}")
    print("SEDONADB APPROACH")
    print(f"{'='*60}")
    
    import sedona.db as sdb
    import pyarrow as pa
    
    start = time.time()
    
    # Read
    read_start = time.time()
    gdf = gpd.read_file(GADM_PATH, layer=layer_index)
    read_time = time.time() - read_start
    print(f"✓ Read {len(gdf)} rows in {read_time:.2f}s")
    
    # Transform with SedonaDB
    transform_start = time.time()
    
    # Separate geometry
    geom_col = gdf.geometry
    crs = gdf.crs
    attrs = gdf.drop(columns=['geometry'])
    
    # Convert to Arrow
    arrow_table = pa.Table.from_pandas(attrs)
    
    # SedonaDB processing
    sd = sdb.connect()
    sd.register("gadm_raw", arrow_table)
    
    # Vectorized SQL transformation
    fixed_df = sd.sql("""
        SELECT 
            CASE WHEN GID_0 = 'NA' THEN NULL ELSE GID_0 END as GID_0,
            CASE WHEN GID_1 = 'NA' THEN NULL ELSE GID_1 END as GID_1,
            CASE WHEN GID_2 = 'NA' THEN NULL ELSE GID_2 END as GID_2,
            CASE WHEN GID_3 = 'NA' THEN NULL ELSE GID_3 END as GID_3,
            CASE WHEN GID_4 = 'NA' THEN NULL ELSE GID_4 END as GID_4,
            CASE WHEN GID_5 = 'NA' THEN NULL ELSE GID_5 END as GID_5,
            *
        FROM gadm_raw
    """).to_pandas()
    
    # Add geometry back
    result_gdf = gpd.GeoDataFrame(fixed_df, geometry=geom_col, crs=crs)
    
    transform_time = time.time() - transform_start
    print(f"✓ Fixed NA values with SedonaDB in {transform_time:.2f}s")
    
    # Write to Parquet
    write_start = time.time()
    result_gdf.to_parquet('/tmp/gadm_sedonadb.parquet')
    write_time = time.time() - write_start
    print(f"✓ Wrote Parquet in {write_time:.2f}s")
    
    total = time.time() - start
    print(f"\n📊 TOTAL: {total:.2f}s")
    print(f"   Breakdown: Read={read_time:.2f}s, Transform={transform_time:.2f}s, Write={write_time:.2f}s")
    
    return {
        'total': total,
        'read': read_time,
        'transform': transform_time,
        'write': write_time,
        'rows': len(result_gdf)
    }


def main():
    print("\n" + "="*60)
    print("BENCHMARK: SedonaDB vs GeoPandas")
    print("Operation: Replace 'NA' strings with NULL in GADM data")
    print("="*60)
    
    # Test on Admin_Level_4 (largest layer with most NA values)
    layer_index = 4
    
    print(f"\nTesting on layer {layer_index} (Admin_Level_4)")
    
    # Run GeoPandas
    gpd_results = benchmark_geopandas(layer_index)
    
    # Run SedonaDB
    sdb_results = benchmark_sedonadb(layer_index)
    
    # Comparison
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    
    speedup_total = gpd_results['total'] / sdb_results['total']
    speedup_transform = gpd_results['transform'] / sdb_results['transform']
    
    print(f"\nRows processed: {gpd_results['rows']:,}")
    print(f"\nTotal Time:")
    print(f"  GeoPandas: {gpd_results['total']:.2f}s")
    print(f"  SedonaDB:  {sdb_results['total']:.2f}s")
    print(f"  Speedup:   {speedup_total:.2f}×")
    
    print(f"\nTransform Time (core operation):")
    print(f"  GeoPandas: {gpd_results['transform']:.2f}s")
    print(f"  SedonaDB:  {sdb_results['transform']:.2f}s")
    print(f"  Speedup:   {speedup_transform:.2f}×")
    
    if speedup_total > 1.5:
        print(f"\n✅ SedonaDB is {speedup_total:.1f}× faster - WORTH IT!")
    elif speedup_total > 1.1:
        print(f"\n⚠️  SedonaDB is {speedup_total:.1f}× faster - marginal improvement")
    else:
        print(f"\n❌ SedonaDB is NOT faster - stick with GeoPandas")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

