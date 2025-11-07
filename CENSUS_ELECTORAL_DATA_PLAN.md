# Census & Electoral Geographic Data Expansion Plan

**Date**: November 7, 2025  
**Purpose**: Comprehensive year-aware geographic units for political/social analysis

---

## Current State (Already Have!)

### Census TIGER Models ✅

**In `locations/models/census/tiger/`**:
1. ✅ `United_States_Census_State` - States
2. ✅ `United_States_Census_County` - Counties
3. ✅ `United_States_Census_Congressional_District` (CD) - US House districts
4. ✅ `United_States_Census_State_Legislative_District_Upper` (SLDU) - State senate
5. ✅ `United_States_Census_State_Legislative_District_Lower` (SLDL) - State house
6. ✅ `United_States_Census_Tract` - Census tracts
7. ✅ `United_States_Census_Tribal_Tract` (TT) - Tribal census tracts
8. ✅ `United_States_Census_Block_Group` - Block groups
9. ✅ `United_States_Census_Tabulation_Block` - Census blocks (smallest unit)

**All have**:
- `year` field (already year-aware!)
- `geom` field (MultiPolygon, SRID 4269)
- Census standard fields (statefp, geoid, namelsad, etc.)
- Area fields (aland, awater)
- Internal point (intptlat, intptlon)

---

## What's Missing

### 1. Additional Census Units

**Urban/Rural Classifications**:
- ❌ `United_States_Census_Urban_Area` - Urban areas (UAC)
- ❌ `United_States_Census_ZCTA` - ZIP Code Tabulation Areas
- ❌ `United_States_Census_Place` - Cities/towns (incorporated places)
- ❌ `United_States_Census_CBSA` - Metro/Micro Statistical Areas
- ❌ `United_States_Census_CSA` - Combined Statistical Areas

**School Districts**:
- ❌ `United_States_Census_School_District_Elementary`
- ❌ `United_States_Census_School_District_Secondary`
- ❌ `United_States_Census_School_District_Unified`

### 2. Voter Tabulation Districts (VTDs)

**NEW**: `Voter_Tabulation_District` (VTD)

**Sources**:
- Census TIGER (basic boundaries)
- Redistricting Data Hub (enhanced, precinct-level)
- State election boards (most detailed)

**Key fields**:
```python
class Voter_Tabulation_District(models.Model):
    # Identifiers
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    vtdst = models.CharField(max_length=6)  # VTD code
    geoid = models.CharField(max_length=11)  # State+County+VTD
    
    # Names
    name = models.CharField(max_length=100)  # VTD name
    namelsad = models.CharField(max_length=100)
    
    # Geography
    geom = models.MultiPolygonField(srid=4269)
    aland = models.BigIntegerField()
    awater = models.BigIntegerField()
    
    # Year (redistricting cycle)
    year = models.IntegerField()  # 2010, 2020, 2030
    
    # Enhanced fields (from RDH)
    precinct_name = models.CharField(max_length=200, null=True)
    precinct_code = models.CharField(max_length=50, null=True)
    
    # Electoral data (if available)
    registered_voters = models.IntegerField(null=True)
    
    # Relationships
    state = models.ForeignKey('United_States_Census_State', on_delete=models.CASCADE)
    county = models.ForeignKey('United_States_Census_County', on_delete=models.CASCADE)
```

### 3. Enhanced Addresses

**Current**: `locations/models/addresses.py` (basic model)

