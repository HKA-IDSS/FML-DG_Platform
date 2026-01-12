import {
    ClockCircleOutlined,
    DatabaseOutlined,
    FolderOpenOutlined,
    HomeOutlined,
    MergeOutlined,
    RadarChartOutlined,
    StarOutlined,
    UserOutlined,
    UsergroupAddOutlined,
    SearchOutlined,
    LineChartOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import { Menu, MenuProps } from 'antd';
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { APP_ROUTES } from '../../app.routes';
import { keycloak } from 'keycloak';

export const LayoutSidebarMenu: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isAdmin, setIsAdmin] = useState<boolean | null>(null);

    const ROUTES: MenuProps['items'] = [
        {
            key: '/',
            icon: React.createElement(HomeOutlined),
            label: <a onClick={(e) => navigate('/')}>Home</a>,
        },
        // {
        //     key: '/favorites',
        //     icon: React.createElement(StarOutlined),
        //     label: <a onClick={(e) => navigate('/favorites')}>Favorites</a>,
        // },
        // {
        //     key: '/recently',
        //     icon: React.createElement(ClockCircleOutlined),
        //     label: <a onClick={(e) => navigate('/recently')}>Recent</a>,
        // },
        {
            key: '/master-data',
            icon: React.createElement(DatabaseOutlined),
            label: 'Master Data',
            children: [
                {
                    key: '/master-data/strategies',
                    icon: React.createElement(MergeOutlined),
                    label: <a onClick={(e) => navigate('/master-data/strategies')}>Strategies</a>,
                },
                {
                    key: '/master-data/mlmodels',
                    icon: React.createElement(RadarChartOutlined),
                    label: <a onClick={(e) => navigate('/master-data/mlmodels')}>ML Models</a>,
                },
                {
                    key: '/master-data/datasets',
                    icon: React.createElement(FolderOpenOutlined),
                    label: <a onClick={(e) => navigate('/master-data/datasets')}>Datasets</a>,
                },
                {
                    key: '/master-data/groups',
                    icon: React.createElement(UsergroupAddOutlined),
                    label: <a onClick={(e) => navigate('/master-data/groups')}>Groups</a>,
                },
                {
                    key: '/master-data/compare',
                    icon: React.createElement(SearchOutlined),
                    label: <a onClick={(e) => navigate('/master-data/compare')}>Compare</a>,
                },
                {
                    key: '/master-data/results',
                    icon: React.createElement(LineChartOutlined),
                    label: <a onClick={(e) => navigate('/master-data/results')}>Results</a>,
                }
            ],
        },
        {
            key: '/user',
            icon: React.createElement(UserOutlined),
            label: <a onClick={(e) => navigate('/user')}>User</a>,
        },
        {
            key: '/admin',
            icon: React.createElement(SettingOutlined),
            label: <a onClick={(e) => navigate('/admin')}>Admin Settings</a>,
            style: { display: isAdmin ? 'block' : 'none' },
        },
    ];

    const getAssociatedPaths = () => {
        const firstSlug = location?.pathname.split('/')[1];
        const matchedMainRoute = APP_ROUTES.find((route) => route.path?.slice(1) === firstSlug);
        if (matchedMainRoute) return [matchedMainRoute.path || '/', location.pathname];
        return undefined;
    };

    // Role check only possible after Keycloak is initialized
    // and user is authenticated, so we use an interval to check periodically
    useEffect(() => {
        const checkAdminRole = () => {
            if (keycloak.authenticated) {
                const admin = keycloak.hasRealmRole('admin');
                setIsAdmin(admin);
            } else {
                setIsAdmin(null);
            }
        };

        let timer: number | null = null;
        if (isAdmin === null) {
            timer = window.setInterval(() => checkAdminRole(), 50);
        }

        return () => window.clearInterval(timer!);
    }, [keycloak, isAdmin]);

    return (
        <>
            <Menu
                mode='inline'
                selectedKeys={getAssociatedPaths()}
                defaultOpenKeys={getAssociatedPaths()}
                style={{ height: '100%', borderRight: 0 }}
                items={ROUTES}
            />
        </>
    );
};
