import { RouteObject, createBrowserRouter } from 'react-router-dom';
import App from './App';
import { PrivateAdminRoute, PrivateRoute } from './keycloak';
import DatasetsFunctional from './pages/dataset';
import Favorites from './pages/favorites';
import GroupsFunctional from './pages/groups';
import Home from './pages/home';
import MLModelsFunctional from './pages/mlmodels';
import Recently from './pages/recently';
import StrategiesFunctional from './pages/strategy';
import UserFunctional from './pages/user';
import { Error404 } from './components/error/Error404';
import { ComparisonPage } from 'pages/comparison';
import ResultsPage from './pages/results';
import AdminPage from 'pages/admin';
import Proposal from './pages/strategy/proposal';
import SingleStrategyView from './pages/strategy/singleStrategy';
import SingleMlModel from './pages/mlmodels/singleMLModel';
import SingleDataset from './pages/dataset/singleDataset';
import SingleGroupView from './pages/groups/singleGroup';

export const APP_ROUTES: RouteObject[] = [
    {
        path: '/',
        element: (
            <PrivateRoute>
                <Home />
            </PrivateRoute>
        ),
    },
    // {
    //     path: '/favorites',
    //     element: (
    //         <PrivateRoute>
    //             <Favorites />
    //         </PrivateRoute>
    //     ),
    // },
    // {
    //     path: '/recently',
    //     element: (
    //         <PrivateRoute>
    //             <Recently />
    //         </PrivateRoute>
    //     ),
    // },
    {
        path: '/master-data',
        children: [
            {
                path: '/master-data/strategies',
                element: (
                    <PrivateRoute>
                        <StrategiesFunctional />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/strategies/:id',
                element: (
                    <PrivateRoute>
                        <SingleStrategyView />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/strategies/:id/proposal',
                element: (
                    <PrivateRoute>
                        <Proposal />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/mlmodels',
                element: (
                    <PrivateRoute>
                        <MLModelsFunctional />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/mlmodels/:id',
                element: (
                    <PrivateRoute>
                        <SingleMlModel />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/datasets',
                element: (
                    <PrivateRoute>
                        <DatasetsFunctional />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/datasets/:id',
                element: (
                    <PrivateRoute>
                        <SingleDataset />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/groups',
                element: (
                    <PrivateRoute>
                        <GroupsFunctional />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/groups/:id',
                element: (
                    <PrivateRoute>
                        <SingleGroupView />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/compare',
                element: (
                    <PrivateRoute>
                        <ComparisonPage />
                    </PrivateRoute>
                ),
            },
            {
                path: '/master-data/results',
                element: (
                    <PrivateRoute>
                        <ResultsPage />
                    </PrivateRoute>
                ),
            },
        ],
    },
    {
        path: '/user',
        element: (
            <PrivateRoute>
                <UserFunctional />
            </PrivateRoute>
        ),
    },
    {
        path: '/admin',
        element: (
            <PrivateAdminRoute>
                <AdminPage />
            </PrivateAdminRoute>
        ),
    },
];

export const APP_ROUTER = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        errorElement: <Error404 />,
        children: APP_ROUTES,
    },
]);
