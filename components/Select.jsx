// components/Select.js
export function Select({ onValueChange, children }) {
    return (
      <select
        onChange={(e) => onValueChange(e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 w-full"
      >
        {children}
      </select>
    );
  }
  
  export function SelectTrigger({ children }) {
    return <>{children}</>;
  }
  
  export function SelectValue({ placeholder }) {
    return <option value="">{placeholder}</option>;
  }
  
  export function SelectContent({ children }) {
    return <>{children}</>;
  }
  
  export function SelectItem({ value, children }) {
    return <option value={value}>{children}</option>;
  }
  