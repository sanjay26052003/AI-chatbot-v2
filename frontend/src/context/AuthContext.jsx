import { createContext, useContext, useState, useEffect } from 'react';
import { initializeSocket, disconnectSocket } from '../services/socket';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
      const socketInstance = initializeSocket(token);
      setSocket(socketInstance);
    }

    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token } = response.data;

      localStorage.setItem('token', access_token);

      // Get user data
      const userResponse = await api.get('/auth/me');
      const userData = {
        id: userResponse.data.id,
        username: userResponse.data.username,
        email: userResponse.data.email,
      };

      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      // Initialize socket
      const socketInstance = initializeSocket(access_token);
      setSocket(socketInstance);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const signup = async (username, email, password) => {
    try {
      await api.post('/auth/register', { username, email, password });
      // After registration, login
      return await login(email, password);
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const logout = () => {
    disconnectSocket();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setSocket(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        socket,
        login,
        signup,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
