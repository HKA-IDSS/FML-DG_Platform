import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api';
import { Configuration } from 'api/models';

// Fetch training configurations for a strategy
export function useTrainingConfigurations(strategyId?: string, strategyVersion?: number) {
    return useQuery<Configuration[], Error>({
        queryKey: ['trainingConfigurations', strategyId, strategyVersion ?? -1],
        queryFn: () => api.getConfigurations(strategyId!, strategyVersion).then((res) => res.data),
        enabled: !!strategyId,
    });
}

export function useTrainingConfigurationsDelete(strategyId?: string) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (configId: string) => api.deleteConfiguration(strategyId!, configId),
        onSuccess: () => {
            // Invalidate and refetch
            queryClient.invalidateQueries({ queryKey: ['trainingConfigurations', strategyId] });
        },
    });
}