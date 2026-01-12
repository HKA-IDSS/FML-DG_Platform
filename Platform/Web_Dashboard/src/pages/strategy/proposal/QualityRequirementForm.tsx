import React from 'react';
import { Form, Input, InputNumber, Select } from 'antd';
import { CorrectnessMethods } from '../../../api/models';

export const RequirementsForm: React.FC = () => {
    //const [selectedQualityRequirementType, setSelectedQualityRequirementType] = React.useState<string>('Correctness');
    const form = Form.useFormInstance();

    const qrType: string =
        Form.useWatch(['quality_requirement', 'quality_req_type'], form) ?? 'Correctness';

    const QualityRequirements = [
        'Correctness', 'Bias', 'Interpretability', 'Robustness', 'Efficient', 'Security', 'Privacy',
    ] as const;

    const subForm = () => {
        console.log(qrType);
        switch (qrType) {
            case 'Correctness':
                return <CorrectnessForm />;
                break;
            //case 'Bias': subForm = <BiasForm />; break;
            default:
                return <p className="m-3">Not Implemented</p>;
                break;
            // add others for future use...
        }
    };

    return (
        <Form.Item label="Quality Requirement">
            <Form.Item name={['quality_requirement', 'quality_req_type']} label="Requirement Type"
                       rules={[{ required: true }]}>
                <Select placeholder="Select Quality Requirement Type"
                        options={QualityRequirements.map(key => ({ value: key, label: key }))}
                />
            </Form.Item>
            {subForm()}
        </Form.Item>
    );
};

const CorrectnessForm: React.FC = () => {

    return (
        <>
            <Form.Item name={['quality_requirement', 'metric']} label="Metric">
                <Select placeholder="Choose Metric"
                        options={Object.values(CorrectnessMethods).map(v => ({ value: v, label: v }))} />
            </Form.Item>
            <Form.Item name={['quality_requirement', 'required_min_value']} label="Minimum Value"
                       rules={[{ required: true, type: 'number' }]}>
                <InputNumber style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name={['quality_requirement', 'required_max_value']} label="Maximum Value"
                       rules={[{ required: true, type: 'number' }]}>
                <InputNumber style={{ width: '100%' }} />
            </Form.Item>
        </>
    );
};

const BiasForm: React.FC = () => {

    return (
        <>
            <Form.Item name="vulnerable_feature" label="Vulnerable Feature"
                       rules={[{ required: true, type: 'string' }]}>
                <Input style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="accepted_threshold" label="Accepted Threshold"
                       rules={[{ required: true, type: 'number' }]}>
                <InputNumber style={{ width: '100%' }} />
            </Form.Item>
        </>
    );
};

// Other quality requirements can be extended in the future
