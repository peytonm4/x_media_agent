// components/Button.js
export function Button({ children, onClick, disabled }) {
    return (
      <button
        onClick={onClick}
        disabled={disabled}
        className={`px-4 py-2 rounded-lg text-white font-semibold transition ${
          disabled ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {children}
      </button>
    );
  }