import React from 'react';
import { Descriptions, Button, Table, Typography } from 'antd';
import { MLModel } from '../../api/models';
import { VersionSelect } from 'components/VersionSelect';

interface MLModelViewProps {
    model: MLModel;
    onEdit: () => void;
    onBack: () => void;
    onDelete: () => void;
}

export const MLModelView: React.FC<MLModelViewProps> = ({ model, onEdit, onBack, onDelete }) => {
    const hyperparameterColumns = [
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Type', dataIndex: 'type_of_hyperparameter', key: 'type_of_hyperparameter' },
        {
            title: 'Valid Values',
            dataIndex: 'valid_values',
            key: 'valid_values',
            render: (val: any[]) => val.join(', '),
        },
    ];

    return (
        <>
            <div className='flex flex-col gap-8'>
                <Descriptions
                    title={
                        <div className='flex flex-row justify-between'>
                            <Typography.Title level={5}>ML Model Details</Typography.Title>
                            <VersionSelect entity='Model' id={model._governance_id} />
                        </div>
                    }
                    bordered
                    column={1}
                >
                    <Descriptions.Item label='Name'>{model.name}</Descriptions.Item>
                    <Descriptions.Item label='Description'>{model.description}</Descriptions.Item>
                    <Descriptions.Item label='Algorithm'>{model.model.algorithm}</Descriptions.Item>
                </Descriptions>
                <div className='flex flex-col gap-4'>
                    <Typography.Title level={5}>Hyperparameters</Typography.Title>
                    <Table
                        dataSource={model.model.hyperparameters ?? []}
                        columns={hyperparameterColumns}
                        pagination={false}
                    />
                </div>
            </div>
            <div className='flex flex-row justify-end gap-2 mt-4'>
                <Button disabled={model._deleted || !model._current} onClick={onDelete} danger>
                    Delete
                </Button>
                <Button disabled={model._deleted || !model._current} onClick={onEdit}>
                    Edit
                </Button>
                <Button type='primary' onClick={onBack}>
                    Back
                </Button>
            </div>
        </>
    );
};
