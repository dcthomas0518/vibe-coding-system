"""
OS-004: Intelligent Context Management System
Maintains peak cognitive performance through intelligent reboots
"""

from .context_manager import ContextManager
from .subagent_wrapper import SubAgentContextWrapper, SubAgentRegistry

__all__ = ['ContextManager', 'SubAgentContextWrapper', 'SubAgentRegistry']

# Version info
__version__ = '1.0.0'
__author__ = 'Vibe Coding System'
__description__ = 'Peak performance maintenance for all AI entities'