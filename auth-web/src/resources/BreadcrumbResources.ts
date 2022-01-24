import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import ConfigHelper from '@/util/config-helper'

export const MarketingHomeBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries and Online Services',
  href: `${ConfigHelper.getValue('BCROS_HOME_URL')}`
}

export const DashboardHomeBreadcrumb: BreadcrumbIF = {
  text: 'BC Registries Dashboard',
  href: `${ConfigHelper.getValue('BCROS_HOME_URL')}dashboard`
}

export const RegistryTableBreadcrumb: BreadcrumbIF = {
  text: 'My Business Registry',
  to: { name: 'business' },
  href: `${ConfigHelper.getValue('AUTH_WEB_URL')}/business`
}

export const StaffDashboardBreadcrumb: BreadcrumbIF = {
  text: 'Staff Dashboard',
  href: `${ConfigHelper.getValue('AUTH_WEB_URL')}/staff/dashboard/active`
}
