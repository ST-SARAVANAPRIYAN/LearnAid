import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'faculty' | 'student';
  is_active: boolean;
}

export interface Faculty {
  id: number;
  employee_id: string;
  designation: string;
  qualification: string;
  specialization: string;
  experience_years: number;
  office_location?: string;
  office_hours?: string;
}

interface AuthContextType {
  user: User | null;
  faculty: Faculty | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [faculty, setFaculty] = useState<Faculty | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          // Validate token and get user info
          const response = await authService.getCurrentUser();
          setUser(response.data);
          
          // If user is faculty, get faculty details
          if (response.data.role === 'faculty') {
            const facultyResponse = await authService.getFacultyProfile();
            setFaculty(facultyResponse.data);
          }
          
          setToken(storedToken);
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          setFaculty(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      
      // If user is faculty, get faculty details
      if (userData.role === 'faculty') {
        const facultyResponse = await authService.getFacultyProfile();
        setFaculty(facultyResponse.data);
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setFaculty(null);
  };

  const value = {
    user,
    faculty,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
