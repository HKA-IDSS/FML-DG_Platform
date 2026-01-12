import { useGroups } from '../../../hooks/groups';
import { useStrategyById, useUpdateStrategy } from '../../../hooks/strategies';
import { useNavigate, useParams } from 'react-router-dom';
import { Divider, Spin } from 'antd';
import { StrategyForm, StrategySubmit } from '../StrategyForm';
import { StrategyView } from '../StrategyView';
import { StrategyVote } from '../StrategyVote';
import { useQueryParams } from '../../../hooks/routing';
import { goBack, goToViewMode } from 'utils/nav';

type ViewMode = 'edit' | 'view' | 'vote';

export default function SingleStrategyView() {
    // Compare logic
    const { data: groups, isLoading: isLoadingGroups } = useGroups();
    const updateStrategy = useUpdateStrategy();

    const { id: strategyId } = useParams();
    const { value: version } = useQueryParams<number>('version', -1);
    const { data: selectedStrategy, isLoading } = useStrategyById(strategyId, version);

    // Navigation
    const navigate = useNavigate();
    const { value: mode, searchParams, setSearchParams } = useQueryParams<ViewMode>('mode', 'view');
    const setMode = (newMode: ViewMode) => {
        searchParams.set('mode', newMode);
        setSearchParams(searchParams);
    };

    const handleFormSubmit = (values: StrategySubmit) => {
        if (!(mode === 'edit' && selectedStrategy)) {
            console.error('Form submit in non-edit mode or strategy not loaded');
            return;
        }

        updateStrategy.mutate(
            { strategyId: selectedStrategy._governance_id, values },
            {
                onSuccess: () => goToViewMode(searchParams, setSearchParams, selectedStrategy),
            },
        );
    };

    return (
        <div>
            <h1 className='text-lg font-semibold'>
                Strategy {selectedStrategy?.name ? selectedStrategy.name : strategyId}
            </h1>
            <Spin spinning={isLoading}>
                <Divider />
                {mode === 'view' && selectedStrategy && (
                    <StrategyView
                        strategy={selectedStrategy}
                        onEdit={() => setMode('edit')}
                        onBack={() => goBack(navigate)}
                    />
                )}
                {mode === 'edit' && selectedStrategy && (
                    <StrategyForm
                        initialValues={selectedStrategy}
                        groups={groups || []}
                        onSubmit={handleFormSubmit}
                        onCancel={() => setMode('view')}
                        loading={isLoadingGroups}
                    />
                )}
                {mode === 'vote' && selectedStrategy && (
                    <StrategyVote strategyId={selectedStrategy._governance_id} onBack={() => navigate(-1)} />
                )}
            </Spin>
        </div>
    );
}