**Enhance with**:
```python
class Address(models.Model):
    # Current fields (keep)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    
    # NEW: Point geometry
    geom = models.PointField(srid=4326, null=True)
    
    # NEW: Geocoding metadata
    geocoded = models.BooleanField(default=False)
    geocode_quality = models.CharField(max_length=20, null=True)  # Exact, Interpolated, Approximate
    geocode_source = models.CharField(max_length=50, null=True)  # Census, Google, Nominatim
    geocoded_at = models.DateTimeField(null=True)
    
    # NEW: Census unit linkages (year-aware!)
    census_year = models.IntegerField(default=2020)
    
    # Census hierarchy (all ForeignKeys)
    state_unit = models.ForeignKey('United_States_Census_State', null=True, on_delete=models.SET_NULL)
    county_unit = models.ForeignKey('United_States_Census_County', null=True, on_delete=models.SET_NULL)
    tract_unit = models.ForeignKey('United_States_Census_Tract', null=True, on_delete=models.SET_NULL)
    block_group_unit = models.ForeignKey('United_States_Census_Block_Group', null=True, on_delete=models.SET_NULL)
    block_unit = models.ForeignKey('United_States_Census_Tabulation_Block', null=True, on_delete=models.SET_NULL)
    
    # Political units
    congressional_district = models.ForeignKey('United_States_Census_Congressional_District', null=True, on_delete=models.SET_NULL)
    state_leg_upper = models.ForeignKey('United_States_Census_State_Legislative_District_Upper', null=True, on_delete=models.SET_NULL)
    state_leg_lower = models.ForeignKey('United_States_Census_State_Legislative_District_Lower', null=True, on_delete=models.SET_NULL)
    vtd = models.ForeignKey('Voter_Tabulation_District', null=True, on_delete=models.SET_NULL)
    
    # Urban/Rural classification
    place = models.ForeignKey('United_States_Census_Place', null=True, on_delete=models.SET_NULL)
    zcta = models.ForeignKey('United_States_Census_ZCTA', null=True, on_delete=models.SET_NULL)
    
    # Computed method
    def assign_census_units(self, year=2020):
        """
        Use spatial join to assign all census units based on point geometry
        """
        pass
```

---

## Year Versioning Strategy

### The Challenge

**Census units change over time**:
- **Decennial**: States, counties (rare changes)
- **Decennial**: Blocks, block groups, tracts (major changes every 10 years)
- **Redistricting**: Congressional districts, state leg districts (every 10 years)
- **Continuous**: Places (cities incorporate/annex)
- **Annual**: ZCTAs (ZIP codes change)

### Our Strategy: Explicit Year Field

**Every model has `year` field**:
```python
class United_States_Census_Tract(models.Model):
    # ... fields ...
    year = models.IntegerField()  # 2000, 2010, 2020, 2030
    
    class Meta:
        unique_together = [['geoid', 'year']]  # Same GEOID can exist across years
        indexes = [
            models.Index(fields=['year', 'statefp']),
            models.Index(fields=['geoid', 'year'])
        ]
```

**Querying by year**:
```python
# Get 2020 tracts
tracts_2020 = United_States_Census_Tract.objects.filter(year=2020)

# Get tract for address (year-specific)
address.tract_unit = United_States_Census_Tract.objects.get(
    geom__contains=address.geom,
    year=2020
)

# Compare across years (track boundary changes)
tract_2010 = United_States_Census_Tract.objects.get(geoid='12345', year=2010)
tract_2020 = United_States_Census_Tract.objects.get(geoid='12345', year=2020)
# geoid same, but geom might differ!
```

---

## Data Sources & Fetch Commands

### Census TIGER (Primary Source)

**URL Pattern**:
```
https://www2.census.gov/geo/tiger/TIGER{YEAR}/{LAYER}/
```

**Layers**:
- `STATE/tl_{year}_us_state.zip` - States
- `COUNTY/tl_{year}_us_county.zip` - Counties (by state)
- `CD/tl_{year}_us_cd116.zip` - Congressional Districts (116th Congress = 2020)
- `TRACT/tl_{year}_{statefp}_tract.zip` - Tracts (by state)
- `BG/tl_{year}_{statefp}_bg.zip` - Block Groups (by state)
- `TABBLOCK20/tl_{year}_{statefp}_tabblock20.zip` - Blocks (by state, by county)
- `VTD/tl_{year}_{statefp}_vtd20.zip` - VTDs (by state)
- `PLACE/tl_{year}_{statefp}_place.zip` - Places (by state)
- `ZCTA520/tl_{year}_us_zcta520.zip` - ZCTAs (nationwide)

**Years Available**: 2000-2024 (varies by product)

### Redistricting Data Hub (Enhanced VTDs)

**URL**: https://redistrictingdatahub.org/

**Provides**:
- Enhanced VTD boundaries with election results
- Precinct-level data
- 2020 redistricting files
- State-specific corrections

### Management Command Pattern

