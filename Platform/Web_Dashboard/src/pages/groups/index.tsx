import React, { useState } from 'react';
import { Divider, Button, Spin } from 'antd';
import { Group, AddGroup } from '../../api/models';
import { GroupTable } from './GroupsTable';
import { GroupForm } from './GroupsForm';
import { useAddGroup, useGroups } from '../../hooks/groups';
import { useNavigate } from 'react-router-dom';

const Groups: React.FC = () => {
    const { data: groups, isLoading } = useGroups();
    const addGroup = useAddGroup();
    const [mode, setMode] = useState<'table' | 'add'>('table');

    const navigate = useNavigate();

    const handleAdd = () => {
        setMode('add');
    };

    const handleView = (group: Group) => {
        navigate(`/master-data/groups/${group._governance_id}?mode=view&version=${group._version}`);
    };

    const handleFormSubmit = (values: AddGroup) => {
        addGroup.mutate(values);
        setMode('table');
    };

    return (
        <div>
            <h1 className="text-lg font-semibold">Groups</h1>
            <Divider />
            {mode === 'table' && (
                <>
                    <Button type="primary" onClick={handleAdd} style={{ marginBottom: 16 }}>
                        Add Group
                    </Button>
                    <Spin spinning={isLoading}>
                        <GroupTable groups={groups ?? []} onView={handleView} />
                    </Spin>
                </>
            )}
            {mode === 'add' && <GroupForm onSubmit={handleFormSubmit} onCancel={() => setMode('table')} />}
        </div>
    );
};

export default Groups;
