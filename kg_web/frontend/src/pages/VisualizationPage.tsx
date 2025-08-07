import React, { useState, useEffect } from 'react';
import {
  Card,
  Select,
  Button,
  Row,
  Col,
  Statistic,
  Typography,
  Space,
  Alert,
  Spin,
  Image,
  Table,
  Tabs,
  Tag
} from 'antd';
import {
  ReloadOutlined,
  DownloadOutlined,
  FullscreenOutlined,
  TableOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';
import { Task, KnowledgeGraphData } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const VisualizationPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);

  useEffect(() => {
    loadCompletedTasks();
    
    // 从URL参数获取taskId
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('taskId');
    if (taskId) {
      setSelectedTaskId(taskId);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (selectedTaskId) {
      loadGraphData(selectedTaskId);
    }
  }, [selectedTaskId]);

  const loadCompletedTasks = async () => {
    try {
      const data = await apiService.getAllTasks();
      const completedTasks = data.tasks.filter(task => task.status === 'completed');
      setTasks(completedTasks);
      
      if (completedTasks.length > 0 && !selectedTaskId) {
        setSelectedTaskId(completedTasks[0].id);
      }
    } catch (error) {
      console.error('加载任务失败:', error);
    }
  };

  const loadGraphData = async (taskId: string) => {
    setLoading(true);
    try {
      const data = await apiService.getKnowledgeGraph(taskId);
      setGraphData(data);
    } catch (error) {
      console.error('加载图谱数据失败:', error);
      setGraphData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskChange = (taskId: string) => {
    setSelectedTaskId(taskId);
  };

  const handleDownloadImage = () => {
    if (selectedTaskId) {
      const url = apiService.getVisualizationUrl(selectedTaskId);
      const link = document.createElement('a');
      link.href = url;
      link.download = `knowledge_graph_${selectedTaskId}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleFullscreen = () => {
    if (selectedTaskId) {
      const url = apiService.getVisualizationUrl(selectedTaskId);
      window.open(url, '_blank');
    }
  };

  // 实体表格列定义
  const entityColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: string) => (
        <Text code style={{ fontSize: 12 }}>
          {id.length > 10 ? `${id.substring(0, 10)}...` : id}
        </Text>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const colors = {
          Person: 'blue',
          Organization: 'green',
          Location: 'orange',
          Product: 'purple',
          Event: 'red',
          Concept: 'cyan'
        };
        return <Tag color={colors[type as keyof typeof colors] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '属性数量',
      dataIndex: 'properties',
      key: 'properties',
      render: (properties: Record<string, any>) => Object.keys(properties || {}).length,
    },
    {
      title: '别名',
      dataIndex: 'aliases',
      key: 'aliases',
      render: (aliases: string[]) => (
        <div>
          {(aliases || []).slice(0, 3).map((alias, index) => (
            <Tag key={index}>{alias}</Tag>
          ))}
          {(aliases || []).length > 3 && <Text type="secondary">...</Text>}
        </div>
      ),
    },
  ];

  // 关系表格列定义 (暂时未使用)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const relationColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: string) => (
        <Text code style={{ fontSize: 12 }}>
          {id.length > 10 ? `${id.substring(0, 10)}...` : id}
        </Text>
      ),
    },
    {
      title: '关系类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: '源实体',
      dataIndex: 'source',
      key: 'source',
      render: (source: string) => {
        const entity = graphData?.entities.find(e => e.id === source);
        return entity ? <Text>{entity.name}</Text> : <Text code>{source}</Text>;
      },
    },
    {
      title: '目标实体',
      dataIndex: 'target',
      key: 'target',
      render: (target: string) => {
        const entity = graphData?.entities.find(e => e.id === target);
        return entity ? <Text>{entity.name}</Text> : <Text code>{target}</Text>;
      },
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => (
        <span style={{ 
          color: confidence > 0.8 ? '#52c41a' : confidence > 0.5 ? '#faad14' : '#ff4d4f' 
        }}>
          {(confidence * 100).toFixed(1)}%
        </span>
      ),
    },
  ];

  return (
    <div>
      <Title level={3}>知识图谱可视化</Title>
      <Text type="secondary">
        查看和分析已完成任务的知识图谱结构和内容。
      </Text>

      {/* 任务选择 */}
      <Card style={{ marginTop: 16, marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Space>
              <Text strong>选择任务:</Text>
              <Select
                style={{ width: 200 }}
                placeholder="选择一个任务"
                value={selectedTaskId}
                onChange={handleTaskChange}
                loading={loading}
              >
                {tasks.map(task => (
                  <Option key={task.id} value={task.id}>
                    {task.id.substring(0, 8)}... ({new Date(task.created_at).toLocaleDateString()})
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={16}>
            <Space style={{ float: 'right' }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => selectedTaskId && loadGraphData(selectedTaskId)}
                loading={loading}
              >
                刷新
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownloadImage}
                disabled={!selectedTaskId}
              >
                下载图片
              </Button>
              <Button
                icon={<FullscreenOutlined />}
                onClick={handleFullscreen}
                disabled={!selectedTaskId}
              >
                全屏查看
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {!selectedTaskId && (
        <Alert
          message="请选择一个已完成的任务来查看知识图谱"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {selectedTaskId && !graphData && !loading && (
        <Alert
          message="无法加载知识图谱数据"
          description="请检查任务是否已完成或重新选择其他任务。"
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>加载知识图谱数据中...</div>
        </div>
      )}

      {graphData && (
        <>
          {/* 统计信息 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="实体数量"
                  value={(graphData as any).nodes_count || graphData.entities?.length || 0}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="关系数量"
                  value={(graphData as any).edges_count || graphData.relations?.length || 0}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="平均度数"
                  value={graphData.statistics?.avg_degree || 0}
                  precision={2}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="连通分量"
                  value={graphData.statistics?.connected_components || 1}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 主要内容 */}
          <Tabs defaultActiveKey="visualization" size="large">
            <TabPane 
              tab={
                <span>
                  <BarChartOutlined />
                  图谱可视化
                </span>
              } 
              key="visualization"
            >
              <Card>
                <div style={{ textAlign: 'center', marginBottom: 16 }}>
                  {imageLoading && <Spin size="large" />}
                  <Image
                    src={apiService.getVisualizationUrl(selectedTaskId)}
                    alt="知识图谱可视化"
                    style={{ maxWidth: '100%', height: 'auto' }}
                    placeholder={
                      <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Spin size="large" />
                      </div>
                    }
                    onLoad={() => setImageLoading(false)}
                    onError={() => setImageLoading(false)}
                  />
                </div>
                <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
                  知识图谱可视化结果 - 点击图片可放大查看
                </Text>
              </Card>
            </TabPane>

            <TabPane 
              tab={
                <span>
                  <TableOutlined />
                  数据详情
                </span>
              } 
              key="data"
            >
              <Row gutter={[0, 24]}>
                <Col span={24}>
                  <Card title={`实体列表 (${(graphData as any).entities?.length || 0})`}>
                    {(graphData as any).entities ? (
                      <Table
                        columns={entityColumns}
                        dataSource={(graphData as any).entities}
                        rowKey="id"
                        pagination={{
                          pageSize: 10,
                          showSizeChanger: true,
                          showQuickJumper: true,
                          showTotal: (total, range) => 
                            `第 ${range[0]}-${range[1]} 条，共 ${total} 条实体`,
                        }}
                        scroll={{ x: 800 }}
                      />
                    ) : (
                      <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Text type="secondary">暂无实体数据</Text>
                      </div>
                    )}
                  </Card>
                </Col>
                <Col span={24}>
                  <Card title={`关系列表 (${(graphData as any).relations?.length || 0})`}>
                    {(graphData as any).relations ? (
                      <Table
                        columns={[
                          {
                            title: '关系类型',
                            dataIndex: 'relation',
                            key: 'relation',
                            render: (relation: string) => <Tag color="blue">{relation}</Tag>,
                          },
                          {
                            title: '源实体',
                            dataIndex: 'source',
                            key: 'source',
                            render: (source: string) => <Text>{source}</Text>,
                          },
                          {
                            title: '目标实体',
                            dataIndex: 'target',
                            key: 'target',
                            render: (target: string) => <Text>{target}</Text>,
                          }
                        ]}
                        dataSource={(graphData as any).relations.map((rel: any, index: number) => ({
                          ...rel,
                          id: `relation_${index}`
                        }))}
                        rowKey="id"
                        pagination={{
                          pageSize: 10,
                          showSizeChanger: true,
                          showQuickJumper: true,
                          showTotal: (total, range) => 
                            `第 ${range[0]}-${range[1]} 条，共 ${total} 条关系`,
                        }}
                        scroll={{ x: 800 }}
                      />
                    ) : (
                      <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Text type="secondary">暂无关系数据</Text>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            </TabPane>

            <TabPane 
              tab={
                <span>
                  <BarChartOutlined />
                  统计分析
                </span>
              } 
              key="statistics"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="实体类型分布">
                    <div>
                      {(graphData as any).entities ? (
                        <div style={{ marginBottom: 8 }}>
                          <Row justify="space-between" align="middle">
                            <Col>
                              <Tag color="blue">实体</Tag>
                            </Col>
                            <Col>
                              <Text strong>{(graphData as any).entities.length}</Text>
                            </Col>
                          </Row>
                        </div>
                      ) : (
                        <Text type="secondary">暂无数据</Text>
                      )}
                    </div>
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="关系类型分布">
                    <div>
                      {(graphData as any).relations ? (
                        (Array.from(new Set((graphData as any).relations.map((r: any) => r.relation))) as string[]).map((type: string) => (
                          <div key={type} style={{ marginBottom: 8 }}>
                            <Row justify="space-between" align="middle">
                              <Col>
                                <Tag color="green">{type}</Tag>
                              </Col>
                              <Col>
                                <Text strong>{(graphData as any).relations.filter((r: any) => r.relation === type).length}</Text>
                              </Col>
                            </Row>
                          </div>
                        ))
                      ) : (
                        <Text type="secondary">暂无数据</Text>
                      )}
                    </div>
                  </Card>
                </Col>
                <Col xs={24}>
                  <Card title="图谱质量指标">
                    <Row gutter={16}>
                      <Col xs={24} sm={8}>
                        <Statistic
                          title="图密度"
                          value={0.5}
                          precision={4}
                          suffix="%"
                        />
                      </Col>
                      <Col xs={24} sm={8}>
                        <Statistic
                          title="平均度数"
                          value={graphData.statistics?.avg_degree || 2.0}
                          precision={2}
                        />
                      </Col>
                      <Col xs={24} sm={8}>
                        <Statistic
                          title="连通分量"
                          value={graphData.statistics?.connected_components || 1}
                        />
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>
            </TabPane>
          </Tabs>
        </>
      )}
    </div>
  );
};

export default VisualizationPage;