import { User } from '../types/auth';

export class PermissionResolver {
  static hasPermission(user: User | null, permissionCode: string): boolean {
    if (!user) return false;
    
    // Super Admins bypass permission checks
    const roleNames = user.roles.map((r) => r.name);
    if (roleNames.includes('SUPER_ADMIN')) return true;

    const userPermissions = user.roles.flatMap((r) => r.permissions.map((p) => p.code));
    return userPermissions.includes(permissionCode);
  }

  static hasAnyPermission(user: User | null, permissionCodes: string[]): boolean {
    if (!user) return false;
    return permissionCodes.some((code) => this.hasPermission(user, code));
  }

  static hasAllPermissions(user: User | null, permissionCodes: string[]): boolean {
    if (!user) return false;
    return permissionCodes.every((code) => this.hasPermission(user, code));
  }
}
