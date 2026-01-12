import { Layout, theme } from 'antd';
import React from 'react';

import { LayoutBreadcrumb } from './components/layout/LayoutBreadcrumb';
import { LayoutHeader } from './components/layout/LayoutHeader';
import { LayoutSidebarMenu } from './components/layout/LayoutSidebarMenu';
import { Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const { Header, Content, Sider } = Layout;
const queryClient = new QueryClient();

const App: React.FC = () => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return (
        <QueryClientProvider client={queryClient}>
            <Layout className='h-full'>
                <Header className='flex'>
                    <LayoutHeader />
                </Header>
                <Layout>
                    <Sider width={200} style={{ background: colorBgContainer }}>
                        <LayoutSidebarMenu />
                    </Sider>
                    <Layout style={{ padding: '0 24px 24px' }}>
                        <LayoutBreadcrumb />
                        <Content
                            style={{
                                padding: 24,
                                margin: 0,
                                minHeight: 280,
                                overflowY: 'scroll',

                                background: colorBgContainer,
                                borderRadius: borderRadiusLG,
                            }}
                        >
                            <Outlet />
                        </Content>
                    </Layout>
                </Layout>
            </Layout>
            <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
    );
};

export default App;
