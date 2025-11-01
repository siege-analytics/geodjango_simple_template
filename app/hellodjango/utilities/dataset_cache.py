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
    Check if dataset needs cleaning using FAST metadata checks (mtime + size)
    Only calculates expensive hash if metadata suggests file changed.
    
    Args:
        source_file: Path to original GPKG file
        data_dir: Directory containing dataset
        
    Returns:
        (needs_cleaning: bool, cached_clean_path: Optional[Path])
        
    If needs_cleaning is False, cached_clean_path will contain the path to use.
    """
    # Load cache manifest
    manifest = load_cache_manifest(data_dir)
    
    if not manifest:
        logger.info("No cache manifest - cleaning needed")
        return True, None
    
    # FAST CHECK: Compare file metadata (mtime + size)
    # Only hash if metadata changed (optimization - avoid 51s hash calculation)
    current_mtime = source_file.stat().st_mtime
    current_size = source_file.stat().st_size
    
    cached_mtime = manifest.get('source_mtime')
    cached_size = manifest.get('source_size')
    cached_path_str = manifest.get('cleaned_path')
    
    # Quick metadata check (instant)
    if cached_mtime == current_mtime and cached_size == current_size:
        # File hasn't changed (same timestamp & size) - use cache!
        if cached_path_str:
            cleaned_path = Path(cached_path_str)
            if cleaned_path.exists():
                logger.info(f"✅ Cache HIT (mtime+size match) - using: {cleaned_path.name}")
                return False, cleaned_path
        
        logger.info("Metadata matches but cleaned file missing - re-cleaning")
        return True, None
    
    # Metadata changed - verify with hash (expensive but necessary)
    logger.info(f"File metadata changed - verifying with hash...")
    logger.info(f"  Size: {cached_size} → {current_size}")
    logger.info(f"  mtime: {cached_mtime} → {current_mtime}")
    
    current_hash = calculate_file_hash(source_file)
    cached_hash = manifest.get('source_hash')
    
    if cached_hash == current_hash:
        # Hash matches - file content unchanged despite metadata change
        # (Maybe just touched/moved - update manifest and use cache)
        logger.info(f"✅ Hash matches despite metadata change - using cache")
        manifest['source_mtime'] = current_mtime
        manifest['source_size'] = current_size
        save_cache_manifest(data_dir, manifest)
        
        if cached_path_str:
            return False, Path(cached_path_str)
    
    # Hash doesn't match - file actually changed
    logger.info(f"Hash mismatch - re-cleaning needed")
    return True, None


def update_cache_after_cleaning(
    source_file: Path,
    cleaned_file: Path,
    data_dir: Path
):
    """
    Update cache manifest after cleaning is complete
    
    Stores:
    - File metadata (mtime, size) for FAST checks
    - Content hash for verification when metadata changes
    
    Args:
        source_file: Original GPKG file
        cleaned_file: Cleaned GPKG file
        data_dir: Dataset directory
    """
    import datetime
    
    # Get file metadata (fast)
    source_stat = source_file.stat()
    cleaned_stat = cleaned_file.stat()
    
    # Calculate hashes (slow, but only once)
    logger.info(f"Calculating hashes for cache manifest...")
    source_hash = calculate_file_hash(source_file)
    cleaned_hash = calculate_file_hash(cleaned_file)
    
    manifest = {
        # Source file tracking
        'source_hash': source_hash,
        'source_file': str(source_file),
        'source_mtime': source_stat.st_mtime,
        'source_size': source_stat.st_size,
        
        # Cleaned file tracking
        'cleaned_hash': cleaned_hash,
        'cleaned_path': str(cleaned_file),
        'cleaned_mtime': cleaned_stat.st_mtime,
        'cleaned_size': cleaned_stat.st_size,
        
        # Metadata
        'timestamp': datetime.datetime.now().isoformat(),
        'note': 'Fast caching: checks mtime+size first, only hashes if changed. Delete to force re-clean.'
    }
    
    save_cache_manifest(data_dir, manifest)
    logger.info(f"✅ Cache updated - future runs check mtime+size (instant) instead of hashing (51s)")


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

