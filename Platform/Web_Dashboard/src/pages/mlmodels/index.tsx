import React, { useState, useEffect } from 'react';
import { Divider, Button, Spin, Modal } from 'antd';
import { MLModel, AddMLModel } from '../../api/models';
import { MLModelTable } from './MLModelTable';
import { MLModelForm } from './MLModelForm';
import { MLModelView } from './MLModelView';
import { useAddMLModel, useDeleteMLModel, useMLModels, useUpdateMLModel } from '../../hooks/mlmodels';
import { useLocation, useNavigate } from 'react-router-dom';
import { buildComparisonPath } from 'pages/comparison/utils';

type NavState = { preselectId?: string; openView?: boolean; entityKind?: 'ml-model' | string };

const MLModelsFunctional: React.FC = () => {
    const { data: models, isLoading } = useMLModels();
    const addMLModel = useAddMLModel();
    const updateMLModel = useUpdateMLModel();
    const deleteMLModel = useDeleteMLModel();
    const [mode, setMode] = useState<'table' | 'add' | 'edit'>('table');
    const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
    // Compare logic
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    const navigate = useNavigate();
    const handleAdd = () => {
        setSelectedModel(null);
        setMode('add');
    };

    const handleView = (model: MLModel) => {
        navigate(model._governance_id + '?mode=view&version=' + model._version);
    };

    const handleDelete = (model: MLModel) => {
        Modal.confirm({
            title: `Delete model "${model.name}"?`,
            content: 'This action cannot be undone.',
            okText: 'Delete',
            okType: 'danger',
            onOk: () => deleteMLModel.mutate(model._governance_id),
        });
    };

    const handleFormSubmit = (values: AddMLModel) => {
        if (mode === 'edit' && selectedModel) {
            updateMLModel.mutate({ modelId: selectedModel._governance_id, values });
        } else {
            addMLModel.mutate(values);
        }
        setMode('table');
    };
    // Compare selection logic
    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const handleCompare = () => {
        if (selectedRowKeys.length !== 2) return;
        const [a, b] = selectedRowKeys;
        const aMod = models?.find((s) => s._governance_id === a);
        const bMod = models?.find((s) => s._governance_id === b);
        if (!aMod || !bMod) return;
        navigate(buildComparisonPath('model', aMod._governance_id, aMod._version, bMod._governance_id, bMod._version));
    };

    return (
        <div>
            <h1 className="text-lg font-semibold">ML Models</h1>
            <Divider />
            {mode === 'table' && (
                <>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                        <Button type="primary" onClick={handleAdd}>
                            Add ML Model
                        </Button>
                        <Button type="primary" disabled={selectedRowKeys.length !== 2} onClick={handleCompare}>
                            Compare ML Models
                        </Button>
                    </div>
                    <Spin spinning={isLoading}>
                        <MLModelTable
                            models={models || []}
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
                <MLModelForm onSubmit={handleFormSubmit} onCancel={() => setMode('table')} loading={isLoading} />
            )}
        </div>
    );
};

export default MLModelsFunctional;
