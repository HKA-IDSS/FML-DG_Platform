import React, { useState, useEffect, useMemo } from 'react';
import { Descriptions, Button, Table, Divider, Tag, Spin, Typography } from 'antd';
import { Strategy, QualityRequirement } from '../../api/models';
import { useGroup } from '../../hooks/groups';
import { useTrainingConfigurations } from '../../hooks/trainingConfiguration';
import { useQualityRequirements } from '../../hooks/qualityrequirements';
import { useStrategyById } from 'hooks/strategies';
import { VersionSelect } from 'components/VersionSelect';
import { useNavigate } from 'react-router-dom';
import { useDatasets } from 'hooks/datasets';
import { useMLModels } from 'hooks/mlmodels';
import { EntityLink } from 'components/EntityLink';
import { useQueryParams } from '../../hooks/routing';

interface StrategyViewProps {
    strategy: Strategy;
    onEdit: () => void;
    onBack: () => void;
}

export const StrategyView: React.FC<StrategyViewProps> = ({ strategy, onEdit, onBack }) => {
    const { data: qualityRequirements, isLoading: qrLoading } = useQualityRequirements(
        strategy._governance_id,
        strategy._version,
    );
    const { data: trainingConfigurations, isLoading: tcLoading } = useTrainingConfigurations(
        strategy._governance_id,
        strategy._version,
    );
    const { data: group, isLoading: groupLoading } = useGroup(strategy?.belonging_group);
    const { data: datasetSchemas, isLoading: dsLoading } = useDatasets();
    const { data: mlModels, isLoading: mlLoading } = useMLModels?.() ?? { data: [], isLoading: false };

    // id -> name maps
    const dsNameByGovId = useMemo(
        () => Object.fromEntries((datasetSchemas ?? []).map((d) => [d._governance_id, d.name])),
        [datasetSchemas],
    );
    const modelNameByGovId = useMemo(
        () => Object.fromEntries((mlModels ?? []).map((m) => [m._governance_id, m.name])),
        [mlModels],
    );

    const navigate = useNavigate();

    const loading = qrLoading || tcLoading || groupLoading || dsLoading || mlLoading;

    const deriveQRName = (qr: QualityRequirement) => {
        const q = qr.quality_requirement as any;
        // Prefer explicit name if backend provides
        if (qr.name) return qr.name;

        // Otherwise display the requirement type (in the future for other types as well)
        switch (q?.quality_req_type) {
            case 'Correctness':
                return `Correctness`;
        }
    };

    // Split quality requirements by type
    const correctness =
        qualityRequirements?.filter((qr) => qr.quality_requirement.quality_req_type === 'Correctness') ?? [];
    const bias = qualityRequirements?.filter((qr) => qr.quality_requirement.quality_req_type === 'Bias') ?? [];

    const correctnessColumns = [
        { title: 'Name', key: 'name', render: (_: unknown, record: QualityRequirement) => deriveQRName(record) },
        {
            title: 'Metric',
            dataIndex: ['quality_requirement', 'metric'],
            key: 'metric',
            render: (val: string) => <Tag color='blue'>{val}</Tag>,
        },
        {
            title: 'Min',
            dataIndex: ['quality_requirement', 'required_min_value'],
            key: 'required_min_value',
        },
        {
            title: 'Max',
            dataIndex: ['quality_requirement', 'required_max_value'],
            key: 'required_max_value',
        },
    ];
    /*
        const biasColumns = [
            { title: 'Name', dataIndex: 'name', key: 'name' },
            {
                title: 'Vulnerable Feature',
                dataIndex: ['quality_requirement', 'vulnerable_feature'],
                key: 'vulnerable_feature',
                render: (val: string) => <Tag color='red'>{val}</Tag>,
            },
            {
                title: 'Accepted Threshold',
                dataIndex: ['quality_requirement', 'accepted_threshold'],
                key: 'accepted_threshold',
            },
        ];
    */
    const trainingConfigColumns = [
        {
            title: 'Configuration ID',
            dataIndex: '_id',
            key: '_id'
        },
        {
            title: 'ML Model',
            dataIndex: 'ml_model_id',
            key: 'ml_model_id',
            render: (id: string, r: any) => (
                <EntityLink kind='ml-model' governanceId={r.ml_model_id}>
                    {modelNameByGovId[id] ?? id}
                </EntityLink>
            ),
        },
        { title: 'ML Model Version', dataIndex: 'ml_model_version', key: 'ml_model_version' },
        {
            title: 'Dataset',
            dataIndex: 'dataset_id',
            key: 'dataset_id',
            render: (id: string, r: any) => (
                <EntityLink kind='dataset' governanceId={r.dataset_id}>
                    {dsNameByGovId[id] ?? id}
                </EntityLink>
            ),
        },
        { title: 'Dataset Version', dataIndex: 'dataset_version', key: 'dataset_version' },
        { title: 'Rounds', dataIndex: 'number_of_rounds', key: 'number_of_rounds' },
        { title: 'HO Rounds', dataIndex: 'number_of_ho_rounds', key: 'number_of_ho_rounds' },
    ];

    return (
        <Spin spinning={loading}>
            <Descriptions
                title={
                    <div className='flex flex-row justify-between'>
                        <Typography.Title level={5}>Strategy Details</Typography.Title>

                        <div className='flex flex-row gap-5'>
                            <Button
                                type='primary'
                                onClick={(e) => navigate(`/master-data/strategies/${strategy._governance_id}/proposal`)}
                            >
                                View Proposals
                            </Button>
                            <VersionSelect entity='Strategy' id={strategy._governance_id} />
                        </div>
                    </div>
                }
                bordered
                column={1}
            >
                <Descriptions.Item label='Name' labelStyle={{ width: 120 }}>
                    {strategy.name}
                </Descriptions.Item>
                <Descriptions.Item label='Description' labelStyle={{ width: 120 }}>
                    {strategy.description}
                </Descriptions.Item>
                <Descriptions.Item label='Group' labelStyle={{ width: 120 }}>
                    {group ? (
                        <EntityLink kind='group' governanceId={group._governance_id}>
                            {group?.name}
                        </EntityLink>
                    ) : (
                        '-'
                    )}
                </Descriptions.Item>
                <Descriptions.Item label='Comments' labelStyle={{ width: 120 }}>
                    {(strategy.comments || []).join(', ')}
                </Descriptions.Item>
            </Descriptions>

            <Divider orientation='left'>Quality Requirements - Correctness</Divider>
            <Table
                rowKey='name'
                dataSource={correctness}
                columns={correctnessColumns}
                pagination={false}
                size='small'
            />

            {/*<Divider orientation='left'>Quality Requirements - Bias</Divider>
            <Table rowKey='name' dataSource={bias} columns={biasColumns} pagination={false} size='small' />*/}

            <Divider orientation='left'>Training Configurations</Divider>
            <Table
                rowKey='_id'
                dataSource={trainingConfigurations}
                columns={trainingConfigColumns}
                pagination={false}
                size='small'
            />

            <div style={{ marginTop: 16 }}>
                <Button onClick={onEdit} type='primary' style={{ marginRight: 8 }}>
                    Edit
                </Button>
                <Button onClick={onBack}>Back</Button>
            </div>
        </Spin>
    );
};
