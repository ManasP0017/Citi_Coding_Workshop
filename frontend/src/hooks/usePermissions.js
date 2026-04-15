import { useAuth } from '../contexts/AuthContext';

/**
 * Returns RBAC flags derived from the authenticated user's role.
 *
 * canWrite  — Admin, Manager, Contributor (create / update)
 * canDelete — Admin, Manager only
 * isAdmin   — Admin only
 */
export default function usePermissions() {
  const { user } = useAuth();
  const role = user?.role ?? 'viewer';
  return {
    role,
    canWrite:  ['admin', 'manager', 'contributor'].includes(role),
    canDelete: ['admin', 'manager'].includes(role),
    isAdmin:   role === 'admin',
  };
}
