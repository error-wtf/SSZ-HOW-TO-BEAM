#!/usr/bin/env python3
"""Create release ZIP for SSZ-HOW-TO-BEAM."""

import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def create_release_zip(
    version: str = "1.0.0",
    output_dir: str = "dist",
    exclude_patterns: list = None,
) -> str:
    """Create clean release ZIP.
    
    Args:
        version: Release version
        output_dir: Output directory for ZIP
        exclude_patterns: Additional patterns to exclude
        
    Returns:
        Path to created ZIP file
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Default exclusions
    default_excludes = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".gitignore",
        ".venv",
        ".env",
        ".pytest_cache",
        ".mypy_cache",
        "*.h5",
        "*.par",
        "*.png",
        "*.jpg",
        "*.egg-info",
        "dist",
        "build",
        "*.egg",
        "old_dist",
        "docs/archive/OLD_FAILED_RUNS",
        # Old v1.0.0 release files (historical, not current)
        "RELEASE_v1.0.0.md",
        "RELEASE_AUDIT_v1.0.0.md",
        "V0_8_FREEZE_REPORT.md",
        "V0_9_DEVELOPMENT_PLAN.md",
        "COMPLETE_VALUE_ANALYSIS.md",
        "REAL_TEST_RESULTS.txt",
        "test_v1_final.py",
        "FULL_REPORT.md",
        "*.zip",  # Old release ZIPs
    ]
    
    all_excludes = default_excludes + exclude_patterns
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    zip_name = f"SSZ-HOW-TO-BEAM-v{version}.zip"
    zip_path = output_path / zip_name
    
    # Remove old ZIP if exists
    if zip_path.exists():
        zip_path.unlink()
        print(f"Removed old: {zip_path}")
    
    repo_root = Path(__file__).parent.parent
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in repo_root.rglob("*"):
            # Skip directories and excluded patterns
            try:
                if file_path.is_dir():
                    continue
            except (PermissionError, OSError):
                continue
                
            # Check exclusions
            relative_path = file_path.relative_to(repo_root)
            str_path = str(relative_path)
            path_parts = relative_path.parts
            
            skip = False
            for pattern in all_excludes:
                # Match exact path components (e.g., exact folder name)
                if pattern in path_parts:
                    skip = True
                    break
                # Check specific file extensions
                if pattern.startswith('*.') and str_path.endswith(pattern[1:]):
                    skip = True
                    break
                # Check exact filename matches at end of path
                if str_path.endswith('/' + pattern) or str_path == pattern:
                    skip = True
                    break
                # Check exact start of path
                if str_path.startswith(pattern + '/'):
                    skip = True
                    break
                    
            if skip:
                continue
            
            # Add to ZIP (skip symlinks that cause issues)
            try:
                if file_path.is_symlink():
                    continue
                arcname = f"SSZ-HOW-TO-BEAM/{relative_path}"
                zf.write(file_path, arcname)
            except (PermissionError, OSError):
                continue
    
    # Verify size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Created: {zip_path}")
    print(f"Size: {size_mb:.2f} MB")
    print(f"Version: {version}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    return str(zip_path)


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
    zip_path = create_release_zip(version)
    print(f"\nRelease ZIP ready: {zip_path}")
