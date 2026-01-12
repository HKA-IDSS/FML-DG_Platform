import { Descriptions, Button, Spin } from 'antd';
import { Group } from '../../api/models';
import React, { useState } from 'react';
import { useGroup } from '../../hooks/groups';
import { useGroupStrategies } from '../../hooks/strategies';
import { VersionSelect } from 'components/VersionSelect';
import { Link } from 'react-router-dom';
import { DynamicUserDataField } from 'components/DataField';

interface GroupViewProps {
    group: Group;
    onEdit: () => void;
    onBack: () => void;
    onDelete: () => void;
}

export const GroupView: React.FC<GroupViewProps> = ({ group, onEdit, onBack, onDelete }) => {
    const { data: strategies, isLoading: isLoadingStrategies } = useGroupStrategies(group?._governance_id);

    return (
        <Spin spinning={isLoadingStrategies}>
            <Descriptions
                title={
                    <div className='flex flex-row justify-between'>
                        Group Details
                        <VersionSelect entity='Group' id={group._governance_id} />
                    </div>
                }
                bordered
                column={1}
            >
                <Descriptions.Item label='Name'>{group?.name}</Descriptions.Item>
                <Descriptions.Item label='Description'>{group?.description}</Descriptions.Item>
                <Descriptions.Item label='Members'>
                    <div className='flex flex-wrap gap-2'>
                        {group?.members.map((member) => <DynamicUserDataField key={member} text={member} />) || '—'}
                    </div>
                </Descriptions.Item>
                <Descriptions.Item label='Strategies'>
                    {strategies && strategies.length > 0 ? (
                        <div className='flex flex-wrap gap-2'>
                            {strategies.map((s) => (
                                <Link
                                    key={s._governance_id}
                                    to={`/master-data/strategies/${s._governance_id}?mode=view`}
                                >
                                    {s.name}
                                </Link>
                            ))}
                        </div>
                    ) : (
                        '-'
                    )}
                </Descriptions.Item>
                {group && group._deleted && (
                    <Descriptions.Item label='Status' span={3}>
                        <span className='text-red-600 font-semibold'>Deleted</span>
                    </Descriptions.Item>
                )}
            </Descriptions>
            <div
                style={{
                    marginTop: 16,
                    alignItems: 'right',
                    gap: 4,
                    flexDirection: 'row-reverse',
                    display: 'flex',
                }}
            >
                <Button type='primary' onClick={onBack}>
                    OK
                </Button>
                <Button disabled={!group._current} onClick={onEdit}>
                    Edit
                </Button>
                <Button disabled={!group._current} danger onClick={onDelete}>
                    Delete
                </Button>
            </div>
        </Spin>
    );
};
