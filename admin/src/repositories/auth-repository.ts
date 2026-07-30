import { AuthApi } from '../services/api/auth-api';
import { TokenStorage } from '../utils/token-storage';
import { User } from '../types/auth';

export class AuthRepository {
  static async login(credentials: { username: string; password: string }): Promise<{ user: User; token: string }> {
    const data = await AuthApi.login(credentials);
    TokenStorage.setTokens(data.access_token, data.refresh_token);
    
    // Fetch user profile upon login
    const user = await AuthApi.getMe();
    TokenStorage.setUserData(user);

    return { user, token: data.access_token };
  }

  static async logout(): Promise<void> {
    try {
      await AuthApi.logout();
    } catch {
      // Ignore remote logout failure, clear local session anyway
    } finally {
      TokenStorage.clear();
    }
  }

  static async getCurrentUser(): Promise<User | null> {
    const localUser = TokenStorage.getUserData();
    if (localUser) return localUser;
    
    try {
      const user = await AuthApi.getMe();
      TokenStorage.setUserData(user);
      return user;
    } catch {
      return null;
    }
  }
}
