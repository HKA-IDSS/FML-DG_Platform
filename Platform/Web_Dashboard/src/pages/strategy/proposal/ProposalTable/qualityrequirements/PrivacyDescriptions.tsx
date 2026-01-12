import { Privacy } from '../../../../../api/models';
import { Descriptions } from 'antd';

export default function PrivacyDescriptions({ record }: { record: Privacy }) {
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
        ]}
    />;
}
