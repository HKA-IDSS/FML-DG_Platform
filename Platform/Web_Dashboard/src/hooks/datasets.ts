import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api';
import { AddDataset, Dataset } from '../api/models';
import { message } from 'antd';

export function useDatasets(enabled = true) {
    return useQuery<Dataset[], Error>({
        queryKey: ['datasets'],
        queryFn: async () => {
            const res = await api.getDatasets();
            return res.data;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled,
    });
}

export function useDatasetById(id?: string, version?: number) {
    return useQuery<Dataset, Error>({
        queryKey: ['datasets', id, version],
        queryFn: async () => {
            const res = await api.getDatasetById(id!, version!);
            return res.data;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        enabled: !!id && !!version,
    });
}

// Delete dataset mutation
export function useDeleteDataset() {
    const { refetch } = useDatasets();
    return useMutation({
        mutationFn: (datasetId: string) => api.deleteDataset(datasetId),
        onSuccess: () => {
            message.success('Dataset deleted');
            refetch();
        },
        onError: () => {
            message.error('Failed to delete dataset');
        },
    });
}

// Add dataset mutation
export function useAddDataset() {
    const { refetch } = useDatasets();
    return useMutation({
        mutationFn: (values: AddDataset) => api.insertDataset(values),
        onSuccess: () => {
            message.success('Dataset added');
            refetch();
        },
        onError: () => {
            message.error('Failed to save dataset');
        },
    });
}

// Update dataset mutation
export function useUpdateDataset() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ datasetId, values }: { datasetId: string; values: AddDataset }) =>
            api.updateDataset(datasetId, values),

        onSuccess: () => {
            message.success('Dataset updated');
            queryClient.invalidateQueries({ queryKey: ['datasets'] });
        },
        onError: () => {
            message.error('Failed to update dataset');
        },
    });
}
