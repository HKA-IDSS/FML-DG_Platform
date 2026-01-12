import { Proposal, Configuration, ProposalType } from '../../../../api/models';
import { Descriptions } from 'antd';
import type { DescriptionsProps } from 'antd';
import { EntityLink } from '../../../../components/EntityLink';
import { useDatasets } from '../../../../hooks/datasets';
import { useMLModels } from '../../../../hooks/mlmodels';
import { useMemo } from 'react';


// Extending AddProposal to have the correct typing for proposal_content
export interface ConfigurationProposal extends Proposal {
    proposal_content: Configuration;
    content_variant: ProposalType.CONFIGURATION;
}


export interface ConfigurationExpandableContentProps {
    record: ConfigurationProposal;
}


export default function ConfigurationExpandableContent({ record }: ConfigurationExpandableContentProps) {
    // Assume these are cached so it is not loaded for every single component
    const { data: datasetSchemas } = useDatasets();
    const { data: mlModelSchemas } = useMLModels();

    const mlNameById = useMemo(
        () => Object.fromEntries((mlModelSchemas ?? []).map((m) => [m._governance_id, m.name] as const)),
        [mlModelSchemas],
    );

    const dsNameById = useMemo(
        () => Object.fromEntries((datasetSchemas ?? []).map((d) => [d._governance_id, d.name] as const)),
        [datasetSchemas],
    );
    console.log(record);

    const items: DescriptionsProps['items'] = [
        {
            key: '1',
            label: 'ML Model',
            children: (
                <EntityLink kind={"ml-model"} governanceId={record.proposal_content.ml_model_id}>
                    {mlNameById[record.proposal_content.ml_model_id] ?? record.proposal_content.ml_model_id}
                </EntityLink>
            ),
            span: 2,
        },
        {
            key: '2',
            label: 'ML Model Version',
            children: record.proposal_content.ml_model_version,
        },
        {
            key: '3',
            label: 'Dataset ID / Schema',
            children: (
                <EntityLink kind="dataset" governanceId={record.proposal_content.dataset_id}>
                    {dsNameById[record.proposal_content.dataset_id] ?? record.proposal_content.dataset_id}
                </EntityLink>
            ),
            span: 2,
        },
        {
            key: '3.1',
            label: 'Dataset Schema Version',
            children: record.proposal_content.dataset_version,
        },
        {
            key: '4',
            label: 'No. of Hyper Optimization Rounds',
            children: record.proposal_content.number_of_ho_rounds,
        },
        {
            key: '5',
            label: 'No. of Training Rounds',
            children: record.proposal_content.number_of_rounds,
            span: 2,
        },
    ];

    return <Descriptions
        title="Details"
        bordered
        items={items}
    />;

}
