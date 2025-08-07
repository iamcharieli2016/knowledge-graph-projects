import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  InputNumber,
  Switch,
  Button,
  message,
  Row,
  Col,
  Typography,
  Select,
  Spin,
  Alert,
  Space,
  Tooltip,
  Input
} from 'antd';
import { SaveOutlined, ReloadOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import { Config } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

const ConfigPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<Config | null>(null);

  useEffect(() => {
    loadConfig();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadConfig = async () => {
    setLoading(true);
    try {
      const data = await apiService.getConfig();
      setConfig(data);
      form.setFieldsValue(data);
    } catch (error) {
      console.error('加载配置失败:', error);
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      await apiService.updateConfig(values);
      setConfig(values);
      message.success('配置保存成功！');
    } catch (error) {
      console.error('保存配置失败:', error);
      message.error('保存配置失败');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (config) {
      form.setFieldsValue(config);
      message.info('配置已重置');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载配置中...</div>
      </div>
    );
  }

  return (
    <div>
      <Title level={3}>系统配置管理</Title>
      <Text type="secondary">
        调整知识图谱构建的各项参数，配置会实时保存并应用到后续任务中。
      </Text>
      
      <Alert
        message="配置说明"
        description="修改配置后请点击保存按钮。配置参数会影响知识抽取的准确性和性能，建议根据具体业务需求调整。"
        type="info"
        showIcon
        style={{ margin: '16px 0' }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
      >
        {/* 知识抽取配置 */}
        <Card title="知识抽取配置" className="config-section">
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    相似度阈值
                    <Tooltip title="用于判断实体相似性的阈值，值越高要求越严格">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['extraction', 'similarity_threshold']}
                rules={[{ required: true, message: '请输入相似度阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.8"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    最小实体长度
                    <Tooltip title="实体名称的最小字符数">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['extraction', 'min_entity_length']}
                rules={[{ required: true, message: '请输入最小实体长度' }]}
              >
                <InputNumber
                  min={1}
                  max={10}
                  style={{ width: '100%' }}
                  placeholder="2"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    最小置信度
                    <Tooltip title="实体抽取的最小置信度要求">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['extraction', 'min_confidence']}
                rules={[{ required: true, message: '请输入最小置信度' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.5"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    上下文窗口大小
                    <Tooltip title="实体抽取时考虑的上下文字符数">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['extraction', 'max_context_window']}
                rules={[{ required: true, message: '请输入上下文窗口大小' }]}
              >
                <InputNumber
                  min={10}
                  max={200}
                  style={{ width: '100%' }}
                  placeholder="50"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label="使用模式匹配"
                name={['extraction', 'use_patterns']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label="使用词性标注"
                name={['extraction', 'use_pos_tagging']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label="使用字典匹配"
                name={['extraction', 'use_dictionary']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 知识映射配置 */}
        <Card title="知识映射配置" className="config-section">
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    实体相似度阈值
                    <Tooltip title="实体映射时的相似度判断阈值">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['mapping', 'entity_similarity_threshold']}
                rules={[{ required: true, message: '请输入实体相似度阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.8"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    关系相似度阈值
                    <Tooltip title="关系映射时的相似度判断阈值">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['mapping', 'relation_similarity_threshold']}
                rules={[{ required: true, message: '请输入关系相似度阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.7"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    模糊匹配阈值
                    <Tooltip title="模糊匹配的相似度阈值">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['mapping', 'fuzzy_match_threshold']}
                rules={[{ required: true, message: '请输入模糊匹配阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.6"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} sm={12}>
              <Form.Item
                label="使用语义映射"
                name={['mapping', 'use_semantic_mapping']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                label="使用上下文映射"
                name={['mapping', 'use_context_mapping']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 知识融合配置 */}
        <Card title="知识融合配置" className="config-section">
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    实体融合阈值
                    <Tooltip title="实体融合时的相似度阈值">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['fusion', 'entity_fusion_threshold']}
                rules={[{ required: true, message: '请输入实体融合阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.8"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    关系融合阈值
                    <Tooltip title="关系融合时的相似度阈值">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['fusion', 'relation_fusion_threshold']}
                rules={[{ required: true, message: '请输入关系融合阈值' }]}
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                  placeholder="0.8"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    冲突解决策略
                    <Tooltip title="当出现知识冲突时的解决策略">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['fusion', 'conflict_resolution_strategy']}
                rules={[{ required: true, message: '请选择冲突解决策略' }]}
              >
                <Select style={{ width: '100%' }} placeholder="选择策略">
                  <Option value="highest_confidence">最高置信度</Option>
                  <Option value="latest">最新信息</Option>
                  <Option value="vote">投票决定</Option>
                  <Option value="manual_review">人工审核</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} sm={12}>
              <Form.Item
                label="合并相似实体"
                name={['fusion', 'merge_similar_entities']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                label="保留数据来源"
                name={['fusion', 'preserve_provenance']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 可视化配置 */}
        <Card title="可视化配置" className="config-section">
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    最大节点数
                    <Tooltip title="可视化图中显示的最大节点数量">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['visualization', 'max_nodes']}
                rules={[{ required: true, message: '请输入最大节点数' }]}
              >
                <InputNumber
                  min={10}
                  max={500}
                  style={{ width: '100%' }}
                  placeholder="50"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    节点大小
                    <Tooltip title="图中节点的大小">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['visualization', 'node_size']}
                rules={[{ required: true, message: '请输入节点大小' }]}
              >
                <InputNumber
                  min={100}
                  max={2000}
                  style={{ width: '100%' }}
                  placeholder="500"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    边宽度
                    <Tooltip title="图中连线的宽度">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['visualization', 'edge_width']}
                rules={[{ required: true, message: '请输入边宽度' }]}
              >
                <InputNumber
                  min={0.5}
                  max={10}
                  step={0.5}
                  style={{ width: '100%' }}
                  placeholder="1.0"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label={
                  <Space>
                    布局算法
                    <Tooltip title="图的布局算法">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                name={['visualization', 'layout']}
                rules={[{ required: true, message: '请选择布局算法' }]}
              >
                <Select style={{ width: '100%' }} placeholder="选择布局">
                  <Option value="spring">弹簧布局</Option>
                  <Option value="circular">圆形布局</Option>
                  <Option value="random">随机布局</Option>
                  <Option value="kamada_kawai">KK布局</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Form.Item
                label="输出格式"
                name={['visualization', 'output_format']}
                rules={[{ required: true, message: '请选择输出格式' }]}
              >
                <Select style={{ width: '100%' }} placeholder="选择格式">
                  <Option value="png">PNG</Option>
                  <Option value="svg">SVG</Option>
                  <Option value="pdf">PDF</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 其他配置 */}
        <Card title="其他配置" className="config-section">
          <Row gutter={24}>
            <Col xs={24} sm={12}>
              <Form.Item
                label="输出目录"
                name="output_dir"
                rules={[{ required: true, message: '请输入输出目录' }]}
              >
                <Input placeholder="output" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                label="日志级别"
                name="log_level"
                rules={[{ required: true, message: '请选择日志级别' }]}
              >
                <Select style={{ width: '100%' }} placeholder="选择级别">
                  <Option value="DEBUG">DEBUG</Option>
                  <Option value="INFO">INFO</Option>
                  <Option value="WARNING">WARNING</Option>
                  <Option value="ERROR">ERROR</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 操作按钮 */}
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Space size="large">
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
              size="large"
            >
              保存配置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
              size="large"
            >
              重置配置
            </Button>
          </Space>
        </div>
      </Form>
    </div>
  );
};

export default ConfigPage;