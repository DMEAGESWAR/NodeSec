import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import DomainNode from './CustomNodes';
import AttackPathHighlight from './AttackPathHighlight';

const nodeTypes = {
  domain: DomainNode,
  subdomain: DomainNode,
  port: DomainNode,
  breach: DomainNode,
  ssl_issue: DomainNode,
};

const SEVERITY_ORDER = { critical: 4, high: 3, medium: 2, low: 1 };

function buildFlowNodes(nodes) {
  const sorted = [...(nodes || [])].sort(
    (a, b) => (SEVERITY_ORDER[b.severity] || 0) - (SEVERITY_ORDER[a.severity] || 0)
  );
  return sorted.map((n, i) => ({
    id: n.id,
    type: n.node_type,
    position: { x: Math.cos((i / Math.max(sorted.length, 1)) * Math.PI * 2) * 250 + 350, y: Math.sin((i / Math.max(sorted.length, 1)) * Math.PI * 2) * 200 + 250 },
    data: {
      label: n.label,
      node_type: n.node_type,
      severity: n.severity,
      ip: n.ip,
      port: n.port,
    },
  }));
}

function buildFlowEdges(edges) {
  return (edges || []).map((e) => ({
    id: e.id,
    source: e.source_node_id || e.source,
    target: e.target_node_id || e.target,
    type: 'smoothstep',
    animated: e.relationship_type === 'has_breach',
    style: { stroke: e.relationship_type === 'has_breach' ? '#FF4444' : '#30363D', strokeWidth: 2 },
  }));
}

export default function AttackGraph({ nodes: rawNodes, edges: rawEdges, chains = [], highlightNodes = [], onNodeClick }) {
  const flowNodes = useMemo(() => buildFlowNodes(rawNodes), [rawNodes]);
  const flowEdges = useMemo(() => buildFlowEdges(rawEdges), [rawEdges]);
  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  const handleNodeClick = useCallback(
    (_, node) => {
      if (onNodeClick) onNodeClick(node);
    },
    [onNodeClick]
  );

  return (
    <div className="w-full h-[500px] bg-bg-primary border border-border rounded-card overflow-hidden relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        nodesDraggable
        nodesConnectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#30363D" gap={20} />
        <Controls />
        <MiniMap
          style={{ backgroundColor: 'var(--bg-secondary)' }}
          maskColor="rgba(0,0,0,0.7)"
          nodeColor={(n) => {
            const severity = n.data?.severity || 'low';
            return { critical: '#FF4444', high: '#F0A500', medium: '#58A6FF', low: '#3FB950' }[severity];
          }}
        />
      </ReactFlow>
      {highlightNodes.length > 0 && <AttackPathHighlight nodeIds={highlightNodes} />}
    </div>
  );
}