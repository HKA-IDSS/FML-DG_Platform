import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { Avatar, Dropdown, MenuProps, theme } from 'antd';
import { keycloak } from '../../keycloak';
import logo from '../../logo.svg';
import React from 'react';
const items: MenuProps['items'] = [
    {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: (
            <a
                onClick={(e) => {
                    e.preventDefault();
                    keycloak.logout();
                }}
            >
                Log Out
            </a>
        ),
    },
];

export const LayoutHeader: React.FC = () => {
    const [userName, setUserName] = React.useState<string>();

    const {
        token: { colorPrimary },
    } = theme.useToken();

    React.useEffect(() => {
        const getUser = async () => {
            if (keycloak.authenticated) {
                await keycloak
                    .loadUserProfile()
                    .then((res) => {
                        setUserName(res?.username);
                    })
                    .catch(() => {
                        setTimeout(() => getUser(), 50);
                    });
            } else {
                setTimeout(() => getUser(), 50);
            }
        };
        getUser();
    }, []);

    return (
        <>
            <div className='flex gap-x-2 items-center'>
                <img src={logo} className='w-5 h-5' alt='logo' />
                <span className='text-gray-200 font-semibold'>Federated Machine Learning</span>
            </div>
            <div className='flex grow items-center justify-end'>
                <Dropdown menu={{ items }} placement='bottomRight' arrow>
                    <div className='flex items-center gap-x-3'>
                        {<span className='text-gray-200 font-semibold'>{userName}</span>}
                        <Avatar
                            className=' cursor-pointer'
                            style={{ backgroundColor: colorPrimary }}
                            shape='square'
                            icon={<UserOutlined />}
                        />
                    </div>
                </Dropdown>
            </div>
        </>
    );
};
