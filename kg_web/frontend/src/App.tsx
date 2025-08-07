import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, ConfigProvider } from 'antd';
import { 
  HomeOutlined, 
  SettingOutlined, 
  ProjectOutlined, 
  BarChartOutlined 
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';

import HomePage from './pages/HomePage';
import ConfigPage from './pages/ConfigPage';
import TasksPage from './pages/TasksPage';
import VisualizationPage from './pages/VisualizationPage';
import TestPage from './TestPage';

import './App.css';

const { Header, Sider, Content } = Layout;

function App() {
  const [collapsed, setCollapsed] = React.useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: '配置管理',
    },
    {
      key: '/tasks',
      icon: <ProjectOutlined />,
      label: '任务管理',
    },
    {
      key: '/visualization',
      icon: <BarChartOutlined />,
      label: '图谱可视化',
    },
  ];

  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Sider 
            collapsible 
            collapsed={collapsed} 
            onCollapse={setCollapsed}
            theme="dark"
          >
            <div className="logo">
              <h3 style={{ color: 'white', textAlign: 'center', margin: '16px 0' }}>
                {collapsed ? 'KG' : '知识图谱'}
              </h3>
            </div>
            <Menu
              theme="dark"
              mode="inline"
              defaultSelectedKeys={['/']}
              items={menuItems}
              onClick={({ key }) => {
                window.location.href = key;
              }}
            />
          </Sider>
          <Layout className="site-layout">
            <Header 
              className="site-layout-background" 
              style={{ 
                padding: '0 24px',
                background: '#fff',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
            >
              <h2 style={{ margin: 0, color: '#1890ff' }}>
                知识图谱构建系统
              </h2>
            </Header>
            <Content
              className="site-layout-background"
              style={{
                margin: '24px 16px',
                padding: 24,
                minHeight: 280,
                background: '#fff',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
            >
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/test" element={<TestPage />} />
                <Route path="/config" element={<ConfigPage />} />
                <Route path="/tasks" element={<TasksPage />} />
                <Route path="/visualization" element={<VisualizationPage />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;