import { ChangeEvent } from "react";

interface NumberInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  step?: number;
  min?: number;
}

export default function NumberInput({
  id,
  value,
  onChange,
  label,
  placeholder,
  step = 0.1,
  min = 0,
}: NumberInputProps) {
  const handleIncrement = () => {
    const num = parseFloat(value || "0");
    onChange((num + step).toFixed(1));
  };

  const handleDecrement = () => {
    const num = parseFloat(value || "0");
    onChange(Math.max(min, num - step).toFixed(1));
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="field">
      {label && <label className="label" htmlFor={id}>{label}</label>}
      <div className="number-input-wrap">
        <button 
          type="button" 
          onClick={handleDecrement}
          className="number-input-btn mr-1"
          aria-label="Decrease"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        
        <input
          id={id}
          type="number"
          step={step}
          min={min}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className="number-input-field text-center"
        />

        <button 
          type="button" 
          onClick={handleIncrement}
          className="number-input-btn ml-1"
          aria-label="Increase"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>
  );
}
