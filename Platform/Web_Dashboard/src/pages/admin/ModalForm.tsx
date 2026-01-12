import React from 'react';
import { Modal } from 'antd';

interface ModalFormProps {
    open: boolean;
    title: string;
    onCancel: () => void;
    children: React.ReactNode;
}

export const ModalForm: React.FC<ModalFormProps> = ({ open, title, onCancel, children }) => (
    <Modal open={open} title={title} onCancel={onCancel} footer={null} destroyOnClose>
        {children}
    </Modal>
);
