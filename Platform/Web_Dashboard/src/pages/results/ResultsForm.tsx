import React, { useEffect, useState } from 'react';
import { Button, Checkbox, Flex, Form, Radio, Select, Switch } from 'antd';
import { useAllStrategies } from '../../hooks/strategies';
import { EvaluationResult, Metric } from '../../api/models';
import { useTrainingConfigurations } from '../../hooks/trainingConfiguration';
import type { DefaultOptionType } from 'antd/es/select';

interface ResultViewForm {
    initialValues?: Partial<EvaluationResult>;
    onSubmit: (values: EvaluationResult, formValues: any) => void;
    onCancel: () => void;
}

export const ResultForm: React.FC<ResultViewForm> = ({ initialValues, onSubmit, onCancel }) => {
    const [form] = Form.useForm();
    const { data: strategies, isLoading: strategiesLoading } = useAllStrategies();
    const [selectedStrategyId, setSelectedStrategyId] = useState<string>();
    const [configurationOptions, setConfigurationOptions] = useState<DefaultOptionType[]>([]);

    const { data: configurations, isLoading: configurationLoading } = useTrainingConfigurations(selectedStrategyId, -1);
    const metricTypes: Metric['type'][] = [
        'CrossEntropyLoss',
        'Accuracy',
        'F1ScoreMacro',
        'F1ScoreMicro',
        /*'CosineSimilarity',
        'CrossEntropy',*/
        'MCC'];
    useEffect(() => {
        if (!selectedStrategyId) {
            setConfigurationOptions([]);
            form.setFieldsValue({ configuration_id: undefined });
            return;
        }
        setConfigurationOptions(
            configurations?.map(config => ({
                // label: `Config ${config._id} - Model: ${config.ml_model_version} - Dataset: ${config.dataset_id} v${config.dataset_version}`,
                label: `Config ${config._id}`,
                value: config._id,
            })) ?? [],
        );
        form.setFieldsValue({ configuration_id: undefined });
    }, [selectedStrategyId, configurations, form]);

    const handleStrategyChange = (value: string) => {
        setSelectedStrategyId(value);
    };

    const handleSubmit = (values: any) => {
        onSubmit(values, form);
    };


    return (
        <Form
            form={form}
            initialValues={initialValues}
            onFinish={handleSubmit}
            style={{ display: 'flex', flexDirection: 'column', maxWidth: '100%' }}
        >
            <Form.Item name="strategy_id" label="Choose Strategy"
                       rules={[{ required: true, message: 'Please select a Strategy' }]}>
                <Select
                    placeholder="Select a strategy"
                    options={strategies?.map(s => ({ label: s.name, value: s._governance_id }))}
                    style={{ minWidth: 200 }}
                    loading={strategiesLoading}
                    onChange={handleStrategyChange}
                />
            </Form.Item>
            <Form.Item name="configuration_id" label="Choose Configuration"
                       rules={[{ required: true, message: 'Please select a configuration' }]}>
                <Select
                    placeholder="Select a configuration"
                    options={configurationOptions}
                    style={{ minWidth: 200 }}
                    loading={configurationLoading}
                    onChange={() => form.submit()}
                />
            </Form.Item>
            {/*<Form.Item name="configuration_id" label="Choose Dataset"*/}
            {/*           rules={[{ required: true, message: 'Please select a configuration' }]}>*/}
            {/*    <Select*/}
            {/*        placeholder="Select a configuration"*/}
            {/*        options={configurationOptions}*/}
            {/*        style={{ minWidth: 200 }}*/}
            {/*        loading={configurationLoading}*/}
            {/*    />*/}
            {/*</Form.Item>*/}
            {/*<Form.Item style={{ alignSelf: 'flex-end', justifySelf: 'flex-end' }}>*/}
            {/*    <Button htmlType="submit" type="primary" onClick={() => {handleSubmit(form.getFieldsValue());}}>*/}
            {/*        Save*/}
            {/*    </Button>*/}
            {/*</Form.Item>*/}
        </Form>
    );
};
