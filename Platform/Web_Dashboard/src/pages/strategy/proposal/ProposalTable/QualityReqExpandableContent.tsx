import { Proposal, ProposalType, QualityRequirement } from '../../../../api/models';
import { CorrectnessDescription } from './qualityrequirements/CorrectnessDescription';
import { BiasDescriptions } from './qualityrequirements/BiasDescriptions';
import PrivacyDescriptions from './qualityrequirements/PrivacyDescriptions';


// Extending AddProposal to have the correct typing for proposal_content
export interface QualityRequirementProposal extends Proposal {
    proposal_content: QualityRequirement;
    content_variant: ProposalType.QUALITY_REQUIREMENT;
}

export interface QualityReqExpandableContentProps {
    record: QualityRequirementProposal;
}

export default function QualityReqExpandableContent({ record }: QualityReqExpandableContentProps) {
    switch (record.proposal_content.quality_requirement.quality_req_type) {
        case 'Correctness':
            return <CorrectnessDescription record={record.proposal_content.quality_requirement} />;
        case 'Bias':
            return <BiasDescriptions record={record.proposal_content.quality_requirement} />;
        case 'Privacy':
            return <PrivacyDescriptions record={record.proposal_content.quality_requirement} />;
        case 'Interpretability':
        case 'Robustness':
        case 'Efficient':
        case 'Security':
        default:
            return null;
    }
}
