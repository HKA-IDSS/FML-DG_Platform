import { useParams } from 'react-router-dom';
import { Divider, Flex, Typography } from 'antd';
import { ProposalModalForm } from './ProposalModalForm';
import { ProposalDataTable } from './ProposalDataTable';
import { useStrategyById } from '../../../hooks/strategies';

function Proposal() {
    const { id } = useParams();
    const { data: strategy, isLoading } = useStrategyById(id);

    if (!id) {
        return <div>Strategy ID Error. Id is null {id}</div>;
    }

    if (isLoading || !strategy) {
        return <div>Load Strategy...</div>;
    }

    return (
        <Flex className="proposal-page" vertical gap={'middle'}>
            <h1 className="text-lg font-semibold">Strategy</h1>
            <Divider />
            <div className="flex flex-row justify-between">
                <Typography.Title level={5}>Proposals for {strategy.name}</Typography.Title>

                <div className="flex flex-row gap-5">
                    <ProposalModalForm title="New Proposal" OpenModalButtonText="Make a new proposal" />
                </div>
            </div>
            <Flex>
                <ProposalDataTable style={{ width: '100%' }} strategy={strategy} />
            </Flex>
        </Flex>
    );
}

export default Proposal;
