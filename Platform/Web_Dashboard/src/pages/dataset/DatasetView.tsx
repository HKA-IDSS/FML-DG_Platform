import { Descriptions, Button, Table } from 'antd';
import { Dataset } from '../../api/models';
import { VersionSelect } from 'components/VersionSelect';

interface DatasetViewProps {
    dataset: Dataset;
    onEdit: () => void;
    onBack: () => void;
}

export const DatasetView: React.FC<DatasetViewProps> = ({ dataset, onEdit, onBack }) => {
    const featureColumns = [
        { title: 'Order', dataIndex: 'order_in_dataset', key: 'order_in_dataset' },
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Type', dataIndex: 'type', key: 'type' },
        { title: 'Description', dataIndex: 'description', key: 'description' },
        { title: 'Encoding', dataIndex: 'preprocessing', key: 'preprocessing' },
        { title: 'Group', dataIndex: 'group', key: 'group', render: (val: boolean) => (val ? 'Yes' : 'No') },
        {
            title: 'Valid Values',
            dataIndex: 'valid_values',
            key: 'valid_values',
            render: (val: any[]) => val.map((v) => v.toString()).join(', '),
        },
        {
            title: 'Sub Features',
            dataIndex: 'sub_features',
            key: 'sub_features',
            render: (val: string[]) => val?.join(', '),
        },
    ];

    return (
        <>
            <Descriptions
                title={
                    <div className='flex flex-row justify-between'>
                        Dataset Details
                        <VersionSelect entity='Dataset' id={dataset._governance_id} />
                    </div>
                }
                bordered
                column={1}
            >
                <Descriptions.Item label='Name'>{dataset.name}</Descriptions.Item>
                <Descriptions.Item label='Description'>{dataset.description}</Descriptions.Item>
                <Descriptions.Item label='Structured'>{dataset.structured ? 'Yes' : 'No'}</Descriptions.Item>
            </Descriptions>
            <div style={{ margin: '16px 0' }}>
                <h3 className='font-semibold'>Features</h3>
                <Table
                    rowKey='order_in_dataset'
                    dataSource={dataset.features}
                    columns={featureColumns}
                    pagination={false}
                />
            </div>
            <div>
                <Button onClick={onEdit} type='primary' style={{ marginRight: 8 }}>
                    Edit
                </Button>
                <Button onClick={onBack}>Back</Button>
            </div>
        </>
    );
};
