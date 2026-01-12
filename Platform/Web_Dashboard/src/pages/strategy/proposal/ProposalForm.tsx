import { Button, Form, Input, InputNumber, notification, Radio, Select } from 'antd';
import React, { useState } from 'react';
import { AddProposal, ProposalType } from '../../../api/models';
import { FormProps, useParams } from 'react-router-dom';
import { useGroups } from '../../../hooks/groups';
import { useDatasets } from '../../../hooks/datasets';
import { useMLModels } from '../../../hooks/mlmodels';
import { RequirementsForm } from './QualityRequirementForm';
import api from '../../../api';
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query';

interface ProposalFormProps extends FormProps {
    initialValues: Partial<AddProposal>;
    onSuccess?: () => void;
}

type ProposalFormState = {
    proposalContent: 'configuration' | 'requirement';
};

export const ProposalForm: React.FC<ProposalFormProps> = () => {
    const { id } = useParams();
    const [notify, contextHolder] = notification.useNotification();
    const [form] = Form.useForm();
    const { data: groups, isLoading: isLoadingGroups } = useGroups();
    const [contentType, setContentType] = useState<ProposalFormState>({ proposalContent: 'configuration' });
    const [submittable, setSubmittable] = React.useState<boolean>(false);

    const values = Form.useWatch([], form);

    const qc = useQueryClient();

    React.useEffect(() => {
        form
            .validateFields({ validateOnly: true })
            .then(() => setSubmittable(true))
            .catch(() => setSubmittable(false));
    }, [form, values]);

    const onSelectProposalContent = (proposalContent: ProposalFormState['proposalContent']) => {
        setContentType({ ...contentType, proposalContent: proposalContent });
    };

    const success = () => {
        notify.open({
            type: 'success',
            message: 'Successfully submitted proposal',
            placement: 'bottomRight',
        });
    };

    const error = () => {
        notify.open({
            type: 'error',
            message: 'Error submitting proposal',
            placement: 'bottomRight',
        });
    };

    const handleSubmit = async (values: any) => {
        if (!groups || !id) {
            console.error('Group or Strategy ID is missing');
            error();
            return;
        }
        if (contentType.proposalContent === 'configuration') {
            let proposal: AddProposal = {
                name: values.name,
                group: values.group,
                strategy_id: id!,
                operation_variant: 'create',
                content_variant: ProposalType.CONFIGURATION,
                proposal_content: {
                    ml_model_id: values.ml_model_id,
                    ml_model_version: values.ml_model_version,
                    dataset_id: values.dataset_id,
                    dataset_version: values.dataset_version,
                    number_of_rounds: values.number_of_rounds,
                    number_of_ho_rounds: values.number_of_ho_rounds,
                },
                reasoning: values.reasoning || '',
            };
            await api.insertConfigurationProposal(proposal);
        } else {
            const proposal: AddProposal = {
                name: values.name,
                group: values.group,
                strategy_id: id!,
                operation_variant: 'create',
                content_variant: ProposalType.QUALITY_REQUIREMENT,
                proposal_content: {
                    quality_requirement: {
                        ...values.quality_requirement,
                    },
                },
                reasoning: values.reasoning || '',
            };
            await api.insertQualityRequirementProposal(proposal);
        }

        success();
        form.resetFields();
        qc.invalidateQueries({ queryKey: ['proposals'] });
    };

    return (
        <Form
            initialValues={contentType}
            layout="vertical"
            style={{ maxWidth: 400 }}
            form={form}
        >
            {contextHolder}
            <Form.Item name="name" label="Proposal Name" rules={[{ required: true, type: 'string' }]}>
                <Input />
            </Form.Item>
            <Form.Item name="group" label="Group" rules={[{ required: true }]}>
                <Select
                    loading={isLoadingGroups}
                    options={groups ? groups.map((group) => ({ label: group.name, value: group._governance_id })) : []}
                />
            </Form.Item>
            <Form.Item name="reasoning" label="Reasoning" rules={[{ type: 'string' }]}>
                <Input />
            </Form.Item>
            <Form.Item label="Proposal Type" name="proposalContent" rules={[{ required: true }]}>
                <Radio.Group value={contentType.proposalContent}
                             onChange={e => onSelectProposalContent(e.target.value)}>
                    <Radio.Button value="configuration">Training Configuration</Radio.Button>
                    <Radio.Button value="requirement">Quality Requirement</Radio.Button>
                </Radio.Group>
            </Form.Item>
            {contentType!.proposalContent === 'configuration' ? <ConfigurationForm /> : <RequirementsForm />}
            <Form.Item>
                <Button htmlType="submit" type="primary" disabled={!submittable}
                        onClick={() => handleSubmit(form.getFieldsValue())}>
                    Save
                </Button>
            </Form.Item>
        </Form>
    );
};

