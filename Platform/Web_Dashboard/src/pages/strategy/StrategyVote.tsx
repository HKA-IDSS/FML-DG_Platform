import React, { useMemo, useState } from 'react';
import { Button, Card, Divider, Select, Space, Spin, Typography, Modal, Alert, message } from 'antd';
import { Proposal } from '../../api/models';
import { keycloak } from '../../keycloak';
import { useDatasets } from 'hooks/datasets';
import { useMLModels } from 'hooks/mlmodels';

import {
    useConfigProposalsForStrategy,
    usePriorityVoteMutation,
    useCountConfigurationVotesMutation,
} from '../../hooks/proposals';
import { useStrategyById } from 'hooks/strategies';
import { useGroup } from 'hooks/groups';
import { DynamicUserDataField } from 'components/DataField';
import { EntityLink } from 'components/EntityLink';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface StrategyVoteProps {
    /** Strategy governance id (NOT _id) */
    strategyId: string;
    /** Show the configuration voting dashboard when true */
    visible?: boolean;
    /** Optional: called when user closes the dashboard */
    onBack?: () => void;
}

interface PriorityBuckets {
    priority_1?: unknown[];
    priority_2?: unknown[];
    priority_3?: unknown[];
}

interface TieTally {
    winner: null;
    votes: Record<string, PriorityBuckets>;
    member_count: number;
}

const formatBuckets = (b?: PriorityBuckets) =>
    `p1: ${b?.priority_1?.length ?? 0} | p2: ${b?.priority_2?.length ?? 0} | p3: ${b?.priority_3?.length ?? 0}`;

