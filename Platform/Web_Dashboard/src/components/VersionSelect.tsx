import { Select } from 'antd';
import { useDatasetById } from 'hooks/datasets';
import { useGroup } from 'hooks/groups';
import { useMLModelById } from 'hooks/mlmodels';
import { useQueryParams } from 'hooks/routing';
import { useStrategyById } from 'hooks/strategies';
import { useEffect } from 'react';

const mockPreviousVersions = (currentVersion: number): number[] => {
    console.log('mockPreviousVersions', currentVersion);
    let previous = [currentVersion];
    for (let v = currentVersion - 1; v >= 1; v--) {
        previous.push(v);
    }

    console.log('mockPreviousVersions', previous);

    return previous;
};

interface Props {
    entity: 'Group' | 'Strategy' | 'Dataset' | 'Model';
    id: string;
}

export const VersionSelect = ({ entity, id }: Props) => {
    const { value, searchParams, setSearchParams } = useQueryParams<number>('version', -1);
    const setValue = (v: number) => {
        searchParams.set('version', v.toString());
        setSearchParams(searchParams);
    };

    const groupId = entity === 'Group' ? id : undefined;
    const datasetId = entity === 'Dataset' ? id : undefined;
    const modelId = entity === 'Model' ? id : undefined;
    const strategyId = entity === 'Strategy' ? id : undefined;

    const { data: group } = useGroup(groupId, -1);
    const { data: dataset } = useDatasetById(datasetId, -1);
    const { data: model } = useMLModelById(modelId, -1);
    const { data: strategy } = useStrategyById(strategyId, -1);

    const entityMap = {
        Group: group,
        Dataset: dataset,
        Model: model,
        Strategy: strategy,
    };

    useEffect(() => {
        console.log('entityMap', entityMap);
        console.log('selected entity', entityMap[entity as keyof typeof entityMap]);
        console.log('entity', entity);

        console.log('datasetId', datasetId);
        console.log('modelId', modelId);
        console.log('strategyId', strategyId);
        console.log('groupId', groupId);
        console.log('dataset', dataset);
    }, [entityMap, entity, datasetId, modelId, strategyId, groupId, dataset]);

    const selectedEntity = entityMap[entity as keyof typeof entityMap];
    const currentVersion = selectedEntity?._version || 1;
    const options = mockPreviousVersions(currentVersion);

    return (
        <div className='flex flex-row gap-2'>
            <p className='text-base'>Version: </p>
            <Select
                value={value === -1 ? currentVersion : value}
                onChange={(v) => setValue(v)}
                placeholder='Select an Version'
                style={{ width: 60 }}
                options={options.map((ver) => ({ label: ver, value: ver }))}
                showSearch
                filterOption={(input, option) => option?.label === Number(input)}
            />
        </div>
    );
};