```python
# locations/management/commands/fetch_census_units.py

class Command(BaseCommand):
    help = 'Fetch and load Census geographic units'
    
    def add_arguments(self, parser):
        parser.add_argument('--unit', type=str, required=True,
                          choices=['state', 'county', 'tract', 'blockgroup', 
                                   'block', 'cd', 'vtd', 'place', 'zcta'])
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument('--state', type=str, help='State FIPS (for state-specific layers)')
        parser.add_argument('--async', action='store_true', help='Run via Celery')
    
    def handle(self, *args, **options):
        unit = options['unit']
        year = options['year']
        state = options.get('state')
        
        if options.get('async'):
            # Delegate to Celery
            from locations.tasks import fetch_and_load_census_unit
            result = fetch_and_load_census_unit.delay(unit, year, state)
            self.stdout.write(f"Task queued: {result.id}")
        else:
            # Run synchronously
            self._fetch_and_load(unit, year, state)
```

---

## Implementation Plan

### Phase 1: Add Missing Census Models (1-2 hours)

**Create models** in `locations/models/census/tiger/`:

1. **`vtd.py`** - Voter Tabulation Districts
   ```python
   class United_States_Census_Voter_Tabulation_District(models.Model):
       # Standard Census fields
       statefp = models.CharField(max_length=2)
       countyfp = models.CharField(max_length=3)
       vtdst = models.CharField(max_length=6)
       geoid = models.CharField(max_length=11)
       name = models.CharField(max_length=100)
       namelsad = models.CharField(max_length=100)
       geom = models.MultiPolygonField(srid=4269)
       year = models.IntegerField()
       
       # Enhanced fields (optional, from RDH)
       precinct_name = models.CharField(max_length=200, null=True, blank=True)
       precinct_code = models.CharField(max_length=50, null=True, blank=True)
       
       class Meta:
           db_table = 'census_vtd'
           unique_together = [['geoid', 'year']]
           indexes = [
               models.Index(fields=['year', 'statefp']),
               models.Index(fields=['geoid', 'year'])
           ]
   ```

2. **`place.py`** - Incorporated Places
3. **`zcta.py`** - ZIP Code Tabulation Areas
4. **`cbsa.py`** - Metro/Micro Statistical Areas
5. **`urban_area.py`** - Urban Areas

### Phase 2: Create Unified Fetch Command (2-3 hours)

**`locations/management/commands/fetch_census_units.py`**

**Features**:
- Download from Census TIGER FTP
- Unzip and extract
- Use LayerMapping to load
- Handle state-by-state (for large layers)
- Support multiple years
- Optional Celery async

**Usage**:
```bash
# Fetch 2020 states (small, nationwide)
python manage.py fetch_census_units --unit state --year 2020

# Fetch 2020 counties (medium, nationwide)
python manage.py fetch_census_units --unit county --year 2020

# Fetch 2020 tracts for California (large, state-specific)
python manage.py fetch_census_units --unit tract --year 2020 --state 06

# Fetch 2020 VTDs for all states (via Celery)
python manage.py fetch_census_units --unit vtd --year 2020 --async

# Fetch multiple years
python manage.py fetch_census_units --unit cd --year 2010
python manage.py fetch_census_units --unit cd --year 2020
# Now have both 2010 and 2020 districts for comparison!
```

### Phase 3: Enhance Address Model (1-2 hours)

**Add to `locations/models/addresses.py`**:

1. **Point geometry** for spatial operations
2. **Geocoding metadata** (quality, source, timestamp)
3. **Year-aware Census linkages**
4. **Method to assign units** via spatial join

