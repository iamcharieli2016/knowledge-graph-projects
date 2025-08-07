// API 响应类型定义
export interface ApiResponse<T> {
  status: string;
  message: string;
  data?: T;
}

// 配置类型
export interface Config {
  extraction: {
    similarity_threshold: number;
    min_entity_length: number;
    min_confidence: number;
    max_context_window: number;
    use_patterns: boolean;
    use_pos_tagging: boolean;
    use_dictionary: boolean;
  };
  mapping: {
    entity_similarity_threshold: number;
    relation_similarity_threshold: number;
    fuzzy_match_threshold: number;
    use_semantic_mapping: boolean;
    use_context_mapping: boolean;
  };
  fusion: {
    entity_fusion_threshold: number;
    relation_fusion_threshold: number;
    conflict_resolution_strategy: string;
    merge_similar_entities: boolean;
    preserve_provenance: boolean;
  };
  visualization: {
    max_nodes: number;
    node_size: number;
    edge_width: number;
    layout: string;
    output_format: string;
    figure_size: [number, number];
  };
  output_dir: string;
  log_level: string;
}

// 任务类型
export interface Task {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  message: string;
  created_at: string;
  progress: number;
  results?: KnowledgeGraphData;
  error?: string;
}

// 知识图谱数据类型
export interface KnowledgeGraphData {
  entities: Entity[];
  relations: Relation[];
  statistics: Statistics;
}

export interface Entity {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
  aliases: string[];
}

export interface Relation {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, any>;
  confidence: number;
}

export interface Statistics {
  entity_count: number;
  relation_count: number;
  entity_types: Record<string, number>;
  relation_types: Record<string, number>;
  avg_degree: number;
  connected_components: number;
  density: number;
}

// 示例数据类型
export interface SampleData {
  texts: string[];
  domains: string[];
  total_count: number;
}

// 文本输入类型
export interface TextInput {
  texts: string[];
  domain?: string;
}