import React, { useEffect } from 'react';
import { Button, Form, Input, Select, Space, Divider } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { AddMLModel, AlgorithmType, TypeHP } from '../../api/models';
import { useAllStrategies } from '../../hooks/strategies';
import { useDefaultMLModel } from 'hooks/mlmodels';
import MinMaxInput from 'components/input/MinMaxInput';

const algorithmOptions = Object.values(AlgorithmType).map((alg) => ({
    value: alg,
    label: alg,
}));

const typeHPOptions = Object.values(TypeHP).map((t) => ({
    value: t,
    label: t,
}));

interface MLModelFormProps {
    initialValues?: Partial<AddMLModel>;
    onSubmit: (values: AddMLModel) => void;
    onCancel: () => void;
    loading?: boolean;
}

export const MLModelForm: React.FC<MLModelFormProps> = ({ initialValues, onSubmit, onCancel, loading }) => {
    const [form] = Form.useForm();
    const algorithm = Form.useWatch(['model', 'algorithm'], form);

    const { data: defaultModel } = useDefaultMLModel(algorithm);

    // Fetch  all strategies
    const { data: strategies = [], isLoading: strategyLoading } = useAllStrategies();

    useEffect(() => {
        if (!initialValues?.model && defaultModel) {
            form.setFieldsValue({
                model: {
                    hyperparameters: defaultModel.hyperparameters,
                },
            });
        }
    }, [defaultModel, form, initialValues?.model]);

    return (
        <Form
            form={form}
            initialValues={initialValues}
            onFinish={(values) => {
                // Ensure hyperparameters is always an array
                //values.hyperparameters = values.hyperparameters || [];
                delete values.group_governance_id;
                onSubmit(values as AddMLModel);
            }}
            layout='vertical'
            style={{ maxWidth: 600 }}
        >
            <Form.Item name='name' label='Name' rules={[{ required: true, message: 'Please enter a model name' }]}>
                <Input />
            </Form.Item>
            <Form.Item
                name='strategy_governance_id'
                label='Strategy'
                rules={[{ required: true, message: 'Please select a strategy!' }]}
            >
                <Select
                    showSearch
                    placeholder={'Select a strategy'}
                    optionFilterProp='label'
                    loading={strategyLoading}
                    filterOption={(input, option) =>
                        (option?.label ?? '').toString().toLowerCase().includes(input.toLowerCase())
                    }
                    options={strategies.map((strategy) => ({
                        value: strategy._governance_id,
                        label: strategy.name,
                    }))}
                />
            </Form.Item>
            <Form.Item
                name='description'
                label='Description'
                rules={[{ required: true, message: 'Please enter a description' }]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                name={['model', 'algorithm']}
                label='Algorithm'
                hidden={!!initialValues}
                rules={[{ required: true, message: 'Please select an algorithm' }]}
            >
                <Select options={algorithmOptions} />
            </Form.Item>

            <Divider orientation='left'>Hyperparameters</Divider>
            <Form.List name={['model', 'hyperparameters']} initialValue={initialValues?.model?.hyperparameters || []}>
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(({ key, name, ...restField }) => (
                            <Space
                                key={key}
                                style={{
                                    display: 'flex',
                                    marginBottom: 8,
                                    alignItems: 'flex-start',
                                    border: '1px solid #eee',
                                    padding: 12,
                                    borderRadius: 4,
                                    width: '100%',
                                }}
                                align='start'
                            >
                                <Form.Item
                                    {...restField}
                                    name={[name, 'name']}
                                    label='Name'
                                    rules={[{ required: true, message: 'Name required' }]}
                                >
                                    <Input placeholder='Hyperparameter name' />
                                </Form.Item>
                                <Form.Item
                                    {...restField}
                                    name={[name, 'type_of_hyperparameter']}
                                    label='Type'
                                    rules={[{ required: true, message: 'Type required' }]}
                                >
                                    <Select options={typeHPOptions} style={{ minWidth: 120 }} />
                                </Form.Item>
                                <Form.Item shouldUpdate>
                                    {() => {
                                        const type = form.getFieldValue([
                                            'model',
                                            'hyperparameters',
                                            name,
                                            'type_of_hyperparameter',
                                        ]);

                                        if (type === 'float' || type === 'integer') {
                                            return (
                                                <Form.Item
                                                    {...restField}
                                                    name={[name, 'valid_values']}
                                                    label='Min/Max'
                                                    rules={[
                                                        { required: true, message: 'Please provide min and max' },
                                                        {
                                                            validator: (_, value) => {
                                                                if (
                                                                    !value ||
                                                                    value.length !== 2 ||
                                                                    value.some(
                                                                        (v: number) => v === undefined || v === null,
                                                                    )
                                                                ) {
                                                                    return Promise.reject(
                                                                        'Both min and max are required',
                                                                    );
                                                                }
                                                                if (value[0] > value[1]) {
                                                                    return Promise.reject(
                                                                        'Min must be less than or equal to Max',
                                                                    );
                                                                }
                                                                return Promise.resolve();
                                                            },
                                                        },
                                                    ]}
                                                >
                                                    {/* ✅ This is the fix! */}
                                                    <MinMaxInput />
                                                </Form.Item>
                                            );
                                        }

                                        return (
                                            <Form.Item
                                                {...restField}
                                                name={[name, 'valid_values']}
                                                label='Valid Values'
                                                rules={[{ required: true, message: 'Please provide valid values' }]}
                                            >
                                                <Select
                                                    mode='tags'
                                                    style={{ minWidth: 120 }}
                                                    placeholder='Valid values'
                                                />
                                            </Form.Item>
                                        );
                                    }}
                                </Form.Item>
                                <Button
                                    icon={<MinusCircleOutlined />}
                                    danger
                                    onClick={() => remove(name)}
                                    style={{ marginTop: 30 }}
                                />
                            </Space>
                        ))}
                        <Form.Item>
                            <Button type='dashed' onClick={() => add()} block icon={<PlusOutlined />}>
                                Add Hyperparameter
                            </Button>
                        </Form.Item>
                    </>
                )}
            </Form.List>

            <Form.Item>
                <Button htmlType='submit' type='primary' loading={loading}>
                    Save
                </Button>
                <Button onClick={onCancel} style={{ marginLeft: 8 }}>
                    Cancel
                </Button>
            </Form.Item>
        </Form>
    );
};
