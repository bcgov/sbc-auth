import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'

export const RegistryHomeBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries and Online Services',
  href: `${sessionStorage.getItem('REGISTRY_HOME_URL')}`
}

export const RegistryDashboardBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries Dashboard',
  href: `${sessionStorage.getItem('REGISTRY_HOME_URL')}dashboard`
}

export const MyBusinessRegistryBreadcrumb: BreadcrumbIF = {
  text: 'My Business Registry',
  to: { name: 'business' },
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}/business`
}

export const StaffBusinessRegistryBreadcrumb: BreadcrumbIF = {
  text: 'My Staff Business Registry',
  to: { name: 'business' },
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}/business`
}

export const StaffDashboardBreadcrumb: BreadcrumbIF = {
  text: 'Staff Dashboard',
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}/staff/dashboard/active`
}
