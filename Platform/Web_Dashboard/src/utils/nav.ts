import { MongoIDAndVersion } from 'api/models';
import { NavigateFunction } from 'react-router-dom';

export const goToViewMode = (
    searchParams: URLSearchParams,
    setSearchParams: (params: URLSearchParams) => void,
    entity: MongoIDAndVersion,
) => {
    searchParams.set('mode', 'view');
    const nextVersion = entity._version + 1;
    searchParams.set('version', nextVersion.toString());
    setSearchParams(searchParams);
};

export const goBack = (navigate: NavigateFunction) => {
    navigate('..', { relative: 'path' });
};
