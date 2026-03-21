import { useState, useRef } from 'react';

const InputBox = ({ onSendMessage, onTyping }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
      onTyping(false);
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
    onTyping(e.target.value);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border-t border-gray-200 p-4"
    >
      <div className="flex items-center space-x-4">
        <input
          ref={inputRef}
          type="text"
          value={message}
          onChange={handleChange}
          placeholder="Type a message..."
          className="flex-1 px-4 py-3 bg-gray-100 rounded-full focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
          autoFocus
        />
        <button
          type="submit"
          disabled={!message.trim()}
          className="bg-indigo-500 text-white p-3 rounded-full hover:bg-indigo-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>
      <p className="text-xs text-gray-400 mt-2 text-center">
        Tip: Send a message to "AI Bot" or start with <code className="bg-gray-100 px-1 rounded">/ai</code> to chat with AI
      </p>
    </form>
  );
};

export default InputBox;
