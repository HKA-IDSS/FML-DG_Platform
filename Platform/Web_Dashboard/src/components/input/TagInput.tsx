import { PlusOutlined } from '@ant-design/icons';
import { Input, Tag } from 'antd';
import { TweenOneGroup } from 'rc-tween-one';
import React, { useEffect, useRef, useState } from 'react';

interface TagInputProps {
    initialValue?: string[];
    readonly?: boolean;
    valueChange: (tags: string[]) => void;
    textNew?: string;
    textNone?: string;
}

export const TagInput: React.FC<TagInputProps> = ({
    initialValue = [],
    readonly = false,
    valueChange,
    textNew = 'Add Tag',
    textNone = 'No tags selected',
}) => {
    const [tags, setTags] = useState<string[]>(initialValue);
    const [inputVisible, setInputVisible] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const inputRef = useRef<React.ComponentRef<typeof Input>>(null);

    useEffect(() => {
        if (inputVisible) inputRef.current?.focus();
    }, [inputVisible]);

    useEffect(() => {
        setTags(initialValue);
    }, [initialValue]);

    const handleClose = (removedTag: string) => {
        const newTags = tags.filter((tag) => tag !== removedTag);
        setTags(newTags);
        valueChange(newTags);
    };

    const showInput = () => setInputVisible(true);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
    };

    const handleInputConfirm = () => {
        if (inputValue && tags.indexOf(inputValue) === -1) {
            const newTags = [...tags, inputValue];
            setTags(newTags);
            valueChange(newTags);
        }
        setInputVisible(false);
        setInputValue('');
    };

    const tagChild =
        tags.length > 0 ? (
            tags.map((tag) => (
                <span key={tag} style={{ display: 'inline-block' }}>
                    <Tag
                        closable={!readonly}
                        onClose={(e) => {
                            e.preventDefault();
                            handleClose(tag);
                        }}
                    >
                        {tag}
                    </Tag>
                </span>
            ))
        ) : (
            <span key={'none'} style={{ display: 'inline-block' }}>
                {textNone}
            </span>
        );

    return (
        <>
            <TweenOneGroup
                enter={{ scale: 0.8, opacity: 0, type: 'from', duration: 100 }}
                onEnd={(e) => {
                    if (e.type === 'appear' || e.type === 'enter') {
                        (e.target as HTMLElement).style.display = 'inline-block';
                    }
                }}
                leave={{ opacity: 0, width: 0, scale: 0, duration: 200 }}
                appear={false}
                className='flex flex-wrap gap-y-2'
            >
                {tagChild}
            </TweenOneGroup>
            {!readonly && (
                <div className='mt-2'>
                    {inputVisible ? (
                        <Input
                            ref={inputRef}
                            type='text'
                            className='w-full'
                            value={inputValue}
                            onChange={handleInputChange}
                            onBlur={handleInputConfirm}
                            onPressEnter={handleInputConfirm}
                        />
                    ) : (
                        <Tag onClick={showInput} className='site-tag-plus w-full !py-1 !border-dashed text-center'>
                            <PlusOutlined /> {textNew}
                        </Tag>
                    )}
                </div>
            )}
        </>
    );
};
