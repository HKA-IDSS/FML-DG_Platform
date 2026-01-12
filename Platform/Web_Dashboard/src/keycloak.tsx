import { Error403 } from 'components/error/Error403';
import Keycloak from 'keycloak-js';
import { useKeycloak } from 'keycloak-react-web';

/**
 * @description Wrapper for a react node that is only rendered if the user is authenticated
 */
export const PrivateRoute = ({ children }: { children: any }) => {
    const { keycloak } = useKeycloak();
    const isLoggedIn = keycloak.authenticated;
    return isLoggedIn ? children : null;
};

/**
 * @description Wrapper for a react node that is only rendered if the user is admin
 */
export const PrivateAdminRoute = ({ children }: { children: any }) => {
    const { keycloak } = useKeycloak();
    const isLoggedIn = keycloak.authenticated && keycloak.hasRealmRole('admin');
    return isLoggedIn ? children : <Error403 />;
};

/**
 * @description Keycloak instance
 */
export const keycloak = new Keycloak({
    // url: 'http://kc:8080/auth',
    url: 'http://localhost/auth',
    realm: 'fml',
    clientId: 'fml-webapp',
});
