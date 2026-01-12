import { Table } from 'antd';
import { Group } from '../../api/models';

interface GroupTableProps {
    groups: Group[];
    onView: (group: Group) => void;
}

export const GroupTable: React.FC<GroupTableProps> = ({ groups, onView }) => {
    const columns = [
        { title: 'Name', dataIndex: 'name', key: 'uname' },
        { title: 'Description', dataIndex: 'description', key: 'udescription' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Group) => <a onClick={() => onView(record)}>View</a>,
        },
    ];
    return <Table rowKey='_id' dataSource={groups} columns={columns} />;
};
