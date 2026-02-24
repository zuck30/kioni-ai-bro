import React, { useRef, useEffect } from 'react';

interface InputAreaProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  placeholder?: string;
}

const InputArea: React.FC<InputAreaProps> = ({ value, onChange, onSend, placeholder }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="flex-1">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="w-full bg-transparent border-none text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-0 resize-none py-3 px-2 text-sm font-medium scrollbar-hide"
        style={{ maxHeight: '150px' }}
      />
    </div>
  );
};

export default InputArea;
