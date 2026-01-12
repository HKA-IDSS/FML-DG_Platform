import { Proposal, Status } from '../../../../api/models';
import { Table, TableProps, Tag } from 'antd';
import React, { useMemo } from 'react';
import ConfigurationExpandableContent, { ConfigurationProposal } from './ConfigurationExpandableContent';
import { useGroups } from '../../../../hooks/groups';
import QualityReqExpandableContent, { QualityRequirementProposal } from './QualityReqExpandableContent';

interface ProposalTableProps extends TableProps<Proposal> {
    dataSource: Proposal[];
    additionalColumns?: TableProps<Proposal>['columns'];
}

/**
 * Proposal Table component to display proposals with expandable content based on their type.
 * @param additionalColumns
 * @param dataSource
 * @param tableProps
 * @constructor
 */
export default function ProposalTable({ additionalColumns, dataSource, ...tableProps }: ProposalTableProps) {
    const { data: groups, isLoading: groupLoading } = useGroups();

    const groupsById = useMemo(() => {
        return Object.fromEntries((groups ?? []).map(g => [g._governance_id, g.name] as const));
    }, [groups]);

    const columns: TableProps<Proposal>['columns'] = [
        {
            title: 'Proposal Name',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Group',
            dataIndex: 'group',
            key: 'group',
            render: (groupId: string) => {
                return groupsById[groupId] ?? groupId;
            },
        },
        {
            title: 'Reasoning',
            dataIndex: 'reasoning',
            key: 'reasoning',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                if (status === Status.ACCEPTED) {
                    return <Tag color="green">{status}</Tag>;
                }
                if (status === Status.REJECTED) {
                    return <Tag color="red">{status}</Tag>;
                }
                if (status === Status.PROPOSED) {
                    return <Tag color="blue">{status}</Tag>;
                }
                if (status === Status.OBSOLETE) {
                    return <Tag color="grey">{status}</Tag>;
                }
            },
        },
        ...additionalColumns ?? [],
    ];
    return <Table
        dataSource={dataSource}
        columns={columns}
        expandable={{
            expandedRowRender: (record) => {
                if (record.content_variant === 'configuration') {
                    return <ConfigurationExpandableContent record={record as ConfigurationProposal} />;
                }
                if (record.content_variant === 'quality_requirement') {
                    return <QualityReqExpandableContent record={record as QualityRequirementProposal} />;
                }
                return null;
            },
        }}
        {...tableProps}
        loading={tableProps.loading || groupLoading}
    />;
}