```python
class Address(models.Model):
    # Existing address fields...
    
    # NEW: Geometry
    geom = models.PointField(srid=4326, null=True, blank=True)
    
    # NEW: Geocoding
    geocoded = models.BooleanField(default=False)
    geocode_quality = models.CharField(max_length=20, null=True, blank=True)
    geocoded_at = models.DateTimeField(null=True, blank=True)
    
    # NEW: Census year for boundary assignment
    census_year = models.IntegerField(default=2020)
    
    # NEW: Census unit ForeignKeys (year-specific via query)
    state_fips = models.CharField(max_length=2, null=True)
    county_fips = models.CharField(max_length=5, null=True)
    tract_geoid = models.CharField(max_length=11, null=True)
    block_group_geoid = models.CharField(max_length=12, null=True)
    block_geoid = models.CharField(max_length=15, null=True)
    vtd_geoid = models.CharField(max_length=11, null=True)
    cd_geoid = models.CharField(max_length=4, null=True)
    
    # Methods
    def geocode_address(self):
        """Geocode address to lat/lon using Census Geocoder"""
        pass
    
    def assign_census_units(self, year=2020):
        """
        Spatial join to assign all census units for given year
        
        Uses PostGIS ST_Contains to find which units contain this point
        """
        from django.contrib.gis.db.models.functions import Distance
        
        if not self.geom:
            return False
        
        # State (by point-in-polygon)
        state = United_States_Census_State.objects.filter(
            geom__contains=self.geom,
            year=year
        ).first()
        
        if state:
            self.state_fips = state.statefp
            
            # County (within this state)
            county = United_States_Census_County.objects.filter(
                geom__contains=self.geom,
                statefp=state.statefp,
                year=year
            ).first()
            
            if county:
                self.county_fips = f"{state.statefp}{county.countyfp}"
                
                # Tract (within this county)
                tract = United_States_Census_Tract.objects.filter(
                    geom__contains=self.geom,
                    statefp=state.statefp,
                    countyfp=county.countyfp,
                    year=year
                ).first()
                
                if tract:
                    self.tract_geoid = tract.geoid
                    
                    # Block group (within this tract)
                    # ... and so on
        
        self.census_year = year
        self.save()
        return True
```

### Phase 4: Create Celery Tasks (1 hour)

**`locations/tasks.py`** (enhance existing)

**Add tasks**:
```python
@shared_task
def fetch_and_load_census_unit(unit_type, year, state_fips=None):
    """
    Fetch and load a Census unit type via Celery
    
    Args:
        unit_type: 'state', 'county', 'tract', etc.
        year: 2010, 2020, 2030
        state_fips: Optional state filter (for large layers)
    """
    pass

@shared_task
def geocode_addresses_batch(address_ids):
    """
    Geocode a batch of addresses using Census Geocoder
    """
    pass

@shared_task
def assign_census_units_to_addresses(year=2020):
    """
    Spatial join to assign census units to all geocoded addresses
    """
    pass
```

### Phase 5: Create Redistricting Data Hub Fetcher (1-2 hours)

**`locations/management/commands/fetch_rdh_vtds.py`**

**Features**:
- Download from RDH API/downloads
- Enhanced VTD boundaries with precincts
- Load to VTD model with precinct fields
- Handle state-by-state

**Usage**:
```bash
python manage.py fetch_rdh_vtds --year 2020 --state CA
```

---

## Data Volume Estimates

### Nationwide, Single Year

| Unit | File Size | Record Count | Load Time |
|---|---|---|---|
| States | 5 MB | 50 | 1 min |
| Counties | 50 MB | 3,200 | 5 min |
| Congressional Districts | 30 MB | 435 | 3 min |
| State Leg Upper | 100 MB | ~2,000 | 10 min |
| State Leg Lower | 150 MB | ~5,000 | 15 min |
| Tracts | 500 MB | ~85,000 | 30 min |
| Block Groups | 800 MB | ~240,000 | 60 min |
| Blocks | **5 GB** | **11M** | **8 hours** |
| VTDs | 600 MB | ~180,000 | 45 min |
| Places | 200 MB | ~30,000 | 15 min |
| ZCTAs | 350 MB | ~33,000 | 20 min |

**Total Single Year**: ~8 GB, ~12 hours to load all units

### Multiple Years (2010, 2020)

**Total**: ~16 GB, ~24 hours

---

## Recommended Implementation Order

### Immediate (Essential for FEC Analysis)

1. **VTD Model + Fetch Command** (2-3 hours)
   - Most important for voter analysis
   - Links to precincts
   - Moderate size (~600 MB)

2. **Enhanced Address Model** (1 hour)
   - Geocoding support
   - Census unit linkage
   - Essential for donor analysis

3. **Address Geocoding Command** (1 hour)
   - Batch geocode addresses
   - Census Geocoder API
   - Assign census units

### Near-term (Useful)

4. **Place Model + Fetch** (1 hour)
   - Cities/towns for donor analysis
   - "Donations from NYC" queries

5. **ZCTA Model + Fetch** (1 hour)
   - ZIP code geography
   - Donor geographic clustering

