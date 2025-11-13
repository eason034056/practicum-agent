"""
Configuration Package Initializer

This file makes the 'config' directory a Python package.
It also provides convenient imports for the rest of the application.

Why this file exists:
- Makes 'config' a proper Python package
- Allows "from config import settings" instead of "from config.settings import settings"
- Can perform package-level initialization if needed
"""

# Import settings from settings.py module
# This allows other files to do: from config import settings
from config.settings import settings

# __all__: Defines what gets exported when someone does "from config import *"
# This is a list of public names that should be available
__all__ = ["settings"]
# Why __all__: 
# - Makes the public API explicit
# - Prevents accidental exposure of internal implementation details
# - Improves IDE autocomplete suggestions

# Note: Even without __all__, you can still import settings explicitly
# Example: from config.settings import settings

