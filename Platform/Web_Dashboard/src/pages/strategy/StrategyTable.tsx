import { Table, Button, TableProps } from 'antd';
import { Strategy } from '../../api/models';

interface StrategyTableProps {
    strategies: Strategy[];
    onView: (strategy: Strategy) => void;
    onDelete: (strategy: Strategy) => void;
    rowSelection?: TableProps<Strategy>['rowSelection'];
}

export const StrategyTable: React.FC<StrategyTableProps> = ({ strategies, onView, onDelete, rowSelection }) => {
    const columns = [
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Status', dataIndex: 'status', key: 'status' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Strategy) => (
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
    return <Table rowKey='_governance_id' dataSource={strategies} columns={columns} rowSelection={rowSelection} />;
};
