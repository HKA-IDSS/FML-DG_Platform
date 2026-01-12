import React, { useState } from 'react';
import { Button, Modal } from 'antd';
import { ProposalForm } from './ProposalForm';

interface ProposalModalFormProps {
    title: string;
    OpenModalButtonText: string;
    handleCancel?: () => void;
    showModal?: () => void;
}

export const ProposalModalForm = ({ title, OpenModalButtonText }: ProposalModalFormProps) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const showModal = () => {
        setIsModalOpen(true);
    };

    const handleOk = () => {
        setIsModalOpen(false);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };

    return (
        <>
            <Button type='primary' onClick={showModal}>
                {OpenModalButtonText}
            </Button>
            <Modal
                title={title}
                closable={{ 'aria-label': 'Close-Button' }}
                open={isModalOpen}
                onCancel={handleCancel}
                footer={null}
            >
                <ProposalForm initialValues={{}} onSuccess={handleOk} />
            </Modal>
        </>
    );
};
