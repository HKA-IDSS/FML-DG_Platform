import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api';
import { AddProposal, Proposal, Status } from '../api/models';
import { keycloak } from 'keycloak';
import { useMemo } from 'react';
import { message } from 'antd';

// Query keys (centralized)
export const proposalsKeys = {
  all: ['proposals'] as const,
  byStrategy: (strategyId: string) => ['proposals', 'by-strategy', strategyId] as const,
};

export const strategyKeys = {
  byId: (strategyId: string, version?: number) =>
    ['strategy', strategyId, version ?? -1] as const,
};

export const qrKeys = {
  byStrategy: (strategyId: string) => ['qualityRequirements', strategyId] as const,
};

export const configKeys = {
  byStrategy: (strategyId: string) => ['trainingConfigurations', strategyId] as const,
};

// Read: all proposals
export function useProposalsQuery() {
  return useQuery({
    queryKey: proposalsKeys.all,
    queryFn: () => api.getProposals().then(r => r.data as Proposal[]),
  });
}

export function useProposalsByStrategy(strategyGovernanceId: string | undefined) {
  return useQuery({
    queryKey: strategyGovernanceId ? proposalsKeys.byStrategy(strategyGovernanceId) : ['proposals', 'byStrategy', 'nil'],
    enabled: !!strategyGovernanceId,
    queryFn: () => api.getProposalsByStrategy(strategyGovernanceId!).then(r => r.data),
  });
}

export function useConfigProposalsForStrategy(strategyGovernanceId: string) {
  const { data: all = [], isLoading, isFetching, error } = useProposalsByStrategy(strategyGovernanceId);

  const data = useMemo<Proposal[]>(
    () =>
      all.filter(
        (p) =>
          p.strategy_id === strategyGovernanceId &&
          p.content_variant === 'configuration' &&
          p.status === Status.PROPOSED,
      ),
    [all, strategyGovernanceId],
  );

  return { data, isLoading, isFetching, error };
}

// Vote: QR decision (accept/reject)
export function useDecisionVoteMutation(strategyGovernanceId: string) {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: proposalsKeys.all });
    qc.invalidateQueries({ queryKey: proposalsKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: qrKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: strategyKeys.byId(strategyGovernanceId) });
  };

  return useMutation({
    mutationFn: (vars: { proposalId: string; decision: boolean }) =>
      api.addDecisionVote(vars.proposalId, {
        member: keycloak.subject || '',
        decision: vars.decision,
      }),
    onSuccess: invalidate,
  });
}

// Vote: configuration priority (1,2,3)
export function usePriorityVoteMutation(strategyGovernanceId: string) {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: proposalsKeys.all });
    qc.invalidateQueries({ queryKey: proposalsKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: configKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: strategyKeys.byId(strategyGovernanceId) });
  };

  return useMutation({
    mutationFn: (vars: { proposalId: string; priority: number }) =>
      api.addPriorityVote(vars.proposalId, {
        member: keycloak.subject || '',
        priority: vars.priority,
      }),
    onSuccess: invalidate,
  });
}

// Count: QR votes for a single proposal (admin)
export function useCountQRVotesMutation(strategyGovernanceId: string) {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: proposalsKeys.all });
    qc.invalidateQueries({ queryKey: proposalsKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: qrKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: strategyKeys.byId(strategyGovernanceId) });
  };

  return useMutation({
    mutationFn: (proposalId: string) =>
      api.countQualityRequirementVotes(strategyGovernanceId, proposalId),
    onSuccess: invalidate,
  });
}

// Count: configuration votes (admin – processes all config proposals)
export function useCountConfigurationVotesMutation(strategyGovernanceId: string) {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: proposalsKeys.all });
    qc.invalidateQueries({ queryKey: proposalsKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: configKeys.byStrategy(strategyGovernanceId) });
    qc.invalidateQueries({ queryKey: strategyKeys.byId(strategyGovernanceId) });
  };

  return useMutation({
    mutationFn: () => api.countConfigurationVotes(strategyGovernanceId),
    onSuccess: invalidate,
  });
}
