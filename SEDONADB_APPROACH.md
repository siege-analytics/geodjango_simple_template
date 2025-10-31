# SedonaDB for GADM Preprocessing - Analysis

**Date**: October 31, 2025  
**Current**: GeoPandas (single-threaded, slow on large datasets)  
**Proposed**: Apache Sedona (distributed Spark processing)

## The Problem with GeoPandas

### Current Preprocessing with GeoPandas

```python
# Single-threaded, processes layers sequentially
for layer in [ADM_0, ADM_1, ADM_2, ADM_3, ADM_4, ADM_5]:
    gdf = gpd.read_file(source_gpkg, layer=layer)  # Load into memory
    for col in columns:
        gdf[col] = gdf[col].replace("NA", np.nan)   # In-memory operation
    gdf.to_file(output_gpkg, layer=layer)          # Write to disk
```

**Issues**:
1. **Single-threaded**: One CPU core, no parallelization
2. **Memory-intensive**: Loads entire layer into RAM
3. **Slow I/O**: Reads/writes large geopackages sequentially
4. **Time**: ~8-10 minutes even with bug fix

**Layer sizes**:
- ADM_0: 263 records (fast)
- ADM_1: 3,662 records (fast)
- ADM_2: 47,217 records (moderate)
- ADM_3: 144,193 records (slow)
- ADM_4: 153,410 records (slow)
- ADM_5: 51,427 records (moderate)

## Apache Sedona/SedonaDB Approach

### What is Sedona?

- **Apache Sedona**: Geospatial extension for Apache Spark
- **Distributed processing**: Uses all CPU cores + can scale to clusters
- **Optimized for big data**: Handles millions of geometries efficiently
- **SQL interface**: Can use Spark SQL or DataFrame API

### How It Would Work

```python
from pyspark.sql import SparkSession
from sedona.register import SedonaRegistrator
from sedona.utils import SedonaKryoRegistrator, KryoSerializer

# Initialize Spark with Sedona
spark = SparkSession.builder \
    .appName("GADM_Processing") \
    .config("spark.serializer", KryoSerializer.getName) \
    .config("spark.kryo.registrator", SedonaKryoRegistrator.getName) \
    .config("spark.sql.extensions", "org.apache.sedona.sql.SedonaSqlExtensions") \
    .getOrCreate()

SedonaRegistrator.registerAll(spark)

# Read GADM layers (distributed across Spark partitions)
for layer_name in ['ADM_0', 'ADM_1', ..., 'ADM_5']:
    df = spark.read.format("geoparquet").load(f"gadm_{layer_name}.gpkg")
    
    # Replace 'NA' with NULL (distributed across all cores!)
    df = df.replace("NA", None, subset=['GID_0', 'GID_1', ...])
    
    # Write output (parallel writes)
    df.write.format("geoparquet").save(f"gadm_{layer_name}_fixed.parquet")
```

**Benefits**:
- **Parallel processing**: All CPU cores utilized
- **Distributed**: Can scale to multiple machines
- **Faster**: 8-10 minutes → 1-2 minutes (estimated)

## Integration Options

### Option 1: Sedona in Docker (Recommended)

Add Sedona to the stack:

```yaml
# compose.yaml
services:
  spark_master:
    image: apache/sedona:latest
    environment:
      SPARK_MODE: master
    ports:
      - "8080:8080"  # Spark UI
      - "7077:7077"  # Spark master
    
  spark_worker:
    image: apache/sedona:latest
    environment:
      SPARK_MODE: worker
      SPARK_MASTER_URL: spark://spark_master:7077
    depends_on:
      - spark_master
    deploy:
      replicas: 3  # 3 Spark workers
```

**Celery task**:
```python
@shared_task(bind=True)
def preprocess_gadm_with_sedona(self, source_gpkg):
    """Use Sedona/Spark for distributed preprocessing"""
    
    # Connect to Spark cluster
    spark = SparkSession.builder \
        .master("spark://spark_master:7077") \
        .appName("GADM_Preprocessing") \
        .getOrCreate()
    
    SedonaRegistrator.registerAll(spark)
    
    # Process all layers in parallel across Spark workers
    for i, layer in enumerate(['ADM_0', ...]):
        df = spark.read.format("geo").load(source_gpkg, layer=i)
        df = df.replace("NA", None, subset=['GID_0', 'GID_1', ...])
        df.write.format("parquet").save(f"output/{layer}.parquet")
    
    return {"status": "success", "layers_preprocessed": 6}
```

