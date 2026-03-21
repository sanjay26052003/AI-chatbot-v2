import { format } from 'date-fns';

const MessageBubble = ({ message, isOwn }) => {
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return format(date, 'HH:mm');
    } catch {
      return '';
    }
  };

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg rounded-2xl px-4 py-2 ${
          isOwn
            ? 'bg-indigo-500 text-white rounded-br-sm'
            : message.is_ai
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-bl-sm'
            : 'bg-white text-gray-800 rounded-bl-sm border border-gray-200'
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        <p
          className={`text-xs mt-1 ${
            isOwn || message.is_ai ? 'text-white/70' : 'text-gray-400'
          }`}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
};

export default MessageBubble;
