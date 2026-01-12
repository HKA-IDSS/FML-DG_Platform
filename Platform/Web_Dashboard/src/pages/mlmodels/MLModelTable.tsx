import { Table, Button, TableProps } from 'antd';
import { MLModel } from '../../api/models';

interface MLModelTableProps {
    models: MLModel[];
    onView: (model: MLModel) => void;
    onDelete: (model: MLModel) => void;
    rowSelection?: TableProps<MLModel>['rowSelection'];
}

export const MLModelTable: React.FC<MLModelTableProps> = ({ models, onView, onDelete, rowSelection }) => {
    const columns = [
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Algorithm', dataIndex: 'algorithm', key: 'algorithm' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: MLModel) => (
                <>
                    <Button size='small' onClick={() => onView(record)} style={{ marginRight: 8 }}>
                        View
                    </Button>
                    <Button size='small' danger onClick={() => onDelete(record)}>
                        Delete
                    </Button>
                </>
            ),
        },
    ];
    return <Table rowKey='_governance_id' dataSource={models} columns={columns} rowSelection={rowSelection} />;
};
