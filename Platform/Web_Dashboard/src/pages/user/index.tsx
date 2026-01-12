import React, { useEffect, useState } from 'react';
import { Divider, Button, Spin, message, Modal } from 'antd';
import api from '../../api/index';
import { Group, User } from '../../api/models';
import { UserGroupTable } from './UserGroupTable';
import { UserGroupForm } from './UserGroupForm';
import { keycloak } from 'keycloak';
import { useAddMember, useGroups } from 'hooks/groups';
import { useUserName } from 'hooks/users';

const UserGroup: React.FC = () => {
    const [mode, setMode] = useState<'table' | 'add'>('table');

    const { data: groups, isLoading: groupsLoading } = useGroups();
    const { data: user } = useUserName(keycloak.subject);
    const mutate = useAddMember();

    const handleJoinGroups = (groups: string[]) => {
        setMode('table');
        mutate.mutate({ groups, userId: keycloak.subject! });
    };

    // Remove user from group (not implemented in API, so just a placeholder)
    const handleLeaveGroup = (group: Group) => {
        Modal.info({
            title: 'Not implemented',
            content: 'Leaving a group is not implemented yet.',
        });
        // If implemented:
        // setLoading(true);
        // api.removeMember(group._governance_id, keycloak.subject)
        //   .then(() => {
        //     message.success('Left group');
        //     fetchData();
        //   })
        //   .catch(() => message.error('Failed to leave group'))
        //   .finally(() => setLoading(false));
    };

    const otherGroups = groups?.filter((g) => !g.members.includes(keycloak.subject!)) || [];
    const myGroups = groups?.filter((g) => g.members.includes(keycloak.subject!)) || [];

    return (
        <div>
            <h1 className='text-lg font-semibold'>My User: {user?.name || '...'}</h1>
            <Divider />
            {mode === 'table' && (
                <>
                    <Button type='primary' onClick={() => setMode('add')} style={{ marginBottom: 16 }}>
                        Join Group
                    </Button>
                    <Spin spinning={groupsLoading}>
                        <UserGroupTable groups={myGroups} onRemove={handleLeaveGroup} />
                    </Spin>
                </>
            )}
            {mode === 'add' && (
                <UserGroupForm
                    availableGroups={otherGroups}
                    onSubmit={handleJoinGroups}
                    onCancel={() => setMode('table')}
                    loading={groupsLoading || mutate.isPending}
                />
            )}
        </div>
    );
};

export default UserGroup;