const ConfigurationForm: React.FC = () => {
    const { data: datasets, isLoading: isLoadingDatasets } = useDatasets();
    const { data: mlModels, isLoading: mlModelsLoading } = useMLModels();
    const form = Form.useFormInstance();

    // Watch currently selected governance IDs
    const selectedModelGovId = Form.useWatch(['ml_model_id'], form) as string | undefined;
    const selectedDatasetGovId = Form.useWatch(['dataset_id'], form) as string | undefined;

    // Fetch latest model/dataset
    const latestModelQuery = useQuery({
        queryKey: ['ml-model-latest', selectedModelGovId],
        enabled: !!selectedModelGovId,
        queryFn: () => api.getMLModelById(selectedModelGovId!, -1).then(r => r.data),
    });

    const latestDatasetQuery = useQuery({
        queryKey: ['dataset-latest', selectedDatasetGovId],
        enabled: !!selectedDatasetGovId,
        queryFn: () => api.getDatasetById(selectedDatasetGovId!, -1).then(r => r.data),
    });

    const modelMaxVersion = latestModelQuery.data?._version ?? 0;
    const datasetMaxVersion = latestDatasetQuery.data?._version ?? 0;

    // Fetch all versions 1..N in parallel
    const modelVersionsQueries = useQueries({
        queries:
            selectedModelGovId && modelMaxVersion > 0
                ? Array.from({ length: modelMaxVersion }, (_, i) => i + 1).map((v) => ({
                    queryKey: ['ml-model-by-version', selectedModelGovId, v],
                    queryFn: () => api.getMLModelById(selectedModelGovId, v).then(r => r.data),
                    enabled: true,
                }))
                : [],
    });

    const datasetVersionsQueries = useQueries({
        queries:
            selectedDatasetGovId && datasetMaxVersion > 0
                ? Array.from({ length: datasetMaxVersion }, (_, i) => i + 1).map((v) => ({
                    queryKey: ['dataset-by-version', selectedDatasetGovId, v],
                    queryFn: () => api.getDatasetById(selectedDatasetGovId, v).then(r => r.data),
                    enabled: true,
                }))
                : [],
    });

    const modelVersionsLoading =
        latestModelQuery.isFetching || modelVersionsQueries.some(q => q.isFetching);

    const datasetVersionsLoading =
        latestDatasetQuery.isFetching || datasetVersionsQueries.some(q => q.isFetching);

    const modelVersionOptions =
        modelVersionsQueries.length > 0
            ? modelVersionsQueries
                .map(q => q.data)
                .filter(Boolean)
                .sort((a: any, b: any) => b._version - a._version)
                .map((m: any) => ({ label: `v${m._version}`, value: m._version }))
            : [];

    const datasetVersionOptions =
        datasetVersionsQueries.length > 0
            ? datasetVersionsQueries
                .map(q => q.data)
                .filter(Boolean)
                .sort((a: any, b: any) => b._version - a._version)
                .map((d: any) => ({ label: `v${d._version}`, value: d._version }))
            : [];

    return (
        <>
            <Form.Item name={['ml_model_id']} label="Machine Learning Model" rules={[{ required: true }]}>
                <Select
                    options={mlModels ? mlModels.map((m) => ({ label: m.name, value: m._governance_id })) : []}
                    loading={mlModelsLoading}
                    placeholder="Select a model"
                    onChange={() => {
                        // reset version when model changes
                        form.setFieldValue(['ml_model_version'], undefined);
                    }}
                />
            </Form.Item>

            {/* ML model version dropdown */}
            <Form.Item name={['ml_model_version']} label="Model Version" rules={[{ required: true }]}>
                <Select
                    placeholder={selectedModelGovId ? 'Select model version' : 'Select a model first'}
                    disabled={!selectedModelGovId}
                    options={modelVersionOptions}
                    loading={modelVersionsLoading}
                />
            </Form.Item>

            <Form.Item name={['dataset_id']} label="Dataset Schema" rules={[{ required: true }]}>
                <Select
                    options={datasets ? datasets.map((d) => ({ label: d.name, value: d._governance_id })) : []}
                    loading={isLoadingDatasets}
                    placeholder="Select a dataset"
                    onChange={() => {
                        // reset version when dataset changes
                        form.setFieldValue(['dataset_version'], undefined);
                    }}
                />
            </Form.Item>

            {/* Dataset version dropdown */}
            <Form.Item name={['dataset_version']} label="Dataset Schema Version" rules={[{ required: true }]}>
                <Select
                    placeholder={selectedDatasetGovId ? 'Select dataset version' : 'Select a dataset first'}
                    disabled={!selectedDatasetGovId}
                    options={datasetVersionOptions}
                    loading={datasetVersionsLoading}
                />
            </Form.Item>

            <Form.Item
                name={['number_of_rounds']}
                label="Number of training rounds"
                rules={[{ required: true, type: 'number' }]}
            >
                <InputNumber style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
                name={['number_of_ho_rounds']}
                label="Number of training rounds for Hyperparameter Optimization"
                rules={[{ required: true, type: 'number' }]}
            >
                <InputNumber style={{ width: '100%' }} />
            </Form.Item>
        </>
    );
};
