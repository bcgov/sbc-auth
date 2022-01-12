import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'

export const HomeBreadCrumb: BreadcrumbIF = {
  text: 'Business Registry Home',
  to: { name: 'home' },
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}`
}

export const DashboardBreadcrumb: BreadcrumbIF = {
  text: 'My Business Registry',
  to: { name: 'business' },
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}/business`
}

export const StaffDashboardBreadcrumb: BreadcrumbIF = {
  text: 'Staff Dashboard',
  to: { name: 'staff-dashboard' },
  href: `${sessionStorage.getItem('AUTH_WEB_URL')}/staff/dashboard/active`
}
