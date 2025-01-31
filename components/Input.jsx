// components/Input.js
export function Input({ value, onChange, placeholder }) {
    return (
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="border border-gray-300 rounded-lg px-3 py-2 w-full"
      />
    );
  }