import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api';
import { AddProposal, AddQualityRequirement, ProposalType, Strategy } from '../api/models';
import { keycloak } from 'keycloak';
import { message } from 'antd';
import { BiasForm, CorrectnessForm, StrategySubmit } from 'pages/strategy/StrategyForm';
import { useGroups } from './groups';

export function useGroupStrategies(groupId?: string) {
    return useQuery<Strategy[], Error>({
        queryKey: ['strategies-group', groupId],
        queryFn: async () => {
            const res = await api.getStrategies(groupId!);
            return res.data;
        },
        enabled: !!groupId,
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

export function useStrategyById(strategyId?: string, version?: number) {
    return useQuery<Strategy, Error>({
        queryKey: ['strategy', strategyId, version],
        queryFn: () => api.getStrategy(strategyId!, version).then((res) => res.data),
        enabled: !!strategyId,
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

export function useAllStrategies(enabled = true) {
    const queryClient = useQueryClient();
    const { data: groups = [] } = useGroups();
    return useQuery<Strategy[], Error>({
        queryKey: ['strategies', groups.map((g) => g._governance_id)],
        queryFn: async () => {
            const strategies: Strategy[] = [];

            for (const group of groups) {
                const str = await api.getStrategies(group._governance_id);
                queryClient.setQueryData(['strategies-group', group._governance_id], str.data);
                strategies.push(...str.data);
            }
            return strategies;
        },

        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled,
    });
}

// Delete strategy
export function useDeleteStrategy() {
    const { refetch, data: strategies } = useAllStrategies();
    return useMutation({
        mutationFn: (strategyId: string) =>
            api.deleteStrategies(
                strategyId,
                strategies?.find((s) => s._governance_id === strategyId)?.belonging_group!,
            ),
        onSuccess: () => {
            message.success('Strategy deleted');
            refetch();
        },
        onError: () => {
            message.error('Failed to delete strategy');
        },
    });
}

const insertProposeQualityRequirements = async (
    strategy: Strategy,
    values: {
        bias?: BiasForm[];
        correctness?: CorrectnessForm[];
    },
) => {
    const bias: AddQualityRequirement[] =
        values.bias?.map((b) => ({
            name: b.name,
            quality_requirement: {
                quality_req_type: 'Bias',
                accepted_threshold: b.accepted_threshold,
                vulnerable_feature: b.vulnerable_feature,
            },
        })) ?? [];

    const correctness: AddQualityRequirement[] =
        values.correctness?.map((c) => ({
            name: c.name,
            quality_requirement: {
                quality_req_type: 'Correctness',
                metric: c.metric,
                required_min_value: c.required_min_value,
                required_max_value: c.required_max_value,
            },
        })) ?? [];

    const biasProposals: AddProposal[] = bias.map((qualityRequirement, idx) => ({
        name: "Proposal for bias" + (idx + 1),
        group: strategy.belonging_group,
        strategy_id: strategy._governance_id,
        proposal_content: qualityRequirement,
        content_variant: ProposalType.QUALITY_REQUIREMENT,
        proposer: keycloak.subject,
        reasoning: values.bias![idx].reasoning,
    }));

    const correctnessProposals: AddProposal[] = correctness.map((qualityRequirement, idx) => ({
        name: "Proposal for correctness" + (idx + 1),
        group: strategy.belonging_group,
        strategy_id: strategy._governance_id,
        proposal_content: qualityRequirement,
        content_variant: ProposalType.QUALITY_REQUIREMENT,
        proposer: keycloak.subject,
        reasoning: values.correctness![idx].reasoning,
    }));

    await Promise.all(
        [...biasProposals, ...correctnessProposals].map(async (proposal) => api.insertQualityRequirementProposal(proposal)),
    );
};

// Add strategy
export function useAddStrategy() {
    const { refetch } = useAllStrategies();
    return useMutation({
        mutationFn: async (values: StrategySubmit) => {
            const strategy = {
                name: values.name,
                description: values.description,
                comments: values.comments,
                belonging_group: values.belonging_group,
            };
            const strategyRes = await api.insertStrategy(strategy);
            await insertProposeQualityRequirements(strategyRes.data, values);
            return strategyRes.data;
        },

        onSuccess: () => {
            message.success('Strategy added');
            refetch();
        },
        onError: () => {
            message.error('Failed to save strategy');
        },
    });
}

// Update strategy
export function useUpdateStrategy() {
    const { refetch } = useAllStrategies();
    return useMutation({
        mutationFn: ({ strategyId, values }: { strategyId: string; values: StrategySubmit }) => {
            return api.updateStrategy(strategyId, values);
        },

        onSuccess: () => {
            message.success('Strategy updated');
            refetch();
        },
        onError: () => {
            message.error('Failed to update strategy');
        },
    });
}
