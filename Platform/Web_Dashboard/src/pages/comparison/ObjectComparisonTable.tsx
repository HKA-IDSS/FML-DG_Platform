import React, { useMemo } from 'react';
import { Table } from 'antd';
import { ComparisonRow } from './types';
import { DataField } from '../../components/DataField';
import { ArraySelector } from './ArrayComparison';

function normalizeKey(key: string): string {
    let extracted = key.replace(/^_+/, '');
    extracted = extracted.replace(/_/g, ' ');
    extracted = extracted.replace('id', '');
    extracted = extracted.replace('governance', '');
    return extracted;
}

function isObject(val: any): val is object {
    return val !== null && typeof val === 'object' && !Array.isArray(val);
}

function isArray(val?: any): val is any[] {
    return Array.isArray(val);
}

function isPrimitiveArray(arr?: any): arr is (string | number)[] {
    const ret =
        Array.isArray(arr) &&
        arr.every((item) => typeof item === 'string' || typeof item === 'number' || typeof item === 'boolean');
    return ret;
}

function getAllKeys(objA?: any, objB?: any): string[] {
    const keysA = objA ? Object.keys(objA) : [];
    const keysB = objB ? Object.keys(objB) : [];
    return Array.from(new Set([...keysA, ...keysB]));
}

function formatValue(val?: any): string {
    if (val === undefined || val === null) return '';
    if (typeof val === 'object') return '';
    return String(val);
}

function buildComparisonRows(a?: any, b?: any, parentKey = ''): ComparisonRow[] {
    if (isArray(a) || isArray(b)) {
        // If a or b is a primitive array, display as string
        if (isPrimitiveArray(a) || isPrimitiveArray(b)) {
            return [
                {
                    key: parentKey,
                    attribute: normalizeKey(parentKey),
                    a: isPrimitiveArray(a) ? `[${a.join(', ')}]` : '',
                    b: isPrimitiveArray(b) ? `[${b.join(', ')}]` : '',
                    type: 'primitive',
                    valueA: a,
                    valueB: b,
                },
            ];
        }
        // Otherwise, show as [n items]
        return [
            {
                key: parentKey,
                attribute: normalizeKey(parentKey),
                a: isArray(a) ? `[${a.length} items]` : '',
                b: isArray(b) ? `[${b.length} items]` : '',
                type: 'array',
                valueA: a,
                valueB: b,
            },
        ];
    }

    if (isObject(a) || isObject(b)) {
        const keys = getAllKeys(a, b);
        const show = (val: any, type: ComparisonRow['type']) => {
            switch (type) {
                case 'primitive':
                    return isPrimitiveArray(val) ? `[${val.join(', ')}]` : formatValue(val);
                case 'array':
                    return isArray(val) ? `[${val.length} items]` : '';
                default:
                    return '';
            }
        };

        return keys
            .map((key) => {
                const valA = a?.[key];
                const valB = b?.[key];
                const type: ComparisonRow['type'] =
                    isArray(valA) || isArray(valB)
                        ? isPrimitiveArray(valA ?? []) && isPrimitiveArray(valB ?? [])
                            ? 'primitive'
                            : 'array'
                        : isObject(valA) || isObject(valB)
                        ? 'object'
                        : 'primitive';

                if (valA === undefined && valB === undefined) return null;

                return {
                    key: parentKey ? `${parentKey}.${key}` : key,
                    attribute: normalizeKey(key),
                    a: show(valA, type),
                    b: show(valB, type),
                    type,
                    valueA: valA,
                    valueB: valB,

                    childrenData:
                        type === 'object'
                            ? buildComparisonRows(valA, valB, parentKey ? `${parentKey}.${key}` : key)
                            : undefined,
                };
            })
            .filter(Boolean) as ComparisonRow[];
    }

    if (a === undefined && b === undefined) return [];
    return [
        {
            key: parentKey,
            attribute: normalizeKey(parentKey),
            a: formatValue(a),
            b: formatValue(b),
            type: 'primitive',
            valueA: a,
            valueB: b,
        },
    ];
}

const filterGovernanceAndId = (obj?: any) => {
    if (!obj || typeof obj !== 'object') return obj;
    const { _governance_id, _id, ...rest } = obj;
    return rest;
};

export const ObjectComparisonTable: React.FC<{
    objectA?: any;
    objectB?: any;
    labelA?: string;
    labelB?: string;
    nested?: boolean;
}> = ({ objectA, objectB, labelA = 'A', labelB = 'B', nested = false }) => {
    const dataSource = useMemo(
        () => buildComparisonRows(filterGovernanceAndId(objectA), filterGovernanceAndId(objectB)),
        [objectA, objectB],
    );

    const columns = [
        {
            title: 'Attribute',
            dataIndex: 'attribute',
            key: 'attribute',
            width: '40%',
            render: (text: string) => <span className='capitalize'>{text}</span>,
        },
        {
            title: labelA,
            dataIndex: 'a',
            key: 'a',
            width: '30%',
            render: (text: string, record: ComparisonRow) => <DataField text={text} record={record} />,
        },
        {
            title: labelB,
            dataIndex: 'b',
            key: 'b',
            width: '30%',
            render: (text: string, record: ComparisonRow) => <DataField text={text} record={record} />,
        },
    ];

    return (
        <Table<ComparisonRow>
            columns={columns}
            dataSource={dataSource}
            pagination={false}
            bordered
            size={nested ? 'small' : 'middle'}
            rowKey='key'
            expandable={{
                defaultExpandAllRows: false,
                expandRowByClick: true,
                expandedRowRender: (record: ComparisonRow) => {
                    if (record.type === 'object' && record.childrenData && record.childrenData.length > 0) {
                        return (
                            <Table<ComparisonRow>
                                columns={columns}
                                dataSource={record.childrenData}
                                pagination={false}
                                bordered
                                size='small'
                                rowKey='key'
                                expandable={{
                                    defaultExpandAllRows: false,
                                    expandRowByClick: true,
                                    expandedRowRender: (nestedRecord: ComparisonRow) => {
                                        // Rekursive Behandlung für weitere Verschachtelung
                                        if (nestedRecord.type === 'object' && nestedRecord.childrenData) {
                                            return (
                                                <Table<ComparisonRow>
                                                    columns={columns}
                                                    dataSource={nestedRecord.childrenData}
                                                    pagination={false}
                                                    bordered
                                                    size='small'
                                                    rowKey='key'
                                                />
                                            );
                                        }
                                        if (nestedRecord.type === 'array') {
                                            return (
                                                <ArraySelector
                                                    arrayA={isArray(nestedRecord.valueA) ? nestedRecord.valueA : []}
                                                    arrayB={isArray(nestedRecord.valueB) ? nestedRecord.valueB : []}
                                                    labelA={labelA}
                                                    labelB={labelB}
                                                    parentKey={nestedRecord.key}
                                                />
                                            );
                                        }
                                        return null;
                                    },
                                    rowExpandable: (nestedRecord: ComparisonRow) =>
                                        nestedRecord.type === 'object' || nestedRecord.type === 'array',
                                }}
                            />
                        );
                    }
                    if (record.type === 'array') {
                        return (
                            <ArraySelector
                                arrayA={isArray(record.valueA) ? record.valueA : []}
                                arrayB={isArray(record.valueB) ? record.valueB : []}
                                labelA={labelA}
                                labelB={labelB}
                                parentKey={record.key}
                            />
                        );
                    }
                    return null;
                },
                rowExpandable: (record: ComparisonRow) => record.type === 'object' || record.type === 'array',
            }}
            style={nested ? { marginTop: 0 } : { marginTop: 24 }}
        />
    );
};
