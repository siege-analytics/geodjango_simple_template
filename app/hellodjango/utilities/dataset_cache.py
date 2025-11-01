"""
Dataset caching utilities using content hashing

Avoids re-downloading and re-cleaning datasets that haven't changed.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: Path, algorithm='sha256', chunk_size=8192) -> str:
    """
    Calculate hash of a file efficiently (streaming, doesn't load entire file)
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)
        chunk_size: Bytes to read at a time
        
    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_cache_manifest_path(data_dir: Path) -> Path:
    """Get path to cache manifest file for a dataset directory"""
    return data_dir / '.cache_manifest.json'


def load_cache_manifest(data_dir: Path) -> Dict[str, Any]:
    """
    Load cache manifest for a dataset
    
    Returns dict with:
        - source_hash: Hash of original downloaded file
        - cleaned_hash: Hash of cleaned file (if exists)
        - cleaned_path: Path to cleaned file
        - timestamp: When cache was created
    """
    manifest_path = get_cache_manifest_path(data_dir)
    
    if not manifest_path.exists():
        return {}
    
    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Cache manifest corrupted, ignoring: {e}")
        return {}


def save_cache_manifest(data_dir: Path, manifest_data: Dict[str, Any]):
    """Save cache manifest"""
    manifest_path = get_cache_manifest_path(data_dir)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    
    logger.info(f"Cache manifest saved: {manifest_path}")


def check_if_cleaning_needed(source_file: Path, data_dir: Path) -> tuple[bool, Optional[Path]]:
    """
    Check if dataset needs cleaning based on content hash
    
    Args:
        source_file: Path to original GPKG file
        data_dir: Directory containing dataset
        
    Returns:
        (needs_cleaning: bool, cached_clean_path: Optional[Path])
        
    If needs_cleaning is False, cached_clean_path will contain the path to use.
    """
    # Calculate hash of source file
    logger.info(f"Calculating hash of {source_file.name}...")
    current_hash = calculate_file_hash(source_file)
    logger.info(f"Source file hash: {current_hash[:16]}...")
    
    # Load cache manifest
    manifest = load_cache_manifest(data_dir)
    
    if not manifest:
        logger.info("No cache manifest found - cleaning needed")
        return True, None
    
    cached_hash = manifest.get('source_hash')
    cleaned_path_str = manifest.get('cleaned_path')
    
    if cached_hash != current_hash:
        logger.info(f"Hash mismatch - cleaning needed")
        logger.info(f"  Cached: {cached_hash[:16] if cached_hash else 'none'}...")
        logger.info(f"  Current: {current_hash[:16]}...")
        return True, None
    
    # Hash matches - check if cleaned file still exists
    if cleaned_path_str:
        cleaned_path = Path(cleaned_path_str)
        if cleaned_path.exists():
            logger.info(f"✅ Cache HIT - using cleaned file: {cleaned_path.name}")
            return False, cleaned_path
    
    logger.info("Hash matches but cleaned file missing - cleaning needed")
    return True, None


def update_cache_after_cleaning(
    source_file: Path,
    cleaned_file: Path,
    data_dir: Path
):
    """
    Update cache manifest after cleaning is complete
    
    Args:
        source_file: Original GPKG file
        cleaned_file: Cleaned GPKG file
        data_dir: Dataset directory
    """
    import datetime
    
    source_hash = calculate_file_hash(source_file)
    cleaned_hash = calculate_file_hash(cleaned_file)
    
    manifest = {
        'source_hash': source_hash,
        'source_file': str(source_file),
        'cleaned_hash': cleaned_hash,
        'cleaned_path': str(cleaned_file),
        'timestamp': datetime.datetime.now().isoformat(),
        'note': 'Content-based cache - safe to delete .cache_manifest.json to force re-clean'
    }
    
    save_cache_manifest(data_dir, manifest)
    logger.info(f"✅ Cache updated - future runs will skip cleaning if file unchanged")


def check_if_download_needed(
    url: str,
    target_file: Path,
    expected_hash: Optional[str] = None
) -> bool:
    """
    Check if file needs to be downloaded
    
    Args:
        url: Download URL
        target_file: Where file would be saved
        expected_hash: Expected SHA256 hash (optional)
        
    Returns:
        True if download needed, False if existing file is valid
    """
    if not target_file.exists():
        logger.info(f"File doesn't exist - download needed")
        return True
    
    if expected_hash:
        actual_hash = calculate_file_hash(target_file)
        if actual_hash == expected_hash:
            logger.info(f"✅ File exists with correct hash - skipping download")
            return False
        else:
            logger.info(f"File exists but hash mismatch - re-downloading")
            return True
    
    # No hash provided, just check existence
    logger.info(f"File exists, no hash to verify - using existing file")
    return False

