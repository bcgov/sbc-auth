import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import ConfigHelper from '@/util/config-helper'

export const RegistryHomeBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries and Online Services',
  href: `${ConfigHelper.getValue('REGISTRY_HOME_URL')}`
}

export const RegistryDashboardBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries Dashboard',
  href: `${ConfigHelper.getValue('REGISTRY_HOME_URL')}dashboard`
}

export const MyBusinessRegistryBreadcrumb: BreadcrumbIF = {
  text: 'My Business Registry',
  to: { name: 'business' },
  href: `${ConfigHelper.getValue('AUTH_WEB_URL')}/business`
}

export const StaffDashboardBreadcrumb: BreadcrumbIF = {
  text: 'Staff Dashboard',
  href: `${ConfigHelper.getValue('AUTH_WEB_URL')}/staff/dashboard/active`
}
