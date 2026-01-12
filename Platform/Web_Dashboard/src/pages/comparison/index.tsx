import React, { useMemo } from 'react';
import { Col, Row, Select, Typography, Spin, Divider } from 'antd';
import { useAllStrategies } from '../../hooks/strategies';
import { useMLModels } from '../../hooks/mlmodels';
import { useDatasets } from '../../hooks/datasets';
import { Artifact, ArtifactType } from './types';
import { ObjectComparisonTable } from './ObjectComparisonTable';
import { usePreviousVersion } from './utils';
import { useSearchParams } from 'react-router-dom';

interface ArtifactOption {
    label: string;
    value: string;
}

const toIdVersion = (artifact?: Artifact) =>
    artifact ? `${artifact.value._governance_id}#${artifact.value._version}` : '';

const fromIdVersion = (idVersion?: string) => {
    if (!idVersion) return { id: '', version: 0 };
    const [id, version] = idVersion.split('#');
    return { id, version: parseInt(version) };
};

const toVersionLabel = (artifact: Artifact) =>
    `${artifact.value.name} (${artifact.value._current ? 'latest' : artifact.value._version})`;

export const ComparisonPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const selectedA = searchParams.get('selectedA') ?? undefined;
    const setSelectedA = (value: string | undefined) => {
        if (value) {
            searchParams.set('selectedA', value);
        } else {
            searchParams.delete('selectedA');
        }
        setSearchParams(searchParams);
    };
    const selectedB = searchParams.get('selectedB') ?? undefined;
    const setSelectedB = (value: string | undefined) => {
        if (value) {
            searchParams.set('selectedB', value);
        } else {
            searchParams.delete('selectedB');
        }
        setSearchParams(searchParams);
    };
    const artifactType = (searchParams.get('artifactType') as ArtifactType) ?? 'strategy';

    const setArtifactType = (value: ArtifactType) => {
        searchParams.set('artifactType', value);
        setSearchParams(searchParams);
    };

    // These endpoints only return the latest version of the artifact
    const { data: strategies, isLoading: isLoadingStrategy } = useAllStrategies(artifactType === 'strategy');
    const { data: mlModels, isLoading: isLoadingModel } = useMLModels(artifactType === 'model');
    const { data: datasets, isLoading: isLoadingDataset } = useDatasets(artifactType === 'dataset');

    const sources: Record<ArtifactType, Artifact[]> = {
        strategy: strategies?.map((item) => ({ artifactType: 'strategy', value: item })) ?? [],
        model: mlModels?.map((item) => ({ artifactType: 'model', value: item })) ?? [],
        dataset: datasets?.map((item) => ({ artifactType: 'dataset', value: item })) ?? [],
    };

    const source = artifactType ? sources[artifactType] : undefined;

    const artifactOptions: ArtifactOption[] = useMemo(() => {
        // Helper to mock previous versions
        const mockPreviousVersions = (item: Artifact): Artifact[] => {
            const currentVersion = item.value?._version || 1;
            const previous: Artifact[] = [];
            for (let v = currentVersion - 1; v >= 1; v--) {
                previous.push({ ...item, value: { ...item.value, _version: v, _current: false } } as Artifact);
            }
            return previous;
        };

        // Build options with previous versions
        const options =
            source?.flatMap((item) => {
                const currentOption: ArtifactOption = {
                    label: toVersionLabel(item),
                    value: toIdVersion(item),
                };
                const previousOptions: ArtifactOption[] = mockPreviousVersions(item).map((prev) => ({
                    label: toVersionLabel(prev),
                    value: toIdVersion(prev),
                }));
                return [currentOption, ...previousOptions];
            }) ?? [];

        return options;
    }, [source]);

    const { id: IdArtifactA, version: VersionArtifactA } = fromIdVersion(selectedA);
    const { id: IdArtifactB, version: VersionArtifactB } = fromIdVersion(selectedB);

    const { data: selectedArtifactA, isLoading: isLoadingPrevA } = usePreviousVersion(
        IdArtifactA,
        VersionArtifactA,
        artifactType,
        !!selectedA,
    );
    const { data: selectedArtifactB, isLoading: isLoadingPrevB } = usePreviousVersion(
        IdArtifactB,
        VersionArtifactB,
        artifactType,
        !!selectedB,
    );

    const loading = isLoadingStrategy || isLoadingModel || isLoadingDataset || isLoadingPrevA || isLoadingPrevB;

    const handleArtifactTypeChange = (value: ArtifactType) => {
        setArtifactType(value);
        setSelectedA(undefined);
        setSelectedB(undefined);
    };

    return (
        <div>
            <h1 className='text-lg font-semibold'>Comparison</h1>
            <Divider />
            <Row gutter={16} align='middle' style={{ marginBottom: 24 }}>
                <Col>
                    <Select<ArtifactType>
                        value={artifactType}
                        onChange={handleArtifactTypeChange}
                        placeholder='Type of artifact'
                        style={{ width: 180 }}
                        options={[
                            { value: 'strategy', label: 'Strategy' },
                            { value: 'model', label: 'ML Model' },
                            { value: 'dataset', label: 'Dataset' },
                        ]}
                    />
                </Col>
                <Col>
                    <Select
                        value={selectedA}
                        onChange={(v) => setSelectedA(v)}
                        placeholder='Name (or id) of artifact'
                        style={{ width: 220 }}
                        options={artifactOptions}
                        showSearch
                        filterOption={(input, option) =>
                            (option?.label as string).toLowerCase().includes(input.toLowerCase())
                        }
                        disabled={!artifactType}
                    />
                </Col>
                <Col>
                    <Select
                        value={selectedB}
                        onChange={(v) => setSelectedB(v)}
                        placeholder='Name (or id) of artifact'
                        style={{ width: 220 }}
                        options={artifactOptions}
                        showSearch
                        filterOption={(input, option) =>
                            (option?.label as string).toLowerCase().includes(input.toLowerCase())
                        }
                        disabled={!artifactType}
                    />
                </Col>
            </Row>
            <Spin spinning={loading}>
                {selectedArtifactA && selectedArtifactB ? (
                    <ObjectComparisonTable
                        objectA={selectedArtifactA?.value}
                        objectB={selectedArtifactB?.value}
                        labelA={selectedArtifactA?.value.name || 'A'}
                        labelB={selectedArtifactB?.value.name || 'B'}
                    />
                ) : (
                    <div style={{ textAlign: 'center', padding: 40 }}>
                        <Typography.Text type='secondary'>Please select two artifacts to compare.</Typography.Text>
                    </div>
                )}
            </Spin>
        </div>
    );
};
