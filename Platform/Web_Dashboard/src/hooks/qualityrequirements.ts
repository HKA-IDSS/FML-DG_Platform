import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../api';
import { QualityRequirement } from '../api/models';
import { message } from 'antd';

// Fetch quality requirements for a strategy
export function useQualityRequirements(strategyId?: string, version?: number) {
    return useQuery<QualityRequirement[], Error>({
        queryKey: ['qualityRequirements', strategyId, version],
        queryFn: () => api.getAllQualityRequirements(strategyId!, version).then((res) => res.data),
        enabled: !!strategyId,
    });
}

export function useDeleteQualityRequirement(strategyId?: string) {
    const { refetch } = useQualityRequirements(strategyId);
    return useMutation({
        mutationFn: (modelId: string) => api.deleteMLModel(modelId),
        onSuccess: () => {
            message.success('Model deleted');
            refetch();
        },
        onError: () => {
            message.error('Failed to delete model');
        },
    });
}