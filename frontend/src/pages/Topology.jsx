import { useState, useEffect } from 'react';
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { getTopology } from '../services/api';
import { Info } from 'lucide-react';

export default function Topology() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [note, setNote] = useState('');

  useEffect(() => {
    const fetchTopology = async () => {
      try {
        const res = await getTopology();
        setNodes(res.data.nodes);
        setEdges(res.data.edges);
        setNote(res.data.note);
      } catch (error) {
        console.error("Failed to load topology", error);
      }
    };
    fetchTopology();
  }, []);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Network Topology</h2>
      </div>

      {note && (
        <div className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg flex items-center space-x-3 text-sm text-slate-300">
          <Info size={16} className="text-blue-400" />
          <span>{note}</span>
        </div>
      )}

      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[600px]">
        <ReactFlow 
          nodes={nodes} 
          edges={edges}
          fitView
          className="bg-slate-950"
          colorMode="dark"
        >
          <Background color="#334155" gap={16} />
          <Controls className="bg-slate-800 border-slate-700 text-slate-200 fill-slate-200" />
          <MiniMap nodeStrokeColor="#475569" nodeColor="#1e293b" maskColor="rgba(15, 23, 42, 0.7)" />
        </ReactFlow>
      </div>
    </div>
  );
}
