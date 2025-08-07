import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  Input, 
  message, 
  Typography, 
  Alert,
  Space,
  Tag,
  Divider
} from 'antd';
import { 
  RocketOutlined, 
  FileTextOutlined, 
  SettingOutlined,
  BulbOutlined,
  ApiOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';
import { SampleData } from '../types';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [sampleData, setSampleData] = useState<SampleData | null>(null);
  const [inputTexts, setInputTexts] = useState<string>('');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkApiStatus();
    loadSampleData();
  }, []);

  const checkApiStatus = async () => {
    try {
      await apiService.healthCheck();
      setApiStatus('online');
    } catch (error) {
      setApiStatus('offline');
    }
  };

  const loadSampleData = async () => {
    try {
      const data = await apiService.getSampleData();
      setSampleData(data);
      // 设置示例文本到输入框
      setInputTexts(data.texts.slice(0, 3).join('\n\n---\n\n'));
    } catch (error) {
      console.error('获取示例数据失败:', error);
    }
  };

  const handleCreateTask = async () => {
    if (!inputTexts.trim()) {
      message.warning('请输入要处理的文本');
      return;
    }

    setLoading(true);
    try {
      const text = inputTexts.trim();
      await apiService.createTask({ text });
      
      message.success('任务创建成功！');
      
      // 跳转到任务页面
      navigate('/tasks');
    } catch (error) {
      console.error('创建任务失败:', error);
      message.error('创建任务失败，请检查网络连接或后端服务');
    } finally {
      setLoading(false);
    }
  };

  const handleUseSampleData = () => {
    if (sampleData) {
      setInputTexts(sampleData.texts.slice(0, 3).join('\n\n---\n\n'));
      message.info('已加载示例数据');
    }
  };

  return (
    <div>
      {/* 系统状态 */}
      <Alert
        message={
          <Space>
            <ApiOutlined />
            后端服务状态: 
            {apiStatus === 'checking' && <Tag color="processing">检查中...</Tag>}
            {apiStatus === 'online' && <Tag color="success">在线</Tag>}
            {apiStatus === 'offline' && <Tag color="error">离线</Tag>}
          </Space>
        }
        type={apiStatus === 'online' ? 'success' : apiStatus === 'offline' ? 'error' : 'info'}
        style={{ marginBottom: 24 }}
        showIcon
      />

      {/* 欢迎区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={2}>
          <BulbOutlined style={{ color: '#1890ff', marginRight: 8 }} />
          欢迎使用知识图谱构建系统
        </Title>
        <Paragraph>
          这是一个基于Web的知识图谱构建平台，支持从文本中自动抽取实体和关系，
          构建结构化的知识图谱，并提供可视化展示功能。
        </Paragraph>
        
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <FileTextOutlined style={{ fontSize: 24, color: '#52c41a', marginBottom: 8 }} />
              <div><strong>智能抽取</strong></div>
              <div style={{ fontSize: 12, color: '#666' }}>
                从文本中自动识别实体和关系
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <SettingOutlined style={{ fontSize: 24, color: '#1890ff', marginBottom: 8 }} />
              <div><strong>灵活配置</strong></div>
              <div style={{ fontSize: 12, color: '#666' }}>
                支持多种参数和规则配置
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <RocketOutlined style={{ fontSize: 24, color: '#faad14', marginBottom: 8 }} />
              <div><strong>可视化展示</strong></div>
              <div style={{ fontSize: 12, color: '#666' }}>
                直观的知识图谱可视化
              </div>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* 快速开始 */}
      <Card title="快速开始" style={{ marginBottom: 24 }}>
        <Row gutter={24}>
          <Col xs={24} lg={16}>
            <div style={{ marginBottom: 16 }}>
              <Text strong>输入文本内容：</Text>
              <Text type="secondary" style={{ marginLeft: 8 }}>
                （多个文本请用 "---" 分隔）
              </Text>
            </div>
            <TextArea
              value={inputTexts}
              onChange={(e) => setInputTexts(e.target.value)}
              placeholder="请输入要构建知识图谱的文本内容，多个文本请用 --- 分隔"
              rows={12}
              style={{ marginBottom: 16 }}
            />
            <Space>
              <Button 
                type="primary" 
                icon={<RocketOutlined />}
                onClick={handleCreateTask}
                loading={loading}
                size="large"
              >
                开始构建知识图谱
              </Button>
              <Button 
                onClick={handleUseSampleData}
                disabled={!sampleData}
              >
                使用示例数据
              </Button>
            </Space>
          </Col>
          
          <Col xs={24} lg={8}>
            <Card size="small" title="使用说明" style={{ height: '100%' }}>
              <div style={{ fontSize: 14, lineHeight: 1.6 }}>
                <p><strong>步骤1:</strong> 在左侧输入框中输入文本内容</p>
                <p><strong>步骤2:</strong> 多个文本用 "---" 分隔</p>
                <p><strong>步骤3:</strong> 点击"开始构建"按钮</p>
                <p><strong>步骤4:</strong> 在任务管理页面查看进度</p>
                <p><strong>步骤5:</strong> 完成后查看可视化结果</p>
                
                <Divider style={{ margin: '16px 0' }} />
                
                <p><strong>支持的文本类型:</strong></p>
                <ul style={{ paddingLeft: 16, margin: 0 }}>
                  <li>新闻文章</li>
                  <li>学术论文</li>
                  <li>企业介绍</li>
                  <li>人物传记</li>
                  <li>产品说明</li>
                </ul>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* 示例数据预览 */}
      {sampleData && (
        <Card title="示例数据预览">
          <Paragraph>
            系统提供了 <Text strong>{sampleData.texts.length}</Text> 个示例文本，
            涵盖多个领域的内容。
          </Paragraph>
          
          <div style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
            {sampleData.texts.slice(0, 2).map((text, index) => (
              <div key={index} style={{ marginBottom: 12, fontSize: 13, lineHeight: 1.5 }}>
                <Text strong>示例 {index + 1}:</Text>
                <div style={{ marginTop: 4 }}>{text.substring(0, 200)}...</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default HomePage;