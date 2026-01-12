import { useQuery } from '@tanstack/react-query';
import api from '../api';
import { Metric } from '../api/models';
import { AxiosError } from 'axios';

export function useTestEvaluation(metric: Metric['type']) {
    return useQuery<string, Error>({
        queryKey: ['evaluation-test', metric],
        queryFn: async () => {
            const res = await api.getEvaluationTest(metric);
            return res.data;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

export function useMultipleTestEvaluations(configuration_id: string, metrics: Metric['type'][]) {
    return useQuery<Record<string, string>, Error>({
        queryKey: ['evaluation-multiple-test', metrics],
        queryFn: async () => {
            const results: Record<string, string> = {};
            for (const metric of metrics) {
                const res = await api.getEvaluation(configuration_id, metric);
                results[metric] = res.data;
            }
            return results;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

export function useTestShapleyValue(metric: Metric['type']) {
    return useQuery<string, Error>({
        queryKey: ['evaluation-test', metric],
        queryFn: async () => {
            const res = await api.getShapleyValueTest(metric);
            return res.data;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

export function useMultipleTestShapleyValues(configuration_id: string, metrics: Metric['type'][]) {
    return useQuery<Record<string, string>, Error>({
        queryKey: ['shapley-multiple-test', metrics],
        queryFn: async () => {
            const results: Record<string, string> = {};
            for (const metric of metrics) {
                const res = await api.getShapleyValues(configuration_id, metric);
                results[metric] = res.data;
            }
            return results;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

const is404 = (error: unknown) =>
    (error as AxiosError)?.response?.status === 404;

export const useResultsData = (
    configuration_id: string,
    evaluationMetrics: Metric['type'][],
    shapleyMetrics: Metric['type'][],
) => {
    const evaluationQuery = useMultipleTestEvaluations(
        configuration_id,
        evaluationMetrics
    );

    const shapleyQuery = useMultipleTestShapleyValues(
        configuration_id,
        shapleyMetrics
    );

    const loading =
        evaluationQuery.isLoading || shapleyQuery.isLoading;

    const evaluation404 =
        evaluationQuery.isError && is404(evaluationQuery.error);

    const shapley404 =
        shapleyQuery.isError && is404(shapleyQuery.error);

    const fatalError =
        (evaluationQuery.isError && !evaluation404) ||
        (shapleyQuery.isError && !shapley404);

    return {
        loading,

        fatalError,

        evaluation: {
            exists: !evaluation404,
            data: evaluationQuery.data,
        },

        shapley: {
            exists: !shapley404,
            data: shapleyQuery.data,
        },
    };
};


