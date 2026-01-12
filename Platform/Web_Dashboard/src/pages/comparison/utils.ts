import { useQuery } from '@tanstack/react-query';
import { ArtifactType } from './types';
import api from 'api';

export const usePreviousVersion = (id: string, version: number, artifactType?: ArtifactType, enabled = true) => {
    return useQuery({
        queryKey: ['previous-version', id, version, artifactType],
        queryFn: async () => {
            switch (artifactType) {
                case 'strategy':
                    const str = await api.getStrategy(id, version);
                    const config = await api.getConfigurations(id, version);
                    const qualityRequirements = await api.getAllQualityRequirements(id, version);

                    const configurations = config.data.map(async (c) => ({
                        dataset: (await api.getDatasetById(c.dataset_id, c.dataset_version)).data.name,
                        dataset_version: c.dataset_version,
                        model: (await api.getMLModelById(c.ml_model_id, c.ml_model_version)).data.name,
                        model_version: c.ml_model_version,
                        status: c.status,
                        number_of_ho_rounds: c.number_of_ho_rounds,
                        number_of_rounds: c.number_of_rounds,
                    }));

                    const qrMappings = qualityRequirements.data.map((qr) => ({
                        name: qr.name,
                        ...qr.quality_requirement,
                    }));

                    const value = {
                        belonging_group: str.data.belonging_group,
                        comments: str.data.comments,
                        description: str.data.description,
                        name: str.data.name,
                        quality_requirements: qrMappings,
                        configurations: await Promise.all(configurations),
                    };

                    return {
                        artifactType,
                        value,
                    };
                case 'model':
                    const mod = await api.getMLModelById(id, version);
                    return { artifactType, value: mod.data };
                case 'dataset':
                    const dat = await api.getDatasetById(id, version);
                    return { artifactType, value: dat.data };
                default:
                    throw new Error('Invalid artifact type');
            }
        },
        enabled: enabled && !!id && !!version && !!artifactType,
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
};

export const buildComparisonPath = (
    artifactType: ArtifactType,
    idA: string,
    versionA: number,
    idB: string,
    versionB: number,
) => {
    return `/master-data/compare?artifactType=${artifactType}&selectedA=${idA}%23${versionA}&selectedB=${idB}%23${versionB}`;
};
