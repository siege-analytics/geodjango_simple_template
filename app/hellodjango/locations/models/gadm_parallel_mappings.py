"""
Parallel-load mappings for GADM data

These mappings load to string fields instead of FK fields,
allowing all 6 layers to load in parallel without FK dependencies.

After parallel load completes, run populate_gadm_foreign_keys()
to resolve GID strings → actual FK relationships.
"""

# Admin Level 1 - Parallel load mapping (no FK resolution)
admin_level_1_mapping_parallel = {
    "gid_0_string": "GID_0",  # Load to string field, not FK
    "country": "COUNTRY",
    "gid_1": "GID_1",
    "name_1": "NAME_1",
    "varname_1": "VARNAME_1",
    "nl_name_1": "NL_NAME_1",
    "type_1": "TYPE_1",
    "engtype_1": "ENGTYPE_1",
    "cc_1": "CC_1",
    "hasc_1": "HASC_1",
    "iso_1": "ISO_1",
    "geom": "MULTIPOLYGON",
}

# Admin Level 2 - Parallel load mapping
admin_level_2_mapping_parallel = {
    "gid_0_string": "GID_0",
    "country": "COUNTRY",
    "gid_1_string": "GID_1",
    "name_1": "NAME_1",
    "nl_name_1": "NL_NAME_1",
    "gid_2": "GID_2",
    "name_2": "NAME_2",
    "varname_2": "VARNAME_2",
    "nl_name_2": "NL_NAME_2",
    "type_2": "TYPE_2",
    "engtype_2": "ENGTYPE_2",
    "cc_2": "CC_2",
    "hasc_2": "HASC_2",
    "geom": "MULTIPOLYGON",
}

# Admin Level 3 - Parallel load mapping
admin_level_3_mapping_parallel = {
    "gid_0_string": "GID_0",
    "country": "COUNTRY",
    "gid_1_string": "GID_1",
    "name_1": "NAME_1",
    "nl_name_1": "NL_NAME_1",
    "gid_2_string": "GID_2",
    "name_2": "NAME_2",
    "nl_name_2": "NL_NAME_2",
    "gid_3": "GID_3",
    "name_3": "NAME_3",
    "varname_3": "VARNAME_3",
    "nl_name_3": "NL_NAME_3",
    "type_3": "TYPE_3",
    "engtype_3": "ENGTYPE_3",
    "cc_3": "CC_3",
    "hasc_3": "HASC_3",
    "geom": "MULTIPOLYGON",
}

# Admin Level 4 - Parallel load mapping  
admin_level_4_mapping_parallel = {
    "gid_4": "GID_4",
    "gid_0_string": "GID_0",
    "country": "COUNTRY",
    "gid_1_string": "GID_1",
    "name_1": "NAME_1",
    "gid_2_string": "GID_2",
    "name_2": "NAME_2",
    "gid_3_string": "GID_3",
    "name_3": "NAME_3",
    "name_4": "NAME_4",
    "varname_4": "VARNAME_4",
    "type_4": "TYPE_4",
    "engtype_4": "ENGTYPE_4",
    "cc_4": "CC_4",
    "geom": "MULTIPOLYGON",
}

# Admin Level 5 - Parallel load mapping
admin_level_5_mapping_parallel = {
    "gid_0_string": "GID_0",
    "country": "COUNTRY",
    "gid_1_string": "GID_1",
    "name_1": "NAME_1",
    "gid_2_string": "GID_2",
    "name_2": "NAME_2",
    "gid_3_string": "GID_3",
    "name_3": "NAME_3",
    "gid_4_string": "GID_4",
    "name_4": "NAME_4",
    "gid_5": "GID_5",
    "name_5": "NAME_5",
    "type_5": "TYPE_5",
    "engtype_5": "ENGTYPE_5",
    "cc_5": "CC_5",
    "geom": "MULTIPOLYGON",
}

