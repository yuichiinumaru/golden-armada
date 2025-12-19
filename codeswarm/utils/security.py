from packageurl import PackageURL
from univers.version_range import VersionRange
from univers.versions import PypiVersion, SemverVersion, Version

def resolve_version_range(version_range: str, version: str, package_type: str = "pypi") -> bool:
    """
    Check if a version satisfies a version range.

    Args:
        version_range: The version range specifier (e.g., "vers:pypi/>=1.0.0")
        version: The version to check (e.g., "1.5.0")
        package_type: The package type (default: "pypi")

    Returns:
        bool: True if the version is within the range, False otherwise.
    """
    try:
        # Normalize version range if it doesn't start with vers:
        if not version_range.startswith("vers:"):
            # Univers spec seems to require comma separated constraints for "AND" logic in version range,
            # but for PyPI, it uses commas inside the specifier.
            # However, for univers VersionRange.from_string, it expects a vers string.
            # If the user provides ">=1.0.0,<2.0.0", we need to format it correctly.
            # It seems simple "vers:pypi/>=1.0.0,<2.0.0" doesn't work as expected if it fails parsing.
            # But "vers:pypi/>=1.0.0|<2.0.0" (using pipe for AND? No, pipe is usually OR in some specs, but comma is AND).
            # Wait, univers documentation says "vers:npm/1.2.3,>=2.0.0".
            # For PyPI, maybe "vers:pypi/>=1.0.0,<2.0.0" IS correct if implemented right.
            # But my test failed.
            # Let's try replacing comma with pipe if that worked in the CLI test: 'vers:pypi/>=1.0.0|<2.0.0' worked.
            # univers seems to use '|' for combining constraints in a range for PyPI?
            # Or maybe just multiple constraints are supported differently.
            # Let's try to simple string substitution for now based on successful CLI test.
            normalized_range = version_range.replace(",", "|")
            version_range = f"vers:{package_type}/{normalized_range}"

        vr = VersionRange.from_string(version_range)

        if package_type == "pypi":
            v = PypiVersion(version)
        elif package_type == "npm":
            v = SemverVersion(version)
        else:
            # Try to infer or use generic version if available, but univers is strict
            # For now default to PypiVersion as a fallback if compatible, or fail
            v = PypiVersion(version)

        return v in vr
    except Exception:
        return False
    except Exception as e:
        # If parsing fails, we log or return False (safe default for security checks? or maybe True to avoid blocking?)
        # Let's return False and maybe log if we had a logger here.
        return False
