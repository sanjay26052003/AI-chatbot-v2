import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

const ChatBox = ({ messages, currentUser, typingUsers, selectedUser }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const isOtherUserTyping =
    selectedUser?.id !== 'AI' &&
    typingUsers[selectedUser?.id];

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-4">
      {/* Chat header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 mb-4 rounded-t-lg">
        <div className="flex items-center">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center ${
              selectedUser?.id === 'AI'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                : 'bg-indigo-100 text-indigo-600'
            }`}
          >
            {selectedUser?.id === 'AI' ? (
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            ) : (
              <span className="font-semibold">
                {selectedUser?.username?.[0]?.toUpperCase()}
              </span>
            )}
          </div>
          <div className="ml-3">
            <h2 className="font-semibold text-gray-800">
              {selectedUser?.username}
            </h2>
            <p className="text-sm text-gray-500">
              {selectedUser?.id === 'AI' ? 'AI Assistant' : 'Online'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No messages yet. Start the conversation!</p>
            {selectedUser?.id === 'AI' && (
              <p className="text-sm mt-2">
                Try asking: "Hello, what can you help me with?"
              </p>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isOwn={message.sender_id === currentUser.id}
            />
          ))
        )}

        {isOtherUserTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatBox;
