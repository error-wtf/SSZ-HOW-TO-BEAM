#!/usr/bin/env python3
"""Verify release ZIP integrity and contents."""

import os
import sys
import zipfile
from pathlib import Path


def verify_release_zip(zip_path: str) -> dict:
    """Verify release ZIP meets release standards.
    
    Args:
        zip_path: Path to ZIP file
        
    Returns:
        Verification report dict
    """
    zip_file = Path(zip_path)
    
    report = {
        "zip_path": str(zip_file),
        "exists": False,
        "size_mb": 0.0,
        "files_count": 0,
        "has_src": False,
        "has_tests": False,
        "has_docs": False,
        "has_pycache": False,
        "has_pyc": False,
        "has_git": False,
        "has_venv": False,
        "required_files_found": [],
        "forbidden_files_found": [],
        "status": "UNKNOWN",
    }
    
    if not zip_file.exists():
        report["status"] = "ZIP_NOT_FOUND"
        return report
    
    report["exists"] = True
    report["size_mb"] = zip_file.stat().st_size / (1024 * 1024)
    
    with zipfile.ZipFile(zip_file, 'r') as zf:
        report["files_count"] = len(zf.namelist())
        
        for name in zf.namelist():
            # Check for required structure
            if "SSZ-HOW-TO-BEAM/src/" in name:
                report["has_src"] = True
            if "SSZ-HOW-TO-BEAM/tests/" in name:
                report["has_tests"] = True
            if "SSZ-HOW-TO-BEAM/docs/" in name:
                report["has_docs"] = True
                
            # Check for forbidden content
            if "__pycache__" in name:
                report["has_pycache"] = True
                report["forbidden_files_found"].append(name)
            if name.endswith('.pyc') or name.endswith('.pyo'):
                report["has_pyc"] = True
                report["forbidden_files_found"].append(name)
            if ".git/" in name:
                report["has_git"] = True
                report["forbidden_files_found"].append(name)
            if ".venv" in name or ".env" in name:
                report["has_venv"] = True
                report["forbidden_files_found"].append(name)
    
    # Check for required files
    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "src/beam_ssz/__init__.py",
        "run_all_modules_test.py",
    ]
    
    with zipfile.ZipFile(zip_file, 'r') as zf:
        names = zf.namelist()
        for req in required_files:
            found = any(req in name for name in names)
            if found:
                report["required_files_found"].append(req)
    
    # Determine status
    if report["has_pycache"] or report["has_pyc"] or report["has_git"] or report["has_venv"]:
        report["status"] = "FAILED_FORBIDDEN_CONTENT"
    elif not report["has_src"] or not report["has_tests"]:
        report["status"] = "FAILED_MISSING_STRUCTURE"
    elif len(report["required_files_found"]) < len(required_files):
        report["status"] = "FAILED_MISSING_REQUIRED_FILES"
    else:
        report["status"] = "PASS"
    
    return report


def print_report(report: dict):
    """Print verification report."""
    print("=" * 60)
    print("RELEASE ZIP VERIFICATION REPORT")
    print("=" * 60)
    print(f"ZIP Path: {report['zip_path']}")
    print(f"Status: {report['status']}")
    print(f"Size: {report['size_mb']:.2f} MB")
    print(f"Files: {report['files_count']}")
    print()
    print("Structure:")
    print(f"  src/: {'✅' if report['has_src'] else '❌'}")
    print(f"  tests/: {'✅' if report['has_tests'] else '❌'}")
    print(f"  docs/: {'✅' if report['has_docs'] else '❌'}")
    print()
    print("Forbidden Content Check:")
    print(f"  __pycache__: {'❌ FOUND' if report['has_pycache'] else '✅ None'}")
    print(f"  *.pyc files: {'❌ FOUND' if report['has_pyc'] else '✅ None'}")
    print(f"  .git/: {'❌ FOUND' if report['has_git'] else '✅ None'}")
    print(f"  .venv/: {'❌ FOUND' if report['has_venv'] else '✅ None'}")
    
    if report["forbidden_files_found"]:
        print("\nForbidden files found:")
        for f in report["forbidden_files_found"][:10]:
            print(f"  - {f}")
        if len(report["forbidden_files_found"]) > 10:
            print(f"  ... and {len(report['forbidden_files_found']) - 10} more")
    
    print()
    print("Required Files:")
    for f in ["pyproject.toml", "README.md", "LICENSE", "src/beam_ssz/__init__.py", "run_all_modules_test.py"]:
        found = f in report["required_files_found"]
        print(f"  {f}: {'✅' if found else '❌'}")
    
    print()
    print("=" * 60)
    if report["status"] == "PASS":
        print("✅ ZIP IS READY FOR RELEASE")
    else:
        print("❌ ZIP HAS ISSUES - NOT RELEASE READY")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default path
        zip_path = "dist/SSZ-HOW-TO-BEAM-v1.0.0.zip"
    else:
        zip_path = sys.argv[1]
    
    report = verify_release_zip(zip_path)
    print_report(report)
    
    # Exit with appropriate code
    sys.exit(0 if report["status"] == "PASS" else 1)
