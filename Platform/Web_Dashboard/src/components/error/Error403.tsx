import { Button, Result } from 'antd';
import React from 'react';
import { useNavigate } from 'react-router-dom';

export const Error403: React.FC = () => {
    const navigate = useNavigate();
    return (
        <div className='h-full flex flex-col justify-center'>
            <Result
                status='403'
                title='403'
                subTitle='Sorry, you have not the permissions to visit this page.'
                extra={
                    <Button type='primary' onClick={() => navigate('/')}>
                        Back Home
                    </Button>
                }
            />
        </div>
    );
};
