import { Correctness } from '../../../../../api/models';
import { Descriptions } from 'antd';

export function CorrectnessDescription({ record }: { record: Correctness }) {
    return <Descriptions
        title="Details"
        bordered
        items={[
            {
                key: '1',
                label: 'Requirement Type',
                children: record.quality_req_type, // Link to ML model details page
                span: 3,
            },
            {
                key: '2',
                label: 'Metric',
                children: record.metric,
            },
            {
                key: '3',
                label: 'Required Minimum Value',
                children: record.required_min_value,
            },
            {
                key: '4',
                label: 'Required Maximum Value',
                children: record.required_max_value,
            },
        ]}
    />;
}
