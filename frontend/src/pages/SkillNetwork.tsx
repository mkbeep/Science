import React, { useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

interface SkillNode {
  name: string;
  value: number;
}

interface SkillLink {
  source: string;
  target: string;
  value: number;
}

interface NetworkData {
  nodes: SkillNode[];
  links: SkillLink[];
}

const SkillNetwork: React.FC = () => {
  const [allNetworkData, setAllNetworkData] = useState<NetworkData | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [searchSkill, setSearchSkill] = useState('');
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [availableSkills, setAvailableSkills] = useState<string[]>([]);

  useEffect(() => {
    loadNetworkData();
  }, []);

  const loadNetworkData = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/skills/network?top_skills=30&min_connection=3');
      const data: NetworkData = response.data;
      setAllNetworkData(data);
      
      const skills = data.nodes.map(n => n.name).sort();
      setAvailableSkills(skills);
      
      showAllSkills(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading network data:', error);
      setLoading(false);
    }
  };

  const filterNetworkBySkill = (skillName: string) => {
    if (!allNetworkData) return;

    const selectedNode = allNetworkData.nodes.find(n => 
      n.name.toLowerCase() === skillName.toLowerCase()
    );

    if (!selectedNode) {
      alert(`Không tìm thấy skill "${skillName}"`);
      return;
    }

    const connectedLinks = allNetworkData.links.filter(link => 
      link.source === selectedNode.name || link.target === selectedNode.name
    );

    const connectedSkillNames = new Set<string>();
    connectedSkillNames.add(selectedNode.name);
    connectedLinks.forEach(link => {
      connectedSkillNames.add(link.source);
      connectedSkillNames.add(link.target);
    });

    const filteredNodes = allNetworkData.nodes.filter(node => 
      connectedSkillNames.has(node.name)
    );

    const flowNodes: Node[] = filteredNodes.map((node, index) => {
      const size = Math.max(80, Math.min(180, node.value / 2));
      const isSelected = node.name === selectedNode.name;
      
      let x, y;
      if (isSelected) {
        x = 400;
        y = 300;
      } else {
        const angle = (index / (filteredNodes.length - 1)) * 2 * Math.PI;
        const radius = 250;
        x = 400 + radius * Math.cos(angle);
        y = 300 + radius * Math.sin(angle);
      }
      
      return {
        id: node.name,
        data: { 
          label: (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 'bold', fontSize: isSelected ? '14px' : '12px' }}>
                {node.name}
              </div>
              <div style={{ fontSize: '10px', color: isSelected ? '#FFF' : '#6B7280' }}>
                {node.value} jobs
              </div>
            </div>
          )
        },
        position: { x, y },
        style: {
          background: isSelected ? '#10B981' : '#2563EB',
          color: 'white',
          border: isSelected ? '3px solid #059669' : '2px solid #1E3A5F',
          borderRadius: '50%',
          width: isSelected ? size * 1.2 : size,
          height: isSelected ? size * 1.2 : size,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '11px',
          fontWeight: '600',
          padding: '8px',
          boxShadow: isSelected ? '0 4px 12px rgba(16, 185, 129, 0.4)' : 'none',
        },
      };
    });

    const flowEdges: Edge[] = connectedLinks.map((link) => ({
      id: `${link.source}-${link.target}`,
      source: link.source,
      target: link.target,
      label: `${link.value}`,
      type: 'default',
      animated: link.value > 10,
      style: { 
        stroke: '#94A3B8',
        strokeWidth: Math.max(2, link.value / 2),
      },
      labelStyle: {
        fontSize: '11px',
        fontWeight: 'bold',
        fill: '#1E3A5F',
        background: '#FFF',
        padding: '2px 4px',
        borderRadius: '2px',
      },
      markerEnd: {
        type: MarkerType.Arrow,
        width: 20,
        height: 20,
        color: '#94A3B8',
      },
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
    setSelectedSkill(selectedNode.name);
  };

  const showAllSkills = (data?: NetworkData) => {
    const networkData = data || allNetworkData;
    if (!networkData) return;

    const flowNodes: Node[] = networkData.nodes.map((node, index) => {
      const size = Math.max(60, Math.min(150, node.value / 2));
      const angle = (index / networkData.nodes.length) * 2 * Math.PI;
      const radius = 300;
      const x = 400 + radius * Math.cos(angle);
      const y = 300 + radius * Math.sin(angle);
      
      return {
        id: node.name,
        data: { 
          label: (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 'bold', fontSize: '12px' }}>{node.name}</div>
              <div style={{ fontSize: '10px', color: '#6B7280' }}>{node.value} jobs</div>
            </div>
          )
        },
        position: { x, y },
        style: {
          background: '#2563EB',
          color: 'white',
          border: '2px solid #1E3A5F',
          borderRadius: '50%',
          width: size,
          height: size,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '11px',
          fontWeight: '600',
          padding: '8px',
        },
      };
    });

    const flowEdges: Edge[] = networkData.links.map((link) => ({
      id: `${link.source}-${link.target}`,
      source: link.source,
      target: link.target,
      label: `${link.value}`,
      type: 'default',
      animated: link.value > 10,
      style: { 
        stroke: '#94A3B8',
        strokeWidth: Math.max(1, link.value / 3),
      },
      labelStyle: {
        fontSize: '10px',
        fontWeight: 'bold',
        fill: '#1E3A5F',
      },
      markerEnd: {
        type: MarkerType.Arrow,
        width: 15,
        height: 15,
        color: '#94A3B8',
      },
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
    setSelectedSkill(null);
  };

  const handleSearch = () => {
    if (searchSkill.trim()) {
      filterNetworkBySkill(searchSkill.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        fontFamily: 'Inter, sans-serif',
        fontSize: '14px',
        color: '#6B7280'
      }}>
        Đang tải skill network...
      </div>
    );
  }

  return (
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      minHeight: '100vh',
      padding: '32px',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '30px',
            fontWeight: 'bold',
            lineHeight: '40px',
            color: '#1E3A5F',
            margin: 0,
            marginBottom: '8px'
          }}>
            🔗 Skill Relationship Network
          </h1>
          <p style={{ 
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            lineHeight: '22px',
            color: '#6B7280',
            margin: 0
          }}>
            Phân tích mối quan hệ giữa các kỹ năng trong tin tuyển dụng. 
            Nhập tên skill để xem các skills liên quan.
          </p>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          marginBottom: '16px',
          display: 'flex',
          gap: '12px',
          alignItems: 'center'
        }}>
          <div style={{ flex: 1, display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={searchSkill}
              onChange={(e) => setSearchSkill(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập tên skill (VD: Python, Java, React, SQL...)"
              list="skills-list"
              style={{
                flex: 1,
                padding: '10px 16px',
                border: '1px solid #E2E8F0',
                borderRadius: '4px',
                fontSize: '14px',
                outline: 'none'
              }}
            />
            <datalist id="skills-list">
              {availableSkills.map(skill => (
                <option key={skill} value={skill} />
              ))}
            </datalist>
            <button
              onClick={handleSearch}
              style={{
                padding: '10px 24px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              🔍 Tìm Kiếm
            </button>
            <button
              onClick={() => showAllSkills()}
              style={{
                padding: '10px 24px',
                backgroundColor: '#FFFFFF',
                color: '#6B7280',
                border: '1px solid #E2E8F0',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              🔄 Hiển Thị Tất Cả
            </button>
          </div>
        </div>

        {selectedSkill && (
          <div style={{
            backgroundColor: '#D1FAE5',
            border: '1px solid #10B981',
            borderRadius: '4px',
            padding: '12px 16px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '20px' }}>✅</span>
            <span style={{ fontSize: '14px', color: '#065F46', fontWeight: '600' }}>
              Đang hiển thị: <strong>{selectedSkill}</strong> và {nodes.length - 1} skills liên quan
            </span>
          </div>
        )}

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          overflow: 'hidden',
          marginBottom: '24px'
        }}>
          <div style={{ height: '700px', width: '100%' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-left"
            >
              <Background />
              <Controls />
            </ReactFlow>
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
        }}>
          <h3 style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '16px',
            fontWeight: '600',
            color: '#1E3A5F',
            margin: '0 0 12px 0'
          }}>
            📖 Hướng Dẫn Đọc
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>
              <strong style={{ color: '#1E3A5F' }}>Node xanh lá:</strong> Skill đang được chọn
            </div>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>
              <strong style={{ color: '#1E3A5F' }}>Node xanh dương:</strong> Skills liên quan
            </div>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>
              <strong style={{ color: '#1E3A5F' }}>Độ dày đường:</strong> Mức độ liên quan
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillNetwork;
