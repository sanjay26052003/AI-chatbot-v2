import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

const Sidebar = ({ users, selectedUser, onSelectUser, onlineUsers }) => {
  const { user, logout } = useAuth();
  const [search, setSearch] = useState('');

  const filteredUsers = users.filter((u) =>
    u.username.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-800">Chat App</h1>
          <button
            onClick={logout}
            className="text-gray-500 hover:text-red-500 transition"
            title="Logout"
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
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
          </button>
        </div>

        {/* User info */}
        <div className="flex items-center mb-4">
          <div className="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center text-white font-semibold">
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <div className="ml-3">
            <p className="font-medium text-gray-800">{user?.username}</p>
            <p className="text-sm text-gray-500">Online</p>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users..."
            className="w-full px-4 py-2 pl-10 bg-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
          />
          <svg
            className="w-5 h-5 text-gray-400 absolute left-3 top-2.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* User list */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          <p className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
            Conversations
          </p>
          {filteredUsers.map((u) => (
            <button
              key={u.id}
              onClick={() => onSelectUser(u)}
              className={`w-full flex items-center px-3 py-3 rounded-lg transition ${
                selectedUser?.id === u.id
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
            >
              <div className="relative">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    u.id === 'AI'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                      : 'bg-indigo-100 text-indigo-600'
                  }`}
                >
                  {u.id === 'AI' ? (
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
                      {u.username[0].toUpperCase()}
                    </span>
                  )}
                </div>
                {onlineUsers.has(u.id) && (
                  <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></span>
                )}
              </div>
              <div className="ml-3 text-left flex-1">
                <p className="font-medium truncate">{u.username}</p>
                <p className="text-sm text-gray-500">
                  {u.id === 'AI' ? 'AI Assistant' : 'Click to chat'}
                </p>
              </div>
            </button>
          ))}
          {filteredUsers.length === 0 && (
            <p className="text-center text-gray-500 py-4">No users found</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
