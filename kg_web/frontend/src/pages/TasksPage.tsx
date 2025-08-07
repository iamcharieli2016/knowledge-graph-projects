import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Tag,
  Progress,
  message,
  Popconfirm,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Modal,
  Descriptions,
  Alert
} from 'antd';
import {
  ReloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  ProjectOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';
import { Task } from '../types';

const { Title, Text } = Typography;

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  useEffect(() => {
    loadTasks();
    // 设置定时刷新
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await apiService.getAllTasks();
      const tasksWithMessage = data.tasks.map(task => ({
        ...task,
        message: task.status === 'completed' ? '任务已完成' : 
                task.status === 'pending' ? '等待处理' :
                task.status.startsWith('processing_') ? `正在${task.status.replace('processing_', '')}` : task.status
      }));
      setTasks(tasksWithMessage.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
    } catch (error) {
      console.error('加载任务失败:', error);
      message.error('加载任务失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await apiService.deleteTask(taskId);
      message.success('任务删除成功');
      loadTasks();
    } catch (error) {
      console.error('删除任务失败:', error);
      message.error('删除任务失败');
    }
  };

  const handleViewDetails = (task: Task) => {
    setSelectedTask(task);
    setDetailModalVisible(true);
  };

  const handleViewVisualization = (taskId: string) => {
    window.open(`/visualization?taskId=${taskId}`, '_blank');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'running':
        return <PlayCircleOutlined style={{ color: '#1890ff' }} />;
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const getStatusTag = (status: string) => {
    let statusConfig;
    
    if (status === 'completed') {
      statusConfig = { color: 'green', text: '已完成' };
    } else if (status === 'pending') {
      statusConfig = { color: 'orange', text: '等待中' };
    } else if (status === 'failed') {
      statusConfig = { color: 'red', text: '失败' };
    } else if (status.startsWith('processing_')) {
      statusConfig = { color: 'blue', text: '运行中' };
    } else {
      statusConfig = { color: 'default', text: status };
    }

    return (
      <Tag color={statusConfig.color} icon={getStatusIcon(status.startsWith('processing_') ? 'running' : status)}>
        {statusConfig.text}
      </Tag>
    );
  };

  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: string) => (
        <Text code style={{ fontSize: 12 }}>
          {id.substring(0, 8)}...
        </Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number, record: Task) => (
        <Progress 
          percent={progress} 
          size="small" 
          status={record.status === 'failed' ? 'exception' : 'active'}
        />
      ),
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: string) => (
        <Text style={{ fontSize: 13 }}>{message}</Text>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time: string) => (
        <Text style={{ fontSize: 12 }}>
          {new Date(time).toLocaleString()}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: Task) => (
        <Space size="small">
          <Button 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
          >
            详情
          </Button>
          {record.status === 'completed' && (
            <Button 
              size="small" 
              type="primary"
              onClick={() => handleViewVisualization(record.id)}
            >
              查看图谱
            </Button>
          )}
          <Popconfirm
            title="确定要删除这个任务吗？"
            onConfirm={() => handleDeleteTask(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              size="small" 
              danger 
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 统计信息
  const getStatistics = () => {
    const stats = {
      total: tasks.length,
      pending: tasks.filter(t => t.status === 'pending').length,
      running: tasks.filter(t => t.status.startsWith('processing_')).length,
      completed: tasks.filter(t => t.status === 'completed').length,
      failed: tasks.filter(t => t.status === 'failed').length,
    };
    return stats;
  };

  const stats = getStatistics();

  return (
    <div>
      <Title level={3}>任务管理</Title>
      <Text type="secondary">
        管理和监控知识图谱构建任务的执行状态和进度。
      </Text>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginTop: 16, marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.total}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.running}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="失败"
              value={stats.failed}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 运行中任务提醒 */}
      {stats.running > 0 && (
        <Alert
          message={`当前有 ${stats.running} 个任务正在运行中`}
          description="页面会自动刷新任务状态，请耐心等待任务完成。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 任务表格 */}
      <Card
        title="任务列表"
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={loadTasks}
            loading={loading}
          >
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          rowClassName={(record) => `task-status-${record.status}`}
        />
      </Card>

      {/* 任务详情模态框 */}
      <Modal
        title="任务详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedTask?.status === 'completed' && (
            <Button
              key="view"
              type="primary"
              onClick={() => {
                handleViewVisualization(selectedTask.id);
                setDetailModalVisible(false);
              }}
            >
              查看图谱
            </Button>
          ),
        ].filter(Boolean)}
        width={800}
      >
        {selectedTask && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="任务ID">
                <Text code>{selectedTask.id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedTask.status)}
              </Descriptions.Item>
              <Descriptions.Item label="进度">
                <Progress 
                  percent={selectedTask.progress} 
                  status={selectedTask.status === 'failed' ? 'exception' : 'active'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(selectedTask.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="当前消息" span={2}>
                {selectedTask.message}
              </Descriptions.Item>
            </Descriptions>

            {selectedTask.error && (
              <Alert
                message="错误信息"
                description={selectedTask.error}
                type="error"
                style={{ marginTop: 16 }}
                showIcon
              />
            )}

            {selectedTask.results && (
              <Card title="结果统计" style={{ marginTop: 16 }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="实体数量"
                      value={selectedTask.results.statistics.entity_count}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="关系数量"
                      value={selectedTask.results.statistics.relation_count}
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="平均度数"
                      value={selectedTask.results.statistics.avg_degree}
                      precision={2}
                      valueStyle={{ color: '#faad14' }}
                    />
                  </Col>
                </Row>
              </Card>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TasksPage;