# SedonaDB Integration for GADM Preprocessing

**Date**: October 31, 2025  
**Reference**: [Apache SedonaDB](https://github.com/apache/sedona-db)

## What is SedonaDB?

**SedonaDB** is a single-node analytical database with geospatial as a first-class citizen:
- Built on **Apache Arrow** + **Apache DataFusion** (not Spark!)
- **Single-node** (no cluster needed - perfect for our use case)
- **10-100× faster** than GeoPandas for large datasets
- **In-process**: Runs within Python - can use in Celery workers directly
- Supports GeoParquet, Shapefile, GeoJSON, all GeoPandas formats

## Why SedonaDB > Apache Sedona for Our Use Case

| Feature | Apache Sedona (Spark) | SedonaDB | Our Need |
|---------|----------------------|----------|----------|
| **Architecture** | Distributed cluster | Single-node | ✅ Single machine |
| **Setup** | Complex (Spark cluster) | Simple (pip install) | ✅ Simple |
| **Resources** | High (multiple JVMs) | Low (one process) | ✅ Resource-efficient |
| **Speed** | Very fast (distributed) | Very fast (Arrow) | ✅ Either works |
| **Integration** | Separate service | In-process | ✅ **In Celery workers!** |

**Winner**: SedonaDB - simpler, lighter, integrates directly into Celery workers

## Current GeoPandas Bottleneck

```python
# Single-threaded, slow
gdf = gpd.read_file(source_gpkg, layer=layer)        # Slow
gdf[col] = gdf[col].replace("NA", np.nan)            # Single-threaded
gdf.to_file(output_gpkg, driver="GPKG", layer=layer) # Slow I/O
```

**Time for GADM**: ~8-10 minutes (even with bug fix)

## SedonaDB Approach

```python
import sedona.db as sdb

# Connect to SedonaDB (in-process, fast)
sd = sdb.connect()

# Read GADM layer (uses Arrow, vectorized)
sd.sql(f"CREATE VIEW gadm_layer AS SELECT * FROM read_parquet('gadm_layer_{i}.parquet')")

# Replace NA with NULL (vectorized, parallel)
result = sd.sql("""
    SELECT 
        CASE WHEN GID_0 = 'NA' THEN NULL ELSE GID_0 END as GID_0,
        CASE WHEN GID_1 = 'NA' THEN NULL ELSE GID_1 END as GID_1,
        geometry
    FROM gadm_layer
""")

# Write output (Arrow-optimized)
result.write_parquet(f"gadm_layer_{i}_fixed.parquet")
```

**Estimated time**: 8-10 minutes → **1-2 minutes** (5-10× faster)

## Integration into Celery Tasks

### Install SedonaDB

```dockerfile
# docker/requirements.txt
apache-sedona[db]
```

### Update Preprocessing Task

```python
# locations/tasks_gadm_pipeline.py

@shared_task(bind=True)
def preprocess_single_gadm_layer_sedonadb(self, layer_index, layer_name, source_gpkg):
    """
    Preprocess ONE GADM layer using SedonaDB (Arrow-based, fast)
    """
    import sedona.db as sdb
    
    start_time = time.time()
    
    try:
        logger.info(f"[Worker {self.request.hostname}] SedonaDB preprocessing {layer_name}")
        
        # Connect to SedonaDB
        sd = sdb.connect()
        
        # Read the specific GADM layer
        # SedonaDB can read directly from GeoPackage
        sd.sql(f"""
            CREATE VIEW gadm_raw AS 
            SELECT * FROM ST_Read('{source_gpkg}', layer='{layer_index}')
        """)
        
        # Replace 'NA' strings with NULL for all GID columns
        # This is vectorized and very fast with Arrow
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
        """)
        
        # Write to GeoParquet (fast Arrow format)
        output_path = f"/data/gadm/{layer_name}_fixed.parquet"
        fixed_df.write_parquet(output_path)
        
        elapsed = time.time() - start_time
        logger.info(f"[Worker {self.request.hostname}] SedonaDB preprocessed {layer_name} in {elapsed:.2f}s")
        
        return {
            'status': 'success',
            'layer_name': layer_name,
            'output_path': output_path,
            'elapsed_seconds': round(elapsed, 2),
            'engine': 'SedonaDB'
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[Worker {self.request.hostname}] SedonaDB preprocessing failed: {e}")
        return {'status': 'error', 'error': str(e)}
```

### Load from GeoParquet

```python
@shared_task(bind=True)
def load_gadm_layer_from_geoparquet(self, preprocess_result):
    """
    Load preprocessed GeoParquet to PostGIS
    SedonaDB → GeoPandas → LayerMapping
    """
    import geopandas as gpd
    
    # Read GeoParquet (fast with Arrow)
    gdf = gpd.read_parquet(preprocess_result['output_path'])
    
    # Load to PostGIS via LayerMapping
    lm = LayerMapping(model_class, gdf, mapping, ...)
    lm.save()
```

## Performance Expectations

### Current (GeoPandas with bug fix)
```
Preprocessing: 8-10 min (single-threaded)
Loading: 5-8 min
Total: 13-18 min
```

### With SedonaDB
```
Preprocessing (SedonaDB, vectorized): 1-2 min
Loading (GeoPandas → PostGIS): 3-4 min  
FK Population: 2-3 min
Total: 6-9 min (50-60% faster!)
```

### With SedonaDB + Pipelined
```
All 3 workers run chains in parallel:
- Worker 1: preprocess ADM_0 (30s) → load (10s) → preprocess ADM_3 (1min) → load (30s)
- Worker 2: preprocess ADM_1 (30s) → load (10s) → preprocess ADM_4 (1min) → load (30s)
- Worker 3: preprocess ADM_2 (45s) → load (20s) → preprocess ADM_5 (30s) → load (10s)

Longest chain: ~2.5 minutes
FK Population: 2-3 minutes
Total: ~5 minutes (80% faster!)
```

## Implementation Steps

### 1. Add SedonaDB Dependency

```bash
# docker/requirements.txt
apache-sedona[db]  # Includes Arrow, DataFusion, geospatial functions
```

### 2. Update Docker Image

```bash
make build  # Rebuild with SedonaDB
```

### 3. Test SedonaDB Connection

```python
# In Django shell
import sedona.db as sdb
sd = sdb.connect()
result = sd.sql("SELECT ST_Point(0, 1) as geom")
result.show()  # Should work
```

### 4. Create SedonaDB Preprocessing Task

Create `tasks_gadm_sedonadb.py` with SedonaDB-based preprocessing

### 5. Add `--sedonadb` Flag

```bash
python manage.py fetch_and_load_standard_spatial_data gadm --async --sedonadb
```

## Advantages Over Previous Approaches

✅ **No Spark cluster** - Simpler infrastructure  
✅ **In-process** - Runs in Celery workers directly  
✅ **Vectorized** - Arrow-based, uses SIMD instructions  
✅ **Fast I/O** - Arrow/Parquet are optimized formats  
✅ **Still parallel** - Each worker preprocesses independently  
✅ **Compatible** - Outputs GeoParquet that GeoPandas can read

## Next Steps

1. ✅ Document SedonaDB approach
2. Add `apache-sedona[db]` to requirements.txt
3. Rebuild Docker image
4. Test SedonaDB connectivity
5. Implement SedonaDB preprocessing task
6. Benchmark vs GeoPandas
7. Roll out to production

---

**Current**: GeoPandas (13-18 min)  
**Proposed**: SedonaDB + pipelined Celery (5-6 min)  
**Expected Speedup**: 65-70% faster  
**Complexity**: Low (no cluster, just pip install)

