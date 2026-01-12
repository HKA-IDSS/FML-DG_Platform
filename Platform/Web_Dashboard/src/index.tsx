import { StyleProvider } from '@ant-design/cssinjs';
import { ConfigProvider } from 'antd';
import { KeycloakProvider } from 'keycloak-react-web';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { APP_ROUTER } from './app.routes';
import './index.css';
import { keycloak } from './keycloak';
import reportWebVitals from './reportWebVitals';

const root = createRoot(document.getElementById('root') as HTMLElement);
root.render(
    <KeycloakProvider client={keycloak as any} initOptions={{ onLoad: 'login-required', checkLoginIframe: false }}>
        <ConfigProvider theme={{ token: { colorPrimary: '#43cdf0' } }}>
            <StyleProvider hashPriority='high'>
                <RouterProvider router={APP_ROUTER} />
            </StyleProvider>
        </ConfigProvider>
    </KeycloakProvider>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
