#!/usr/bin/env python3
"""
Session Memory Bridge - Integrates memories with Claude's session management
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class SessionMemoryBridge:
    """Bridge between Internal Memory System and session persistence"""
    
    def __init__(self):
        self.memory_manifest_path = Path("MEMORY_MANIFEST.md")
        self.session_memory_path = Path("SESSION_MEMORIES.json")
        
    def inject_into_claude_context(self, memory_summary: Dict) -> str:
        """Generate markdown for Claude's context on session start"""
        
        manifest = f"""# Organizational Memory Context
*Loaded from Internal Memory System - {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Active Knowledge State

### Key Insights from Previous Sessions
"""
        
        # Add key insights with proper formatting
        for insight in memory_summary.get('key_insights', [])[:5]:
            significance_emoji = {
                'critical': '🔴',
                'notable': '🟡',
                'routine': '⚪'
            }.get(insight.get('significance', 'routine'), '⚪')
            
            manifest += f"- {significance_emoji} **{insight['entity']}**: {insight['insight']}\n"
            if insight.get('project'):
                manifest += f"  - Project: {insight['project']}\n"
        
        # Add cross-mode knowledge flows
        if memory_summary.get('cross_mode_flows'):
            manifest += "\n### Cross-Mode Knowledge Flows\n"
            manifest += "*How knowledge has flowed between different modes:*\n"
            for flow in memory_summary['cross_mode_flows'][:3]:
                manifest += f"- {flow['from']}\n"
                manifest += f"  ↓ *influenced*\n"
                manifest += f"  {flow['to']}\n"
                if flow.get('impact') and flow['impact'] != 'pending':
                    manifest += f"  Impact: {flow['impact']}\n"
                manifest += "\n"
        
        # Add recommended focus areas
        if memory_summary.get('recommended_focus'):
            manifest += "### Recommended Focus Areas\n"
            manifest += "*Based on organizational memory patterns:*\n"
            for focus in memory_summary['recommended_focus']:
                manifest += f"- {focus}\n"
        
        # Add memory statistics
        manifest += f"\n### Memory Statistics\n"
        manifest += f"- Total organizational memories: {memory_summary.get('total_memories', 0)}\n"
        manifest += f"- Memories loaded this session: {len(memory_summary.get('key_insights', []))}\n"
        manifest += f"- Cross-mode connections found: {len(memory_summary.get('cross_mode_flows', []))}\n"
        
        # Save manifest
        self.memory_manifest_path.write_text(manifest)
        
        return manifest
    
    def update_current_context(self, memory_summary: Dict):
        """Enhance CURRENT_CONTEXT.md with memory insights"""
        current_context_path = Path.home() / "CURRENT_CONTEXT.md"
        
        # Create minimal context if doesn't exist
        if not current_context_path.exists():
            initial_content = """# Current Context

## Active Work
- Building OS-001 Organizational Memory System

"""
            current_context_path.write_text(initial_content)
        
        content = current_context_path.read_text()
        
        # Check if memory section already exists
        if "## Organizational Memory Insights" in content:
            # Update existing section
            lines = content.split('\n')
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if line.startswith("## Organizational Memory Insights"):
                    start_idx = i
                elif start_idx is not None and line.startswith("## "):
                    end_idx = i
                    break
            
            if end_idx is None:
                end_idx = len(lines)
            
            # Remove old section
            lines = lines[:start_idx] + lines[end_idx:]
            content = '\n'.join(lines)
        
        # Find insertion point (after first header)
        lines = content.split('\n')
        insert_index = 2  # After title and first blank line
        
        # Create memory section
        memory_section = [
            "",
            "## Organizational Memory Insights",
            f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            ""
        ]
        
        # Add most relevant insights
        if memory_summary.get('key_insights'):
            memory_section.append("### Recent Discoveries")
            for i, insight in enumerate(memory_summary['key_insights'][:3]):
                # Truncate long insights
                insight_text = insight['insight']
                if len(insight_text) > 100:
                    insight_text = insight_text[:97] + "..."
                memory_section.append(f"{i+1}. **{insight['entity']}**: {insight_text}")
            memory_section.append("")
        
        # Add active patterns if any
        if memory_summary.get('cross_mode_flows'):
            memory_section.append("### Active Knowledge Flows")
            memory_section.append("*Knowledge actively flowing between modes:*")
            for flow in memory_summary['cross_mode_flows'][:2]:
                # Extract just the modes
                from_mode = flow['from'].split(':')[0]
                to_mode = flow['to'].split(':')[0]
                memory_section.append(f"- {from_mode} → {to_mode}")
            memory_section.append("")
        
        # Insert into content
        new_lines = lines[:insert_index] + memory_section + lines[insert_index:]
        
        # Write back
        current_context_path.write_text('\n'.join(new_lines))
        
        print(f"  ✓ Updated CURRENT_CONTEXT.md with {len(memory_summary.get('key_insights', []))} insights")
    
    def save_session_memories(self, memory_summary: Dict):
        """Save current session's memory state for debugging/analysis"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': memory_summary,
            'stats': {
                'total_memories': memory_summary.get('total_memories', 0),
                'insights_loaded': len(memory_summary.get('key_insights', [])),
                'cross_mode_flows': len(memory_summary.get('cross_mode_flows', [])),
            }
        }
        
        try:
            with open(self.session_memory_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"  ✓ Saved session memory state to {self.session_memory_path}")
        except Exception as e:
            print(f"  ⚠ Failed to save session memories: {e}")
    
    def generate_memory_prompt(self, memory_summary: Dict) -> str:
        """Generate a prompt snippet for Claude to understand memory context"""
        prompt = "\n[ORGANIZATIONAL MEMORY CONTEXT]\n"
        
        if memory_summary.get('key_insights'):
            # Get the most critical/recent insight
            critical_insights = [
                i for i in memory_summary['key_insights'] 
                if i.get('significance') == 'critical'
            ]
            
            if critical_insights:
                insight = critical_insights[0]
                prompt += f"Critical insight from {insight['entity']}: {insight['insight']}\n"
            else:
                # Just get most recent
                insight = memory_summary['key_insights'][0]
                prompt += f"Recent insight from {insight['entity']}: {insight['insight']}\n"
        
        if memory_summary.get('cross_mode_flows'):
            prompt += "Knowledge is flowing between modes - leverage cross-functional insights.\n"
        
        prompt += "[END MEMORY CONTEXT]\n"
        
        return prompt


# Test the bridge
if __name__ == "__main__":
    print("🌉 Testing Session Memory Bridge...")
    
    # Create test memory summary
    test_summary = {
        'timestamp': datetime.now().isoformat(),
        'total_memories': 4,
        'key_insights': [
            {
                'insight': 'The OS needs a collective soul where knowledge flows between entities and modes',
                'entity': 'Pompey (CTO)',
                'significance': 'critical',
                'project': 'OS-001'
            },
            {
                'insight': 'Quick wins build momentum - deploy basic capture TODAY',
                'entity': 'Pompey (CTO)',
                'significance': 'notable',
                'project': 'OS-001'
            }
        ],
        'cross_mode_flows': [
            {
                'from': 'CTO: Journey capture system implementation',
                'to': 'Creative_Director: Visual content showing moat-building',
                'impact': 'Content idea generated'
            }
        ],
        'recommended_focus': [
            'Complete memory persistence implementation',
            'Test cross-session memory retention'
        ]
    }
    
    # Test bridge functions
    bridge = SessionMemoryBridge()
    
    # Generate manifest
    manifest = bridge.inject_into_claude_context(test_summary)
    print(f"\n📄 Generated manifest ({len(manifest)} chars)")
    print("First 500 chars:")
    print(manifest[:500] + "...")
    
    # Update current context
    bridge.update_current_context(test_summary)
    
    # Save session state
    bridge.save_session_memories(test_summary)
    
    # Generate prompt
    prompt = bridge.generate_memory_prompt(test_summary)
    print(f"\n💭 Memory prompt for Claude:")
    print(prompt)