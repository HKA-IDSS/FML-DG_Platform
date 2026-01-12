import React from 'react';
import { Button, Form, Input, Select, Space, Switch, Tag, Upload, message } from 'antd';
import { MinusCircleOutlined, PlusOutlined, ImportOutlined } from '@ant-design/icons';
import { AddDataset, Feature, FeatureType, EncodingType, Group } from '../../api/models';
import { TagInput } from '../../components/input/TagInput';
import { useAllStrategies } from '../../hooks/strategies';

interface DatasetFormProps {
    initialValues?: Partial<AddDataset>;
    onSubmit: (values: AddDataset) => void;
    onCancel: () => void;
    loading?: boolean;
    groups: Group[];
}

const featureTypeOptions = Object.values(FeatureType).map((ft) => ({
    value: ft,
    label: ft,
}));

const encodingTypeOptions = Object.values(EncodingType).map((et) => ({
    value: et,
    label: et,
}));

export const DatasetForm: React.FC<DatasetFormProps> = ({ initialValues, onSubmit, onCancel, loading, groups }) => {
    const [form] = Form.useForm();
    const features = Form.useWatch('features', form) || [];
    const { data: strategies = [], isLoading } = useAllStrategies();

    // Import JSON logic
    const importProps = {
        accept: '.json',
        showUploadList: false,
        beforeUpload: (file: File) => {
            const fileReader = new FileReader();
            fileReader.readAsText(file, 'UTF-8');
            fileReader.onload = (e) => {
                try {
                    const json = JSON.parse(e.target?.result as string);
                    if (!json.name || !json.features) throw new Error('Missing required fields');
                    form.setFieldsValue(json);
                    message.success('Imported dataset from JSON');
                } catch (e: any) {
                    message.error('Invalid JSON: ' + e.message);
                }
            };
            return false;
        },
    };

    return (
        <Form
            form={form}
            initialValues={initialValues}
            className='min-w-[1000px]'
            onFinish={(values) => {
                // Ensure order_in_dataset is set and valid_values is present
                values.features = (values.features || []).map((f: Feature, i: number) => {
                    let valid_values = f.valid_values ?? [];
                    // Convert valid_values to numbers for numeric types
                    if (
                        ['integer', 'long', 'float', 'double'].includes(
                            f.type && typeof f.type === 'string' ? f.type : '',
                        )
                    ) {
                        valid_values = valid_values.map((v: any) => {
                            const input = v.toString().replace(',', '.');

                            if (input === '') return undefined;

                            const output = isNaN(Number(input)) ? v : Number(input);

                            if (f.type === FeatureType.INTEGER || f.type === FeatureType.LONG) {
                                return Math.round(output);
                            }

                            return output;
                        });
                    }

                    if (f.type === FeatureType.BOOLEAN) {
                        valid_values = [true, false];
                    }

                    return {
                        ...f,
                        order_in_dataset: i + 1,
                        valid_values,
                    };
                });
                // Remove group_governance_id from payload if not needed by backend
                delete values.group_governance_id;
                const dataset: AddDataset = {
                    ...values,
                    features: values.features,
                };
                onSubmit(dataset);
            }}
            layout='vertical'
            style={{ maxWidth: 700 }}
        >
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
                <Upload {...importProps}>
                    <Button icon={<ImportOutlined />}>Import JSON</Button>
                </Upload>
            </div>
            <Form.Item name='name' label='Name' rules={[{ required: true, message: 'Please enter a dataset name' }]}>
                <Input />
            </Form.Item>
            <Form.Item name='description' label='Description'>
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
                    loading={isLoading}
                    filterOption={(input, option) =>
                        (option?.label ?? '').toString().toLowerCase().includes(input.toLowerCase())
                    }
                    options={strategies.map((strategy) => ({
                        value: strategy._governance_id,
                        label: strategy.name,
                    }))}
                />
            </Form.Item>
            <Form.Item name='structured' label='Structured' valuePropName='checked' initialValue={false}>
                <Switch />
            </Form.Item>

            <h1 className='font-semibold'>Features</h1>
            <Form.List name='features' initialValue={initialValues?.features || []}>
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(({ key, name, ...restField }, idx) => {
                            // For sub_features: all other feature names except this one
                            const availableSubFeatures = features
                                .filter((_: any, i: number) => i !== idx)
                                .map((f: Feature) => f?.name)
                                .filter(Boolean);

                            return (
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
                                    <Tag color='blue'>#{idx + 1}</Tag>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'name']}
                                        label='Name'
                                        rules={[{ required: true, message: 'Feature name required' }]}
                                    >
                                        <Input placeholder='Feature name' />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'description']}
                                        label='Description'
                                        rules={[{ required: true, message: 'Please enter a description' }]}
                                    >
                                        <Input placeholder='Description' />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'type']}
                                        label='Type'
                                        rules={[{ required: true, message: 'Type required' }]}
                                    >
                                        <Select options={featureTypeOptions} style={{ minWidth: 100 }} />
                                    </Form.Item>
                                    <Form.Item {...restField} name={[name, 'preprocessing']} label='Encoding'>
                                        <Select allowClear options={encodingTypeOptions} style={{ minWidth: 120 }} />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'group']}
                                        label='Group'
                                        valuePropName='checked'
                                        initialValue={false}
                                    >
                                        <Switch />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'valid_values']}
                                        label='Valid Values'
                                        tooltip='For categoricals: enter allowed categories. For numbers: enter allowed values or ranges (e.g. 1, 2)'
                                    >
                                        <TagInput
                                            initialValue={features?.[idx]?.valid_values}
                                            valueChange={(val: string[]) => {
                                                const updated = [...features];
                                                updated[idx] = { ...updated[idx], valid_values: val };
                                                form.setFieldValue(['features'], updated);
                                            }}
                                            textNew='Add Value'
                                            textNone='No constraints'
                                        />
                                    </Form.Item>
                                    <Form.Item
                                        noStyle
                                        shouldUpdate={(prev, curr) =>
                                            prev.features?.[name]?.group !== curr.features?.[name]?.group ||
                                            prev.features?.length !== curr.features?.length
                                        }
                                    >
                                        {({ getFieldValue }) =>
                                            getFieldValue(['features', name, 'group']) ? (
                                                <Form.Item
                                                    {...restField}
                                                    name={[name, 'sub_features']}
                                                    label='Sub Features'
                                                >
                                                    <Select
                                                        mode='multiple'
                                                        style={{ minWidth: 120 }}
                                                        placeholder='Sub features'
                                                        options={availableSubFeatures.map((name: string) => ({
                                                            value: name,
                                                            label: name,
                                                        }))}
                                                    />
                                                </Form.Item>
                                            ) : null
                                        }
                                    </Form.Item>
                                    <Button
                                        icon={<MinusCircleOutlined />}
                                        danger
                                        onClick={() => remove(name)}
                                        style={{ marginTop: 30 }}
                                    />
                                </Space>
                            );
                        })}
                        <Form.Item>
                            <Button type='dashed' onClick={() => add()} block icon={<PlusOutlined />}>
                                Add Feature
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
