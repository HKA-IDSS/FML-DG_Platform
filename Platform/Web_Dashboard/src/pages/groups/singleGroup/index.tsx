import React, { useState } from 'react';
import { Modal, Spin } from 'antd';
import { Group, AddGroup } from '../../../api/models';
import { GroupForm } from '../GroupsForm';
import { GroupView } from '../GroupView';
import { useDeleteGroup, useGroup, useUpdateGroup } from '../../../hooks/groups';
import { useNavigate, useParams } from 'react-router-dom';
import { useQueryParams } from '../../../hooks/routing';
import { goToViewMode } from 'utils/nav';

type ViewMode = 'edit' | 'view';

const SingleGroupView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { value: version } = useQueryParams<number>('version', -1);

    const { data: selectedGroup, isLoading } = useGroup(id, version);
    const deleteGroup = useDeleteGroup();
    const updateGroup = useUpdateGroup();

    const navigate = useNavigate();
    const { value: mode, searchParams, setSearchParams } = useQueryParams<ViewMode>('mode', 'view');
    const setMode = (newMode: ViewMode) => {
        searchParams.set('mode', newMode);
        setSearchParams(searchParams);
    };

    const handleDelete = (group: Group) => {
        Modal.confirm({
            title: `Delete group "${group.name}"?`,
            content: 'This action cannot be undone.',
            okText: 'Delete',
            okType: 'danger',
            onOk: () => deleteGroup.mutate(group._governance_id),
        });
    };

    const handleFormSubmit = (values: AddGroup) => {
        if (selectedGroup) {
            updateGroup.mutate(
                { groupId: selectedGroup._governance_id, values },
                {
                    onSuccess: () => goToViewMode(searchParams, setSearchParams, selectedGroup),
                },
            );
        }
    };

    if (!selectedGroup) {
        return (
            <div className='flex flex-col items-center justify-center h-full'>
                <div>Group not found</div>
            </div>
        );
    }

    return (
        <div>
            <Spin spinning={isLoading}>
                {mode === 'edit' && (
                    <GroupForm
                        initialValues={selectedGroup}
                        onSubmit={handleFormSubmit}
                        onCancel={() => setMode('view')}
                    />
                )}
                {mode === 'view' && (
                    <GroupView
                        group={selectedGroup}
                        onEdit={() => setMode('edit')}
                        onBack={() => navigate('..', { relative: 'path' })}
                        onDelete={() => handleDelete(selectedGroup)}
                    />
                )}
            </Spin>
        </div>
    );
};

export default SingleGroupView;
