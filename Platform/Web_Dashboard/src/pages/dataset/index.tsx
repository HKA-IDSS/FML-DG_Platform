import React, { useState } from 'react';
import { Divider, Button, Spin, Modal } from 'antd';
import { Dataset, AddDataset } from '../../api/models';
import { DatasetTable } from './DatasetTable';
import { DatasetForm } from './DatasetForm';
import { useAddDataset, useDatasets, useDeleteDataset } from '../../hooks/datasets';
import { useGroups } from '../../hooks/groups';
import { useNavigate } from 'react-router-dom';
import { buildComparisonPath } from 'pages/comparison/utils';

const DatasetsFunctional: React.FC = () => {
    const { data: datasets, refetch: refetchDatasets, isLoading: datasetLoading } = useDatasets();
    const { data: groups, refetch: refetchGroups, isLoading: groupsLoading } = useGroups();
    const deleteDataset = useDeleteDataset();
    const addDataset = useAddDataset();
    const [mode, setMode] = useState<'table' | 'add'>('table');

    // Compare logic
    const [compareSelection, setCompareSelection] = useState<Dataset[]>([]);

    const loading = datasetLoading || groupsLoading;
    const navigate = useNavigate();

    const handleAdd = () => {
        setMode('add');
    };

    const handleView = (dataset: Dataset) => {
        navigate(`/master-data/datasets/${dataset._governance_id}?mode=view&version=${dataset._version}`);
    };

    const handleDelete = (dataset: Dataset) => {
        Modal.confirm({
            title: `Delete dataset "${dataset.name}"?`,
            content: 'This action cannot be undone.',
            okText: 'Delete',
            okType: 'danger',
            onOk: () => deleteDataset.mutate(dataset._governance_id),
        });
    };

    const handleFormSubmit = (values: AddDataset) => {
        addDataset.mutate(values);
        setMode('table');
    };

    // Compare selection logic
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
        if (newSelectedRowKeys.length === 2 && datasets) {
            const selected = datasets.filter((ds) => newSelectedRowKeys.includes(ds._id));
            setCompareSelection(selected);
        } else {
            setCompareSelection([]);
        }
    };

    const handleCompare = () => {
        console.log('Comparing datasets', selectedRowKeys, datasets);
        if (selectedRowKeys.length !== 2) return;
        const [a, b] = selectedRowKeys;
        const aDat = datasets?.find((s) => s._governance_id === a);
        const bDat = datasets?.find((s) => s._governance_id === b);
        console.log('Found datasets', aDat, bDat);
        if (!aDat || !bDat) return;
        navigate(
            buildComparisonPath('dataset', aDat._governance_id, aDat._version, bDat._governance_id, bDat._version),
        );
    };

    return (
        <div>
            <h1 className="text-lg font-semibold">Datasets</h1>
            <Divider />
            {mode === 'table' && (
                <>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                        <Button type="primary" onClick={handleAdd}>
                            Add Dataset
                        </Button>
                        <Button type="primary" disabled={selectedRowKeys.length !== 2} onClick={handleCompare}>
                            Compare Datasets
                        </Button>
                    </div>
                    <Spin spinning={loading}>
                        <DatasetTable
                            datasets={datasets ?? []}
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
                <DatasetForm
                    groups={groups ?? []}
                    onSubmit={handleFormSubmit}
                    onCancel={() => setMode('table')}
                    loading={loading}
                />
            )}
        </div>
    );
};

export default DatasetsFunctional;
