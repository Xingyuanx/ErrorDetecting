export const Roles = {
  admin: 'admin',
  operator: 'operator',
  observer: 'observer'
} as const

export type Role = typeof Roles[keyof typeof Roles]

export const AllRoles: Role[] = [Roles.admin, Roles.operator, Roles.observer]

export const RoleLabel: Record<Role, string> = {
  admin: '管理员',
  operator: '操作员',
  observer: '观察员'
}