export const StrategyVote: React.FC<StrategyVoteProps> = ({ strategyId, onBack }) => {
    const [tieInfo, setTieInfo] = useState<TieTally | null>(null);
    const [tieOpen, setTieOpen] = useState(false);

    const isAdmin = keycloak.authenticated && keycloak.hasRealmRole('admin');

    const { data: strategy } = useStrategyById(strategyId);
    const { data: group } = useGroup(strategy?.belonging_group);

    // Load pending configuration proposals for this strategy
    const { data: configProposals = [], isLoading, isFetching } = useConfigProposalsForStrategy(strategyId);

    // Mutations (these invalidate queries on success → auto refresh)
    const priorityVote = usePriorityVoteMutation(strategyId);
    const countConfigs = useCountConfigurationVotesMutation(strategyId);

    // Use Names of models and datasets instead of IDs
    const { data: datasetSchemas } = useDatasets();
    const { data: mlModels } = useMLModels?.() ?? { data: [] };

    const dsNameByGovId = useMemo(
        () => Object.fromEntries((datasetSchemas ?? []).map((d) => [d._governance_id, d.name])),
        [datasetSchemas],
    );
    const modelNameByGovId = useMemo(
        () => Object.fromEntries((mlModels ?? []).map((m) => [m._governance_id, m.name])),
        [mlModels],
    );

    // Compute majority threshold and current turnout (unique voters across proposals)
    const memberCount = group?.members?.length ?? 0;
    const majorityNeeded = Math.floor(memberCount / 2) + 1;

    const uniqueVotersCount = useMemo(() => {
        const s = new Set<string>();
        for (const p of configProposals) {
            const votes: any[] = Array.isArray(p.votes) ? (p.votes as any[]) : [];
            for (const v of votes) {
                if (v?.member) s.add(v.member);
            }
        }
        return s.size;
    }, [configProposals]);

    const handlePriorityChange = (proposalId: string, priority: number) => {
        priorityVote.mutate(
            { proposalId, priority },
            {
                onSuccess: () => message.success(`Priority ${priority} submitted`),
                onError: (err: any) => message.error(`Priority vote failed: ${err?.response?.data?.detail || 'Error'}`),
            },
        );
    };

    const handleCountConfigs = async () => {
        try {
            const res = await countConfigs.mutateAsync();
            const data = res?.data;

            // Handle “tie” as a message
            if (data?.message === 'There was a tie in the voting. Please, change votes to solve it.') {
                setTieInfo(data as TieTally);
                setTieOpen(true);
                if (memberCount > 0 && uniqueVotersCount < majorityNeeded) {
                    message.warning(
                        `No majority yet: ${uniqueVotersCount}/${memberCount} voters. Need at least ${majorityNeeded} to avoid tie.`,
                    );
                } else {
                    message.warning('Tie detected. Ask voters to change priorities and recount.');
                }
                return;
            }

            message.success('Configuration votes counted.');
        } catch (err: any) {
            message.error(`Failed to count configuration votes: ${err?.response?.data?.detail || 'Error'}`);
        }
    };

    return (
        <div className='flex flex-col gap-y-4'>
            <div className='flex items-center justify-between'>
                <Title level={4} style={{ margin: 0 }}>
                    Training Configuration Voting
                </Title>
                <Space>
                    {isAdmin && configProposals.length > 0 && (
                        <Button danger type='primary' onClick={handleCountConfigs} loading={countConfigs.isPending}>
                            End Voting (Count Config Votes)
                        </Button>
                    )}
                    {onBack && <Button onClick={onBack}>Close</Button>}
                </Space>
            </div>

            <Divider className='!mt-2 !mb-2' />

            <Spin spinning={isLoading || isFetching || priorityVote.isPending}>
                {configProposals.map((p: Proposal) => {
                    const content: any = p.proposal_content || {};
                    return (
                        <Card
                            key={p._id}
                            title={p.name}
                            size='small'
                            style={{ marginBottom: 16 }}
                            extra={
                                <Text type='secondary' className='flex items-center gap-1'>
                                    Proposed by: <DynamicUserDataField text={p.proposer ?? 'Unknown'} />
                                </Text>
                            }
                        >
                            <Paragraph>
                                <Text strong>Reasoning:</Text> {p.reasoning || '—'}
                            </Paragraph>
                            <Paragraph>
                                <Text strong>Model:</Text>{' '}
                                <EntityLink kind='ml-model' governanceId={content.ml_model_id}>
                                {modelNameByGovId[content.ml_model_id] ?? content.ml_model_id}{' '}
                                </EntityLink>
                                <Text strong>v</Text>
                                {content.ml_model_version}
                            </Paragraph>
                            <Paragraph>
                                <Text strong>Dataset:</Text>{' '}
                                <EntityLink kind='dataset' governanceId={content.dataset_id}>
                                {dsNameByGovId[content.dataset_id] ?? content.dataset_id}{' '}
                                </EntityLink>
                                <Text strong>v</Text>
                                {content.dataset_version}
                            </Paragraph>
                            <Paragraph>
                                <Text strong>Rounds:</Text> {content.number_of_rounds} &nbsp; | &nbsp;
                                <Text strong>HO Rounds:</Text> {content.number_of_ho_rounds}
                            </Paragraph>

                            <Space>
                                <Text>Set priority:</Text>
                                <Select
                                    placeholder='Select priority'
                                    onChange={(val: any) => handlePriorityChange(p._id, val)}
                                    style={{ width: 200 }}
                                    popupMatchSelectWidth={false}
                                >
                                    <Option value={1}>1 (Highest)</Option>
                                    <Option value={2}>2</Option>
                                    <Option value={3}>3 (Lowest)</Option>
                                </Select>
                            </Space>
                        </Card>
                    );
                })}
                {!isLoading && !isFetching && configProposals.length === 0 && (
                    <Text type='secondary'>No pending configuration proposals for this strategy.</Text>
                )}
            </Spin>

            <Modal
                title={memberCount > 0 && uniqueVotersCount < majorityNeeded ? 'No majority yet' : 'Tie detected'}
                open={tieOpen}
                onCancel={() => setTieOpen(false)}
                footer={
                    <>
                        <Button onClick={() => setTieOpen(false)}>Close</Button>
                        {isAdmin && (
                            <Button type='primary' onClick={handleCountConfigs} loading={countConfigs.isPending}>
                                Recount Now
                            </Button>
                        )}
                    </>
                }
            >
                {memberCount > 0 && uniqueVotersCount < majorityNeeded ? (
                    <Alert
                        type='info'
                        showIcon
                        message={`Not enough turnout. Need at least ${majorityNeeded} of ${memberCount} members to reach a majority.`}
                        style={{ marginBottom: 12 }}
                    />
                ) : (
                    <Alert
                        type='info'
                        showIcon
                        message='Two or more proposals are tied. Ask voters to adjust priorities (1, 2, 3) and recount.'
                        style={{ marginBottom: 12 }}
                    />
                )}

                {tieInfo &&
                    Object.entries(tieInfo.votes).map(([proposalId, buckets]) => (
                        <Card key={proposalId} size='small' style={{ marginBottom: 8 }}>
                            <div className='flex justify-between'>
                                <div>
                                    <strong>Proposal:</strong> {proposalId}
                                </div>
                                <div>
                                    <strong>Votes:</strong> {formatBuckets(buckets as PriorityBuckets)}
                                </div>
                            </div>
                        </Card>
                    ))}
            </Modal>
        </div>
    );
};
