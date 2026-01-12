import { useDeleteMLModel, useMLModelById, useUpdateMLModel } from '../../../hooks/mlmodels';
import { AddMLModel, MLModel } from '../../../api/models';
import { useNavigate, useParams } from 'react-router-dom';
import { MLModelForm } from '../MLModelForm';
import { MLModelView } from '../MLModelView';
import { Modal, Spin } from 'antd';
import { useQueryParams } from '../../../hooks/routing';
import { goToViewMode } from 'utils/nav';

type ViewMode = 'edit' | 'view';

const SingleMlModel: React.FC = () => {
    const deleteMLModel = useDeleteMLModel();
    const updateMLModel = useUpdateMLModel();

    // routing
    const navigate = useNavigate();
    const { id: modelId } = useParams();
    const { value: version } = useQueryParams<number>('version', -1);
    const { data, isLoading } = useMLModelById(modelId, version);

    const { value: mode, searchParams, setSearchParams } = useQueryParams<ViewMode>('mode', 'view');
    const setMode = (newMode: ViewMode) => {
        searchParams.set('mode', newMode);
        setSearchParams(searchParams);
    };

    if (!data) {
        return (
            <div className='flex flex-col items-center justify-center h-full'>
                <Spin spinning={isLoading} size='large' />
                {!isLoading && <div>Model not found</div>}
            </div>
        );
    }

    const handleDelete = (model: MLModel) => {
        Modal.confirm({
            title: `Delete model "${model.name}"?`,
            content: 'This action cannot be undone.',
            okText: 'Delete',
            okType: 'danger',
            onOk: () => deleteMLModel.mutate(model._governance_id),
        });
    };

    const handleBack = () => {
        navigate('..', { relative: 'path' });
    };

    const handleFormSubmit = (values: AddMLModel) => {
        updateMLModel.mutate(
            { modelId: data._governance_id, values },
            {
                onSuccess: () => goToViewMode(searchParams, setSearchParams, data),
            },
        );
    };

    return (
        <div>
            {mode === 'view' && data && (
                <MLModelView
                    model={data}
                    onEdit={() => setMode('edit')}
                    onBack={() => handleBack()}
                    onDelete={() => handleDelete(data)}
                />
            )}
            {mode === 'edit' && data && (
                <MLModelForm
                    initialValues={data}
                    onSubmit={handleFormSubmit}
                    onCancel={() => setMode('view')}
                    loading={isLoading}
                />
            )}
        </div>
    );
};

export default SingleMlModel;
