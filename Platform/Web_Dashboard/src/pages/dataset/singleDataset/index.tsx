import { useDatasetById, useDeleteDataset, useUpdateDataset } from 'hooks/datasets';
import { useGroups } from 'hooks/groups';
import { useNavigate, useParams } from 'react-router-dom';
import { useQueryParams } from '../../../hooks/routing';
import { AddDataset } from '../../../api/models';
import { DatasetForm } from '../DatasetForm';
import { DatasetView } from '../DatasetView';
import { Spin } from 'antd';
import { goToViewMode } from 'utils/nav';

type ViewMode = 'edit' | 'view';

const SingleDataset: React.FC = () => {
    const { id: datasetId } = useParams<{ id: string }>();
    const { value: version } = useQueryParams<number>('version', -1);

    const navigate = useNavigate();
    const { value: mode, searchParams, setSearchParams } = useQueryParams<ViewMode>('mode', 'view');
    const setMode = (newMode: ViewMode) => {
        searchParams.set('mode', newMode);
        setSearchParams(searchParams);
    };

    const { data: selectedDataset, isLoading: datasetLoading } = useDatasetById(datasetId, version);
    const { data: groups, isLoading: groupsLoading } = useGroups();
    const updateDataset = useUpdateDataset();

    const loading = datasetLoading || groupsLoading;

    if (!selectedDataset && !datasetLoading) {
        return (
            <div className='flex flex-col items-center justify-center h-full'>
                <div>Dataset not found</div>
            </div>
        );
    }

    const handleFormSubmit = (values: AddDataset) => {
        if (!selectedDataset) {
            console.error('Form submit but dataset not loaded');
            return;
        }
        updateDataset.mutate(
            { datasetId: selectedDataset._governance_id, values },
            {
                onSuccess: () => goToViewMode(searchParams, setSearchParams, selectedDataset),
            },
        );
    };

    return (
        <div>
            {mode === 'edit' && (
                <DatasetForm
                    initialValues={selectedDataset}
                    groups={groups ?? []}
                    onSubmit={handleFormSubmit}
                    onCancel={() => setMode('view')}
                    loading={loading}
                />
            )}
            {mode === 'view' && (
                <Spin spinning={datasetLoading}>
                    {selectedDataset && (
                        <DatasetView
                            dataset={selectedDataset}
                            onEdit={() => setMode('edit')}
                            onBack={() => navigate('..', { relative: 'path' })}
                        />
                    )}
                </Spin>
            )}
        </div>
    );
};

export default SingleDataset;
