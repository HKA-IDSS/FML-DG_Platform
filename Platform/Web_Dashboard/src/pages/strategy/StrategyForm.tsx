import React from 'react';
import { Button, Form, Input, Select, Space, Divider } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { AddStrategy, Group, Strategy, Correctness, Bias } from '../../api/models';
import { useDatasets } from 'hooks/datasets';

export type CorrectnessForm = Omit<Correctness, 'quality_req_type'> & { name: string; reasoning: string };
export type BiasForm = Omit<Bias, 'quality_req_type'> & { name: string; reasoning: string };

export type StrategySubmit = AddStrategy & {
    correctness: CorrectnessForm[];
    bias: BiasForm[];
};

interface StrategyFormProps {
    initialValues?: Partial<Strategy>;
    groups: Group[];
    onSubmit: (values: StrategySubmit) => void;
    onCancel: () => void;
    loading?: boolean;
}

export const StrategyForm: React.FC<StrategyFormProps> = ({ initialValues, groups, onSubmit, onCancel, loading }) => {
    return (
        <Form
            initialValues={initialValues}
            onFinish={(values) => {
                onSubmit(values);
            }}
            layout='vertical'
            style={{ maxWidth: 700 }}
        >
            <Form.Item name='name' label='Name' rules={[{ required: true, message: 'Please enter a strategy name' }]}>
                <Input />
            </Form.Item>
            <Form.Item
                name='belonging_group'
                label='Group'
                hidden={!!initialValues}
                rules={[{ required: true, message: 'Please select a group!' }]}
            >
                <Select
                    showSearch
                    placeholder='Select a group'
                    optionFilterProp='label'
                    filterOption={(input, option) =>
                        (option?.label ?? '').toString().toLowerCase().includes(input.toLowerCase())
                    }
                    options={groups.map((group) => ({
                        value: group._governance_id,
                        label: group.name,
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
            <Divider orientation='left'>Comments</Divider>
            <Form.List name='comments' initialValue={initialValues?.comments || []}>
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(({ key, name, ...restField }) => (
                            <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align='baseline'>
                                <Form.Item {...restField} name={name} label='Comment' rules={[{ required: false }]}>
                                    <Input placeholder='Comment' />
                                </Form.Item>
                                <Button icon={<MinusCircleOutlined />} danger onClick={() => remove(name)} />
                            </Space>
                        ))}
                        <Form.Item>
                            <Button type='dashed' onClick={() => add()} block icon={<PlusOutlined />}>
                                Add Comment
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
