import { Button, Form, Input } from 'antd';
import { AddGroup } from '../../api/models';

interface GroupFormProps {
    initialValues?: Partial<AddGroup>;
    onSubmit: (values: AddGroup) => void;
    onCancel: () => void;
}

export const GroupForm: React.FC<GroupFormProps> = ({ initialValues, onSubmit, onCancel }) => (
    <Form initialValues={initialValues} onFinish={onSubmit} layout='vertical' style={{ maxWidth: 400 }}>
        <Form.Item name='name' label='Name' rules={[{ required: true }]}>
            <Input />
        </Form.Item>
        <Form.Item name='description' label='Description' rules={[{ required: true }]}>
            <Input />
        </Form.Item>
        <Form.Item>
            <Button htmlType='submit' type='primary'>
                Save
            </Button>
            <Button onClick={onCancel} style={{ marginLeft: 8 }}>
                Cancel
            </Button>
        </Form.Item>
    </Form>
);
