import { User } from '../types/auth';

export class RoleResolver {
  static isSuperAdmin(user: User | null): boolean {
    if (!user) return false;
    return user.roles.some((r) => r.name === 'SUPER_ADMIN');
  }

  static isTempleAdmin(user: User | null): boolean {
    if (!user) return false;
    return user.roles.some((r) => r.name === 'SUPER_ADMIN' || r.name === 'TEMPLE_ADMIN');
  }

  static isVolunteer(user: User | null): boolean {
    if (!user) return false;
    return user.roles.some((r) => r.name === 'VOLUNTEER');
  }

  static getPrimaryRoleName(user: User | null): string {
    if (!user || user.roles.length === 0) return 'GUEST';
    return user.roles[0].name;
  }
}
