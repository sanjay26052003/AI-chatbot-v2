import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { getSocket } from '../services/socket';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import ChatBox from '../components/ChatBox';
import InputBox from '../components/InputBox';

const Chat = () => {
  const { user, socket: authSocket } = useAuth();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState({});
  const [onlineUsers, setOnlineUsers] = useState(new Set());
  const socketRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Fetch users
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await api.get('/auth/users');
        setUsers(response.data);

        // Add AI bot to users
        setUsers((prev) => [
          ...prev,
          { id: 'AI', username: 'AI Bot', email: 'ai@chat.app' },
        ]);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
    };

    fetchUsers();
  }, []);

  // Socket connection
  useEffect(() => {
    const socket = getSocket();
    if (!socket) return;

    socketRef.current = socket;

    // Listen for messages
    socket.on('message', (message) => {
      if (
        message.sender_id === selectedUser?.id ||
        message.receiver_id === selectedUser?.id ||
        message.sender_id === user.id ||
        (message.receiver_id === 'AI' && selectedUser?.id === 'AI')
      ) {
        setMessages((prev) => [...prev, message]);
      }
    });

    // Listen for typing
    socket.on('typing', (data) => {
      setTypingUsers((prev) => ({
        ...prev,
        [data.user_id]: data.is_typing,
      }));
    });

    // Listen for status changes
    socket.on('status', (data) => {
      setOnlineUsers((prev) => {
        const newSet = new Set(prev);
        if (data.status === 'online') {
          newSet.add(data.user_id);
        } else {
          newSet.delete(data.user_id);
        }
        return newSet;
      });
    });

    return () => {
      socket.off('message');
      socket.off('typing');
      socket.off('status');
    };
  }, [selectedUser, user]);

  // Fetch messages when user is selected
  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedUser) return;

      try {
        const response = await api.get(`/chat/messages/${selectedUser.id}`);
        setMessages(response.data);
      } catch (error) {
        console.error('Failed to fetch messages:', error);
      }
    };

    fetchMessages();
  }, [selectedUser]);

  const sendMessage = (content) => {
    if (!socketRef.current || !selectedUser) {
      console.log('Cannot send: socket or user not ready', { socket: !!socketRef.current, user: selectedUser });
      return;
    }

    console.log('Sending message:', content, 'to:', selectedUser.id);

    const messageData = {
      type: 'message',
      receiver_id: selectedUser.id,
      content,
    };

    socketRef.current.emit('send_message', messageData);
    console.log('Message emitted');
  };

  const sendTypingIndicator = (isTyping) => {
    if (!socketRef.current || !selectedUser) return;

    socketRef.current.emit('typing', {
      receiver_id: selectedUser.id,
      is_typing: isTyping,
    });
  };

  const handleTyping = (text) => {
    // Send typing indicator with debounce
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    sendTypingIndicator(true);

    typingTimeoutRef.current = setTimeout(() => {
      sendTypingIndicator(false);
    }, 2000);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        users={users}
        selectedUser={selectedUser}
        onSelectUser={setSelectedUser}
        onlineUsers={onlineUsers}
      />

      <div className="flex-1 flex flex-col">
        {selectedUser ? (
          <>
            <ChatBox
              messages={messages}
              currentUser={user}
              typingUsers={typingUsers}
              selectedUser={selectedUser}
            />
            <InputBox onSendMessage={sendMessage} onTyping={handleTyping} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-4 bg-indigo-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-12 h-12 text-indigo-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-700">
                Select a conversation
              </h2>
              <p className="text-gray-500 mt-1">
                Choose a user or AI Bot to start chatting
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
