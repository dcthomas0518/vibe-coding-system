#!/usr/bin/env python3
"""
Memory Loader - Rapid context restoration from organizational memories
Target: <30 second full context load
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import concurrent.futures
import time

class MemoryLoader:
    """Lightning-fast memory restoration for session start"""
    
    def __init__(self):
        self.db_path = Path("organizational_memory.db")
        self.cache_path = Path("MEMORY_CACHE.json")
        self.context_path = Path("MEMORY_CONTEXT.json")
        
    def load_session_context(self) -> Dict:
        """Primary entry point - loads all relevant memories in <30s"""
        start_time = datetime.now()
        
        print("🔄 Loading organizational memories...")
        
        # Phase 1: Load current context markers (1-2s)
        context_markers = self._load_context_markers()
        print(f"  ✓ Context markers loaded: mode={context_markers.get('current_mode')}, project={context_markers.get('active_project')}")
        
        # Phase 2: Parallel memory retrieval (5-10s)
        memories = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all queries in parallel
            futures = {
                'recent': executor.submit(self._load_recent_memories),
                'mode_specific': executor.submit(self._load_mode_memories, context_markers.get('current_mode')),
                'project_specific': executor.submit(self._load_project_memories, context_markers.get('active_project')),
                'high_significance': executor.submit(self._load_significant_memories),
                'cross_mode_flows': executor.submit(self._load_cross_mode_connections)
            }
            
            # Collect results
            for key, future in futures.items():
                try:
                    memories[key] = future.result()
                    print(f"  ✓ Loaded {key} memories: {len(memories[key])} items")
                except Exception as e:
                    print(f"  ⚠ Failed to load {key}: {e}")
                    memories[key] = []
        
        # Phase 3: Build memory graph (2-3s)
        memory_graph = self._build_memory_graph(memories)
        print(f"  ✓ Memory graph built: {len(memory_graph['nodes'])} nodes, {len(memory_graph['edges'])} edges")
        
        # Phase 4: Generate context summary (2-3s)
        context_summary = self._generate_context_summary(memory_graph)
        
        # Phase 5: Cache for next session (1s)
        self._update_cache(context_summary)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"✨ Memory context loaded in {elapsed:.1f} seconds")
        
        return context_summary
    
    def _load_context_markers(self) -> Dict:
        """Extract context from CURRENT_CONTEXT.md and environment"""
        markers = {
            'current_mode': 'CTO',  # Default
            'active_project': None,
            'last_session': None,
            'working_directory': Path.cwd().name
        }
        
        # Read CURRENT_CONTEXT.md
        current_context_path = Path.home() / "CURRENT_CONTEXT.md"
        if current_context_path.exists():
            content = current_context_path.read_text()
            # Parse for active project
            if "OS-001" in content:
                markers['active_project'] = "OS-001"
            elif "TR-001" in content:
                markers['active_project'] = "TR-001"
        
        # Check for saved context
        if self.context_path.exists():
            try:
                with open(self.context_path) as f:
                    saved_context = json.load(f)
                    markers.update(saved_context)
            except:
                pass
        
        return markers
    
    def _load_recent_memories(self, hours: int = 24) -> List[Dict]:
        """Load memories from recent timeframe"""
        if not self.db_path.exists():
            return []
            
        conn = sqlite3.connect(self.db_path)
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        results = conn.execute("""
            SELECT memory_json FROM memories 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (cutoff,)).fetchall()
        
        conn.close()
        return [json.loads(row[0]) for row in results]
    
    def _load_mode_memories(self, mode: Optional[str]) -> List[Dict]:
        """Load memories specific to current mode"""
        if not mode or not self.db_path.exists():
            return []
            
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("""
            SELECT memory_json FROM memories 
            WHERE entity_mode = ? 
            ORDER BY timestamp DESC 
            LIMIT 15
        """, (mode,)).fetchall()
        
        conn.close()
        return [json.loads(row[0]) for row in results]
    
    def _load_project_memories(self, project: Optional[str]) -> List[Dict]:
        """Load memories related to active project"""
        if not project or not self.db_path.exists():
            return []
            
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("""
            SELECT memory_json FROM memories 
            WHERE project = ? 
            ORDER BY timestamp DESC 
            LIMIT 15
        """, (project,)).fetchall()
        
        conn.close()
        return [json.loads(row[0]) for row in results]
    
    def _load_significant_memories(self) -> List[Dict]:
        """Load memories marked as critical or notable"""
        if not self.db_path.exists():
            return []
            
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("""
            SELECT memory_json FROM memories 
            WHERE event_significance IN ('critical', 'notable')
            ORDER BY timestamp DESC 
            LIMIT 10
        """).fetchall()
        
        conn.close()
        return [json.loads(row[0]) for row in results]
    
    def _load_cross_mode_connections(self) -> List[Dict]:
        """Load memories that show cross-mode knowledge flow"""
        if not self.db_path.exists():
            return []
            
        # For now, return empty - will implement connection tracking
        return []
    
    def _build_memory_graph(self, memories: Dict[str, List]) -> Dict:
        """Build interconnected memory graph showing knowledge flows"""
        graph = {
            'nodes': {},
            'edges': [],
            'clusters': {}
        }
        
        # Aggregate all unique memories
        seen_ids = set()
        all_memories = []
        for category, memory_list in memories.items():
            for memory in memory_list:
                if memory['id'] not in seen_ids:
                    seen_ids.add(memory['id'])
                    all_memories.append(memory)
        
        # Build nodes
        for memory in all_memories:
            graph['nodes'][memory['id']] = {
                'memory': memory,
                'connections': memory.get('connections', {}),
                'weight': self._calculate_memory_weight(memory)
            }
        
        # Build edges (knowledge flows)
        for memory_id, node in graph['nodes'].items():
            # Influences edges
            for influenced_id in node['connections'].get('influences', []):
                if influenced_id in graph['nodes']:
                    graph['edges'].append({
                        'from': memory_id,
                        'to': influenced_id,
                        'type': 'influences'
                    })
            
            # Influenced by edges
            for influenced_by_id in node['connections'].get('influenced_by', []):
                if influenced_by_id in graph['nodes']:
                    graph['edges'].append({
                        'from': influenced_by_id,
                        'to': memory_id,
                        'type': 'influenced_by'
                    })
        
        return graph
    
    def _calculate_memory_weight(self, memory: Dict) -> float:
        """Calculate importance weight of a memory"""
        weight = 1.0
        
        # Significance multiplier
        significance = memory['event'].get('significance', 'routine')
        if significance == 'critical':
            weight *= 3.0
        elif significance == 'notable':
            weight *= 2.0
        
        # Recency boost
        timestamp = datetime.fromisoformat(memory['timestamp'])
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        if age_hours < 24:
            weight *= 1.5
        elif age_hours < 72:
            weight *= 1.2
        
        # Connection boost
        connections = memory.get('connections', {})
        total_connections = len(connections.get('influences', [])) + len(connections.get('influenced_by', []))
        weight *= (1 + total_connections * 0.1)
        
        return weight
    
    def _generate_context_summary(self, memory_graph: Dict) -> Dict:
        """Generate actionable context summary for session start"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_memories': len(memory_graph['nodes']),
            'key_insights': [],
            'active_patterns': [],
            'cross_mode_flows': [],
            'recommended_focus': [],
            'memory_graph': memory_graph  # Include for debugging
        }
        
        # Extract key insights from high-weight memories
        sorted_memories = sorted(
            memory_graph['nodes'].values(),
            key=lambda x: x['weight'],
            reverse=True
        )[:10]
        
        for node in sorted_memories:
            memory = node['memory']
            if memory.get('content', {}).get('insight'):
                summary['key_insights'].append({
                    'insight': memory['content']['insight'],
                    'entity': f"{memory['entity']['name']} ({memory['entity']['mode']})",
                    'significance': memory['event'].get('significance', 'routine'),
                    'timestamp': memory['timestamp'],
                    'project': memory.get('context', {}).get('project')
                })
        
        # Identify cross-mode knowledge flows
        mode_transitions = {}
        for edge in memory_graph['edges']:
            if edge['from'] in memory_graph['nodes'] and edge['to'] in memory_graph['nodes']:
                from_node = memory_graph['nodes'][edge['from']]
                to_node = memory_graph['nodes'][edge['to']]
                
                from_mode = from_node['memory']['entity']['mode']
                to_mode = to_node['memory']['entity']['mode']
                
                if from_mode != to_mode:
                    flow_key = f"{from_mode} → {to_mode}"
                    if flow_key not in mode_transitions:
                        mode_transitions[flow_key] = []
                    
                    mode_transitions[flow_key].append({
                        'from': f"{from_mode}: {from_node['memory']['event']['description'][:50]}...",
                        'to': f"{to_mode}: {to_node['memory']['event']['description'][:50]}...",
                        'impact': to_node['memory'].get('outcome', {}).get('impact', 'pending')
                    })
        
        # Add top cross-mode flows
        for flow_type, flows in mode_transitions.items():
            summary['cross_mode_flows'].extend(flows[:2])  # Top 2 per flow type
        
        # Generate recommended focus based on patterns
        if summary['key_insights']:
            # Focus on recent critical items
            critical_recent = [
                i for i in summary['key_insights'] 
                if i['significance'] == 'critical'
            ]
            if critical_recent:
                summary['recommended_focus'].append(
                    f"Critical: {critical_recent[0]['insight'][:100]}..."
                )
        
        return summary
    
    def _update_cache(self, context_summary: Dict):
        """Cache summary for faster subsequent loads"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': context_summary
        }
        
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"  ⚠ Cache update failed: {e}")


# Test functionality
if __name__ == "__main__":
    print("🧠 Testing Memory Loader...")
    loader = MemoryLoader()
    
    # Test context loading
    context = loader.load_session_context()
    
    print(f"\n📊 Context Summary:")
    print(f"  - Total memories: {context['total_memories']}")
    print(f"  - Key insights: {len(context['key_insights'])}")
    print(f"  - Cross-mode flows: {len(context['cross_mode_flows'])}")
    
    if context['key_insights']:
        print(f"\n💡 Top Insights:")
        for insight in context['key_insights'][:3]:
            print(f"  - {insight['entity']}: {insight['insight'][:80]}...")