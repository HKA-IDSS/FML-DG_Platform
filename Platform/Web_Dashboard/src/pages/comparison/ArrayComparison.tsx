import { Select, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { ObjectComparisonTable } from './ObjectComparisonTable';

const { Text } = Typography;

export const ArraySelector: React.FC<{
    arrayA: any[];
    arrayB: any[];
    labelA: string;
    labelB: string;
    parentKey: string;
}> = ({ arrayA, arrayB, labelA, labelB, parentKey }) => {
    const [selectedA, setSelectedA] = useState<number>();
    const [selectedB, setSelectedB] = useState<number>();

    const objectA = useMemo(() => (selectedA !== undefined ? arrayA[selectedA] : undefined), [arrayA, selectedA]);
    const objectB = useMemo(
        () => (selectedB !== undefined ? arrayB[selectedB] : selectedA !== undefined ? arrayB[selectedA] : undefined),
        [arrayB, selectedA, selectedB],
    );

    return (
        <div>
            <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
                <Select
                    style={{ minWidth: 180 }}
                    placeholder={`Select ${labelA} item`}
                    value={selectedA}
                    onChange={setSelectedA}
                    options={arrayA.map((item, idx) => ({
                        value: idx,
                        label: item?.name || item?.id || `Item ${idx + 1}`,
                    }))}
                />
                <Select
                    style={{ minWidth: 180 }}
                    placeholder={`Select ${labelB} item`}
                    value={selectedB ?? selectedA}
                    onChange={setSelectedB}
                    options={arrayB.map((item, idx) => ({
                        value: idx,
                        label: item?.name || item?.id || `Item ${idx + 1}`,
                    }))}
                />
            </div>
            {objectA !== undefined || objectB !== undefined ? (
                <ObjectComparisonTable objectA={objectA} objectB={objectB} labelA={labelA} labelB={labelB} nested />
            ) : (
                <Text type='secondary'>Select one item from each side to compare.</Text>
            )}
        </div>
    );
};
