import React, { useState } from 'react';
import { Button, Divider, Modal, Spin } from 'antd';
import { Strategy } from '../../api/models';
import { StrategyTable } from './StrategyTable';
import { StrategyForm, StrategySubmit } from './StrategyForm';

import { useAddStrategy, useAllStrategies, useDeleteStrategy } from 'hooks/strategies';
import { useGroups } from '../../hooks/groups';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { buildComparisonPath } from 'pages/comparison/utils';

type ViewMode = 'table' | 'add';
const ViewModeParameter = 'mode';

const StrategiesFunctional: React.FC = () => {
    // Compare logic
    const navigate = useNavigate();

    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    const { data: groups, isLoading: isLoadingGroups } = useGroups();
    const { data: strategies, isLoading: isLoadingStrategies } = useAllStrategies();
    const addStrategy = useAddStrategy();
    const deleteStrategy = useDeleteStrategy();

    const [searchParams, setSearchParams] = useSearchParams();
    const mode = (searchParams.get(ViewModeParameter) as ViewMode) || 'table';

    const setMode = (newMode: ViewMode) => {
        searchParams.set(ViewModeParameter, newMode);
        setSearchParams(searchParams);
    };

    const handleAdd = () => setMode('add');
    const handleView = (s: Strategy) => navigate(s._governance_id + '?mode=view&version=' + s._version);

    const handleDelete = (strategy: Strategy) => {
        Modal.confirm({
            title: `Delete strategy "${strategy.name}"?`,
            content: 'This action cannot be undone.',
            okText: 'Delete',
            okType: 'danger',
            onOk: () => deleteStrategy.mutate(strategy._governance_id),
        });
    };

    const handleFormSubmit = (values: StrategySubmit) => {
        if (mode !== 'add') {
            console.error('Form submit in non-add mode');
            return;
        }
        addStrategy.mutate(values);
        setMode('table');
    };

    // Compare selection logic
    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const handleCompare = () => {
        if (selectedRowKeys.length !== 2) return;
        const [a, b] = selectedRowKeys;
        const aStr = strategies?.find((s) => s._governance_id === a);
        const bStr = strategies?.find((s) => s._governance_id === b);
        if (!aStr || !bStr) return;
        navigate(
            buildComparisonPath('strategy', aStr._governance_id, aStr._version, bStr._governance_id, bStr._version),
        );
    };

    return (
        <div>
            <h1 className="text-lg font-semibold">Strategies</h1>
            <Divider />
            {mode === 'table' && (
                <>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                        <Button type="primary" onClick={handleAdd}>
                            Add Strategy
                        </Button>
                        <Button type="primary" disabled={selectedRowKeys.length !== 2} onClick={handleCompare}>
                            Compare Strategies
                        </Button>
                    </div>
                    <Spin spinning={isLoadingStrategies}>
                        <StrategyTable
                            strategies={strategies || []}
                            onView={handleView}
                            onDelete={handleDelete}
                            rowSelection={{
                                selectedRowKeys,
                                onChange: onSelectChange,
                                type: 'checkbox',
                            }}
                        />
                    </Spin>
                </>
            )}
            {mode === 'add' && (
                <StrategyForm
                    groups={groups || []}
                    onSubmit={handleFormSubmit}
                    onCancel={() => setMode('table')}
                    loading={isLoadingGroups}
                />
            )}
        </div>
    );
};

export default StrategiesFunctional;
