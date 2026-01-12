import { useState } from 'react';
import { Button, Card, Col, Divider, Form, Input, Row, Select, Table } from 'antd';
import { AddOrganisation, AddUser, Organisation, User } from 'api/models';
import { useAllUsers, useCreateOrg, useCreateUser, useDeleteOrg, useDeleteUser, useOrganizations } from 'hooks/admin';
import { ModalForm } from './ModalForm';

type ModalType = 'org' | 'user' | null;

const AdminPage = () => {
    const { data: organisations, isLoading: orgLoading } = useOrganizations();
    const { data: users, isLoading: usersLoading } = useAllUsers();
    const deleteUser = useDeleteUser();
    const createOrg = useCreateOrg();
    const createUser = useCreateUser();
    const deleteOrg = useDeleteOrg();

    const [modalType, setModalType] = useState<ModalType>(null);

    // Organization form
    const [orgForm] = Form.useForm();
    const handleOrgSubmit = (values: AddOrganisation) => {
        createOrg.mutate(values, {
            onSuccess: () => {
                orgForm.resetFields();
                setModalType(null);
            },
        });
    };

    // User form
    const [userForm] = Form.useForm();
    const handleUserSubmit = (values: AddUser) => {
        createUser.mutate(values, {
            onSuccess: () => {
                userForm.resetFields();
                setModalType(null);
            },
        });
    };

    return (
        <div>
            <h1 className='text-lg font-semibold'>Admin Settings</h1>
            <Divider />
            <Row gutter={32}>
                <Col span={12}>
                    <Button type='primary' style={{ marginBottom: 16 }} onClick={() => setModalType('org')}>
                        Create Organization
                    </Button>
                    <Card title='Organizations' loading={orgLoading}>
                        <Table
                            dataSource={organisations}
                            rowKey='_id'
                            columns={[
                                { title: 'Name', dataIndex: 'name' },
                                {
                                    title: 'Users',
                                    dataIndex: 'users',
                                    render: (val: string[]) =>
                                        val
                                            .map((id) => users?.find((user) => user._governance_id === id)?.name ?? id)
                                            .join(', '),
                                },
                                {
                                    title: 'Action',
                                    key: 'action',
                                    render: (_: any, record: Organisation) => (
                                        <>
                                            <Button
                                                size='small'
                                                danger
                                                onClick={() => deleteOrg.mutate(record._governance_id)}
                                            >
                                                Delete
                                            </Button>
                                        </>
                                    ),
                                },
                            ]}
                            pagination={false}
                            size='small'
                        />
                    </Card>
                </Col>
                <Col span={12}>
                    <Button type='primary' style={{ marginBottom: 16 }} onClick={() => setModalType('user')}>
                        Create User
                    </Button>
                    <Card title='Users' loading={usersLoading}>
                        <Table
                            dataSource={users}
                            rowKey='_id'
                            columns={[
                                { title: 'Name', dataIndex: 'name' },
                                { title: 'Description', dataIndex: 'description' },
                                {
                                    title: 'Organization',
                                    dataIndex: 'organisation_id',
                                    render: (id: string) =>
                                        organisations?.find((o) => o._governance_id === id)?.name || id,
                                },
                                {
                                    title: 'Action',
                                    key: 'action',
                                    render: (_: any, record: User) => (
                                        <>
                                            <Button
                                                size='small'
                                                danger
                                                onClick={() => deleteUser.mutate(record._governance_id)}
                                            >
                                                Delete
                                            </Button>
                                        </>
                                    ),
                                },
                            ]}
                            pagination={false}
                            size='small'
                        />
                    </Card>
                </Col>
            </Row>

            <ModalForm open={modalType === 'org'} title='Create Organization' onCancel={() => setModalType(null)}>
                <Form form={orgForm} layout='vertical' onFinish={handleOrgSubmit}>
                    <Form.Item name='name' label='Organization Name' rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Button type='primary' htmlType='submit' loading={createOrg.isPending} style={{ marginTop: 8 }}>
                        Create Organization
                    </Button>
                </Form>
            </ModalForm>

            <ModalForm open={modalType === 'user'} title='Create User' onCancel={() => setModalType(null)}>
                <Form form={userForm} layout='vertical' onFinish={handleUserSubmit}>
                    <Form.Item name='name' label='User Name' rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name='description' label='Description' rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name='organisation_id' label='Organization' rules={[{ required: true }]}>
                        <Select
                            options={organisations?.map((org) => ({
                                value: org._governance_id,
                                label: org.name,
                            }))}
                            loading={orgLoading}
                        />
                    </Form.Item>
                    <Button type='primary' htmlType='submit' loading={createUser.isPending} style={{ marginTop: 8 }}>
                        Create User
                    </Button>
                </Form>
            </ModalForm>
        </div>
    );
};

export default AdminPage;
