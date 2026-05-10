import { BaseEdge, getSmoothStepPath } from '@xyflow/react';

export default function AnimatedEdge({ id, sourceX, sourceY, targetX, targetY, data }) {
  const [edgePath] = getSmoothStepPath({ sourceX, sourceY, targetX, targetY });
  const isBreach = data?.relationship_type === 'has_breach';

  return (
    <BaseEdge
      id={id}
      path={edgePath}
      style={{
        stroke: isBreach ? '#FF4444' : '#30363D',
        strokeWidth: isBreach ? 2.5 : 1.5,
        strokeDasharray: isBreach ? '5,5' : 'none',
      }}
    />
  );
}