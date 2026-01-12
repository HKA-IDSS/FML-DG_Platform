import { useGroup } from 'hooks/groups';
import { ComparisonRow } from '../pages/comparison/types';
import { Spin } from 'antd';
import { useStrategyById } from 'hooks/strategies';
import { useUserName } from 'hooks/users';

interface DataFieldProps {
    text: string;
    record: ComparisonRow;
}

export const DataField = ({ text, record }: DataFieldProps) => {
    switch (record.key) {
        case 'belonging_group':
            return <DynamicGroupDataField text={text} />;
        case 'strategy_governance_id':
            return <DynamicStartegyDataField text={text} />;
        case 'proposer':
            return <DynamicUserDataField text={text} />;
        default:
            return <span>{text}</span>;
    }
};

export const DynamicGroupDataField = ({ text }: Pick<DataFieldProps, 'text'>) => {
    const { data, isLoading } = useGroup(text);

    return (
        <Spin spinning={isLoading}>
            <span>{data?.name ?? text}</span>
        </Spin>
    );
};

export const DynamicStartegyDataField = ({ text }: Pick<DataFieldProps, 'text'>) => {
    const { data, isLoading } = useStrategyById(text);

    return (
        <Spin spinning={isLoading}>
            <span>{data?.name ?? text}</span>
        </Spin>
    );
};

export const DynamicUserDataField = ({ text }: Pick<DataFieldProps, 'text'>) => {
    const { data, isLoading } = useUserName(text);

    return <Spin spinning={isLoading}>{data?.name ?? text}</Spin>;
};
