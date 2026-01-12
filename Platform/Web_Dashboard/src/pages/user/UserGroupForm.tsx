import { Button, Form, Select, Space } from 'antd';
import { Group } from '../../api/models';

interface UserGroupFormProps {
    availableGroups: Group[];
    onSubmit: (groupIds: string[]) => void;
    onCancel: () => void;
    loading?: boolean;
}

export const UserGroupForm: React.FC<UserGroupFormProps> = ({ availableGroups, onSubmit, onCancel, loading }) => {
    return (
        <Form layout='vertical' onFinish={(values) => onSubmit(values.groups)} style={{ maxWidth: 400 }}>
            <Form.Item
                label='Groups'
                name='groups'
                rules={[{ required: true, message: 'Please select at least one group!' }]}
            >
                <Select mode='multiple' placeholder='Select groups to join' optionLabelProp='label'>
                    {availableGroups.map((group) => (
                        <Select.Option key={group._governance_id} value={group._governance_id} label={group.name}>
                            <Space>{group.name}</Space>
                        </Select.Option>
                    ))}
                </Select>
            </Form.Item>
            <Form.Item>
                <Button htmlType='submit' type='primary' loading={loading}>
                    Join
                </Button>
                <Button onClick={onCancel} style={{ marginLeft: 8 }}>
                    Cancel
                </Button>
            </Form.Item>
        </Form>
    );
};
