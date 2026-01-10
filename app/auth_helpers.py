"""
DEPRECATED: This file is replaced by client_auth.py

Keep this file for now for backwards compatibility,
but all decorators now come from client_auth.py

To migrate, replace imports:
  OLD: from .auth_helpers import login_required, admin_required
  NEW: from .client_auth import login_required, admin_required
"""

# Import from new centralized auth module
from .client_auth import login_required, admin_required

# Keep old functions as aliases for backwards compatibility
__all__ = ['login_required', 'admin_required']