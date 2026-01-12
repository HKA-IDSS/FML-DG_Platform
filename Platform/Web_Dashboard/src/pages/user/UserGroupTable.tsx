import { Table, Button } from 'antd';
import { Group } from '../../api/models';

interface UserGroupTableProps {
    groups: Group[];
    onRemove: (group: Group) => void;
}

export const UserGroupTable: React.FC<UserGroupTableProps> = ({ groups, onRemove }) => {
    const columns = [
        { title: 'Group Name', dataIndex: 'name', key: 'uname' },
        { title: 'Description', dataIndex: 'description', key: 'udescription' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Group) => (
                <Button danger size='small' onClick={() => onRemove(record)}>
                    Leave
                </Button>
            ),
        },
    ];
    return <Table rowKey='_id' dataSource={groups} columns={columns} />;
};
