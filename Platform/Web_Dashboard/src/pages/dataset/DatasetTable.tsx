import { Table, Button, TableProps } from 'antd';
import { Dataset } from '../../api/models';

interface DatasetTableProps {
    datasets: Dataset[];
    onView: (dataset: Dataset) => void;
    onDelete: (dataset: Dataset) => void;
    rowSelection?: TableProps<Dataset>['rowSelection'];
}

export const DatasetTable: React.FC<DatasetTableProps> = ({ datasets, onView, onDelete, rowSelection }) => {
    const columns = [
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Description', dataIndex: 'description', key: 'description' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Dataset) => (
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
    return <Table rowKey='_governance_id' dataSource={datasets} columns={columns} rowSelection={rowSelection} />;
};
