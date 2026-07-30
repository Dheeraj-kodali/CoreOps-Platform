import { UserApi } from '../services/api/user-api';
import { User, Role, Permission } from '../types/user';

export class UserRepository {
  static async getUsers(params?: Record<string, any>): Promise<User[]> {
    const data = await UserApi.list(params);
    return data.items || data;
  }

  static async getUserById(id: string): Promise<User> {
    return await UserApi.getById(id);
  }

  static async createUser(payload: Partial<User>): Promise<User> {
    return await UserApi.create(payload);
  }

  static async updateUser(id: string, payload: Partial<User>): Promise<User> {
    return await UserApi.update(id, payload);
  }

  static async getRoles(): Promise<Role[]> {
    return await UserApi.getRoles();
  }

  static async getPermissions(): Promise<Permission[]> {
    return await UserApi.getPermissions();
  }
}