### Option 2: Sedona within Celery Workers

Install Sedona + PySpark in webserver image:

```dockerfile
# docker/requirements.txt
apache-sedona
pyspark
```

**Use local Spark session** (multi-threaded, not distributed):
```python
spark = SparkSession.builder \
    .master("local[*]") \  # Use all cores on this machine
    .appName("GADM") \
    .getOrCreate()
```

**Pros**: No additional containers  
**Cons**: Limited to one machine's cores

### Option 3: Hybrid Approach (Best?)

```python
@shared_task(bind=True)
def preprocess_all_gadm_layers_spark(self):
    """
    Use Sedona to preprocess ALL 6 layers in parallel on Spark
    Returns paths to fixed parquet files
    """
    spark = SparkSession.builder.master("spark://spark_master:7077").getOrCreate()
    SedonaRegistrator.registerAll(spark)
    
    # Process all 6 layers in parallel on Spark cluster
    for i, layer in enumerate(['ADM_0', 'ADM_1', ..., 'ADM_5']):
        df = spark.read.format("geo").load(source_gpkg, layer=i)
        df = df.replace("NA", None)
        df.write.parquet(f"/data/gadm/{layer}_fixed.parquet")
    
    return {"preprocessed_layers": 6}

@shared_task(bind=True)  
def load_gadm_layer_from_parquet(self, layer_index, parquet_path):
    """
    Load preprocessed parquet to PostGIS
    These CAN run in parallel on Celery workers!
    """
    # Use GeoPandas to read parquet and load via LayerMapping
    gdf = gpd.read_parquet(parquet_path)
    # ... LayerMapping load
```

**Workflow**:
```
Spark preprocessing (all 6 layers parallel): 1-2 min
    ↓
Celery group (6 parallel PostGIS loads): 2-3 min
    ↓
FK population: 2-3 min

Total: 5-8 minutes (vs 25+ current)
```

## Performance Comparison

| Approach | Preprocessing | Loading | FK Population | Total |
|----------|--------------|---------|---------------|-------|
| **Current (GeoPandas, sequential)** | 20-30 min | 5-8 min | N/A | 25-38 min |
| **With bug fix (GeoPandas)** | 8-10 min | 5-8 min | N/A | 13-18 min |
| **Pipelined (GeoPandas)** | 6-7 min | 3-4 min | 2-3 min | 11-14 min |
| **Sedona + Celery (proposed)** | 1-2 min | 2-3 min | 2-3 min | **5-8 min** |

## Implementation Plan

### Phase 1: Add Sedona to Stack
1. Add Spark/Sedona services to compose.yaml
2. Update requirements.txt with apache-sedona
3. Test Sedona connectivity from Celery tasks

### Phase 2: Create Sedona Preprocessing Task
1. Write `preprocess_gadm_with_sedona()` task
2. Test preprocessing all 6 layers with Spark
3. Verify output parquet files

### Phase 3: Integrate with Pipeline
1. Chain: Sedona preprocess → 6 parallel PostGIS loads → FK population
2. Test end-to-end
3. Benchmark against GeoPandas approach

### Phase 4: Generalize Pattern
1. Create reusable Sedona preprocessing for other datasets
2. Document the pattern
3. Apply to Census TIGER data

## Questions Before Implementation

1. **Spark cluster size**: How many Spark workers? (Start with 2-3)
2. **Memory allocation**: GADM is ~500MB uncompressed - 2GB per worker?
3. **Output format**: Parquet or GeoParquet for intermediate files?
4. **Integration point**: Separate service or embed in Celery workers?

## Recommended Approach

**Start with Option 3 (Hybrid)**:
- Separate Spark cluster for preprocessing (distributed across 3 workers)
- Celery workers for PostGIS loading (uses existing infrastructure)
- Best of both: Distributed preprocessing + familiar Celery orchestration

---

**Next Steps**: 
1. Wait for current pipelined test to complete (benchmark)
2. Add Sedona/Spark services to compose.yaml
3. Implement Sedona preprocessing task
4. Test and compare performance

**Expected Gain**: 13-18 min → 5-8 min (60-70% faster)

