import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../api';
import { AddMLModel, AlgorithmType, MLModel, MLModelUnion } from '../api/models';
import { message } from 'antd';

export function useMLModels(enabled = true) {
    return useQuery<MLModel[], Error>({
        queryKey: ['mlmodels'],
        queryFn: async () => {
            const res = await api.getMLModels();
            return res.data;
        },

        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled,
    });
}

export function useMLModelById(id?: string, version?: number) {
    return useQuery<MLModel, Error>({
        queryKey: ['mlmodels', id, version],
        queryFn: async () => {
            const res = await api.getMLModelById(id!, version);
            return res.data;
        },

        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled: !!id,
    });
}

export function useDefaultMLModel(name?: AlgorithmType) {
    return useQuery<MLModelUnion | null, Error>({
        queryKey: ['mlmodels-default', name],
        queryFn: async () => {
            if (name === 'custom') return null;
            const res = await api.getDefaultModel(name!);
            return res.data;
        },

        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled: !!name,
    });
}

// Add ML Model
export function useAddMLModel() {
    const { refetch } = useMLModels();
    return useMutation({
        mutationFn: (values: AddMLModel) => api.insertMLModels(values),
        onSuccess: () => {
            message.success('Model added');
            refetch();
        },
        onError: () => {
            message.error('Failed to add model');
        },
    });
}

// Update ML Model
export function useUpdateMLModel() {
    const { refetch } = useMLModels();
    return useMutation({
        mutationFn: ({ modelId, values }: { modelId: string; values: AddMLModel }) =>
            api.updateMLModels(modelId, values),

        onSuccess: () => {
            message.success('Model updated');
            refetch();
        },
        onError: () => {
            message.error('Failed to update model');
        },
    });
}

// Delete ML Model
export function useDeleteMLModel() {
    const { refetch } = useMLModels();
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