### Later (Nice to Have)

6. **CBSA/CSA Models** - Metro areas
7. **Urban Area Models** - Urban/rural classification
8. **School District Models** - Education district analysis

---

## Use Cases Enabled

### FEC + Census Integration

**Donor Geography**:
```python
# Get all donations from a specific Congressional District
from fec.models import Transaction, Individual
from locations.models import Address

# Find donors in CA-12 (San Francisco)
ca_12_addresses = Address.objects.filter(
    congressional_district__geoid='0612',
    census_year=2020
)

donations_from_ca_12 = Transaction.objects.filter(
    contributor_address__in=ca_12_addresses,
    transaction_type='DON'
).aggregate(total=Sum('amount'))

# Result: $XX million from CA-12 to Biden 2020
```

**Voter Registration + Fundraising**:
```python
# Get VTD with high voter registration but low donations
from locations.models import Voter_Tabulation_District

vtds = Voter_Tabulation_District.objects.filter(
    year=2020,
    registered_voters__gt=10000
)

for vtd in vtds:
    # Find addresses in this VTD
    addresses_in_vtd = Address.objects.filter(
        vtd=vtd,
        census_year=2020
    )
    
    # Count donations from these addresses
    donations = Transaction.objects.filter(
        contributor_address__in=addresses_in_vtd
    ).count()
    
    # Calculate donation rate
    donation_rate = donations / vtd.registered_voters
    
    # Identify untapped districts (high registration, low donations)
```

**Rural vs Urban Fundraising**:
```python
# Compare urban vs rural donation patterns
from django.db.models import Q

# Urban donors (in places)
urban_addresses = Address.objects.filter(place__isnull=False)
urban_donations = Transaction.objects.filter(
    contributor_address__in=urban_addresses
).aggregate(total=Sum('amount'), avg=Avg('amount'))

# Rural donors (not in places)
rural_addresses = Address.objects.filter(place__isnull=True)
rural_donations = Transaction.objects.filter(
    contributor_address__in=rural_addresses
).aggregate(total=Sum('amount'), avg=Avg('amount'))

# Comparison shows donation patterns by urbanicity
```

---

## Implementation Sequence

### Step 1: VTD Model (Most Important)

```bash
# 1. Create model
vi app/hellodjango/locations/models/census/tiger/vtd.py

# 2. Add to __init__.py
echo "from .vtd import *" >> app/hellodjango/locations/models/census/tiger/__init__.py

# 3. Create migration
docker exec geodjango_webserver bash -c "cd hellodjango && python manage.py makemigrations locations"

# 4. Run migration
docker exec geodjango_webserver bash -c "cd hellodjango && python manage.py migrate locations"

# 5. Create fetch command
vi app/hellodjango/locations/management/commands/fetch_census_vtds.py

# 6. Test fetch (one state)
docker exec geodjango_webserver bash -c "cd hellodjango && python manage.py fetch_census_vtds --year 2020 --state 06"
```

### Step 2: Enhanced Address Model

```bash
# 1. Update model
vi app/hellodjango/locations/models/addresses.py

# 2. Create migration
docker exec geodjango_webserver bash -c "cd hellodjango && python manage.py makemigrations locations"

# 3. Create geocoding command
vi app/hellodjango/locations/management/commands/geocode_addresses.py

# 4. Test geocoding
docker exec geodjango_webserver bash -c "cd hellodjango && python manage.py geocode_addresses --limit 100"
```

### Step 3: Additional Units (As Needed)

Repeat for: Place, ZCTA, Urban Area, School Districts

---

## Questions for You

Before I start implementing:

1. **Priority order**: 
   - VTDs first? (most important for voter analysis)
   - Or address enhancement first? (enables donor geography immediately)
   
2. **Year coverage**:
   - Just 2020? (current boundaries)
   - 2010 + 2020? (track redistricting changes)
   - All years 2000-2024? (complete history)

3. **Scope**:
   - Start with VTD + Address only? (focused)
   - Or all missing units at once? (comprehensive)

4. **Where to build**:
   - In `geodjango_simple_template` (template for everyone)
   - Or in `socialwarehouse` first (test, then push to GST)
   - Or both simultaneously?

**What would you like me to start with?**

