import { apiClient } from './client';
import { TokenResponse, User } from '../types/auth';

export const authApi = {
  googleLogin: async (googleToken: string) => {
    const { data } = await apiClient.post<TokenResponse>('/auth/google', { google_token: googleToken });
    return data;
  },

  refreshToken: async (refreshToken: string) => {
    const { data } = await apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken });
    return data;
  },

  getMe: async () => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },

  logout: async () => {
    await apiClient.post('/auth/logout');
  },
};
