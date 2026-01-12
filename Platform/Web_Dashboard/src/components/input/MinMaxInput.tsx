import React from 'react';
import { InputNumber, Space } from 'antd';

// Define the props our component will accept.
// Ant Design's Form.Item will inject `value` and `onChange`.
type MinMaxInputProps = {
    value?: [number?, number?];
    onChange?: (value: [number?, number?]) => void;
};

const MinMaxInput: React.FC<MinMaxInputProps> = ({ value = [], onChange }) => {
    // Safely destructure the value array
    const [min, max] = value || [];

    const handleMinChange = (newMin: number | null) => {
        // When min changes, call the parent's onChange with the new array
        onChange?.([newMin ?? undefined, max]);
    };

    const handleMaxChange = (newMax: number | null) => {
        // When max changes, call the parent's onChange with the new array
        onChange?.([min, newMax ?? undefined]);
    };

    return (
        <Space>
            <InputNumber placeholder='Min' value={min} onChange={handleMinChange} />
            <InputNumber placeholder='Max' value={max} onChange={handleMaxChange} />
        </Space>
    );
};

export default MinMaxInput;
