import { Bias } from '../../../../../api/models';
import { Descriptions } from 'antd';

export function BiasDescriptions({ record }: { record: Bias }) {
    return <Descriptions
        title="Details"
        bordered
        items={[
            {
                key: '1',
                label: 'Requirement Type',
                children: record.quality_req_type,
                span: 3,
            },
            {
                key: '2',
                label: 'Vulnerable Feature',
                children: record.vulnerable_feature,
            },
            {
                key: '3',
                label: 'Accepted Threshold',
                children: record.accepted_threshold,
            },
        ]} />;
}
