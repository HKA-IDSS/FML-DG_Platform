import { useState } from 'react';
import { Divider, TableProps, Button, Drawer, message, Space } from 'antd';
import { Configuration, Proposal, QualityRequirement, Strategy } from '../../../api/models';
import {
    useDecisionVoteMutation,
    useCountQRVotesMutation,
    useProposalsByStrategy,
} from '../../../hooks/proposals';
import { useDatasets } from '../../../hooks/datasets';
import { StrategyVote } from '../StrategyVote';
import { keycloak } from 'keycloak';
import { useMLModels } from 'hooks/mlmodels';
import ProposalTable from './ProposalTable';

interface ProposalDataTableProps extends TableProps {
    strategy: Strategy;
}

export const ProposalDataTable = ({ strategy }: ProposalDataTableProps) => {
    const { data: proposals, isLoading: proposalLoading } = useProposalsByStrategy(strategy._governance_id);
    const { isLoading: datasetSchemaLoading } = useDatasets();
    const { isLoading: mlModelSchemaLoading } = useMLModels();
    const voteMutation = useDecisionVoteMutation(strategy._governance_id);
    const { mutate: countQRVotes } = useCountQRVotesMutation(strategy._governance_id);

    const isAdmin = keycloak.authenticated && keycloak.hasRealmRole('admin');

    const [voteOpen, setVoteOpen] = useState(false);

    const qualityRequirementProposals = proposals
        ?.filter((p) => p.strategy_id === strategy._governance_id && p.content_variant === 'quality_requirement')
        .map((p) => ({ ...p, proposal_content: p.proposal_content as QualityRequirement }));

    const trainingConfigurationsProposals = proposals
        ?.filter((p) => p.strategy_id === strategy._governance_id && p.content_variant === 'configuration')
        .map((p) => ({ ...p, proposal_content: p.proposal_content as Configuration }));

    const qrProposalVoteCounts =
        qualityRequirementProposals?.map((p) => (Array.isArray(p.votes) ? p.votes.length : 0)) ?? [];

    const handleCountQR = (proposalId: string) => {
        countQRVotes(proposalId, {
            onSuccess: () => {
                message.success('Counted QR votes for this proposal.');
            },
            onError: (err: any) => {
                message.error(err?.response?.data?.detail || 'Failed to count QR votes.');
            },
        });
    };

    function handleVote(proposalId: string, decision: boolean) {
        return voteMutation.mutate(
            { proposalId, decision },
            {
                onSuccess: () => message.success(decision ? 'Accepted' : 'Rejected'),
                onError: (e: any) => message.error(e?.response?.data?.detail || 'Vote failed'),
            },
        );
    }

    const QRVotingColumn = (props: {
        proposalId: string;
        index: number;
        proposal: Proposal
    }) => {
        const { proposalId, index, proposal } = props;
        if (proposal.status !== 'PROPOSED') {
            return <p>Voting concluded</p>;
        }
        return (
            <Space size="small">
                <Button type="primary" onClick={() => handleVote(proposalId, true)}>
                    Accept
                </Button>
                <Button danger onClick={() => handleVote(proposalId, false)}>
                    Reject
                </Button>
                {isAdmin && <Button
                    onClick={() => handleCountQR(proposalId)}
                    disabled={!qrProposalVoteCounts[index]} // TODO: i think?
                >
                    Count
                </Button>}
            </Space>
        );
    };

    return (
        <div className="proposal-data-table w-full">
            <Divider orientation="left">Training Configuration Proposal</Divider>
            <ProposalTable
                dataSource={trainingConfigurationsProposals?.map((p) => ({ ...p, key: p._id })) ?? []}
                additionalColumns={[
                    {
                        title: 'Voting',
                        dataIndex: 'voting',
                        key: 'voting',
                        render: (id: string) => (
                            <Button type="primary" onClick={() => setVoteOpen(true)}>
                                Open Voting
                            </Button>
                        ),
                    },
                ]}
                // Copied from Table<Configuration>
                loading={datasetSchemaLoading || proposalLoading || mlModelSchemaLoading}
                pagination={{ position: ['bottomRight'] }}
                style={{ width: '100%', marginBottom: '20px' }}
            />
            <Divider orientation="left">Quality Requirements</Divider>
            <ProposalTable
                dataSource={qualityRequirementProposals?.map(p => ({ ...p, key: p._id })) ?? []}

                loading={datasetSchemaLoading || proposalLoading || mlModelSchemaLoading}
                pagination={{ position: ['bottomRight'] }}
                style={{ width: '100%', marginBottom: '20px' }}
                additionalColumns={[
                    {
                        title: 'Voting',
                        dataIndex: '_id',
                        key: '_id',
                        render: (proposalId: string, proposal, index) =>
                            <QRVotingColumn proposalId={proposalId} proposal={proposal} index={index} />,
                    },
                ]}
            />

            {/* Voting Drawer */}
            <Drawer
                title="Vote on Training Configuration Proposals"
                open={voteOpen}
                width={720}
                onClose={() => setVoteOpen(false)}
                destroyOnClose
            >
                <StrategyVote
                    strategyId={strategy._governance_id}
                    visible={voteOpen}
                    onBack={() => setVoteOpen(false)}
                />
            </Drawer>
        </div>
    );


};
