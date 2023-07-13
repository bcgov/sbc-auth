import { AssetsPermissions, AssetsRoles } from '@/util/constants'

export const MhrSubProducts: any = [
  {
    type: AssetsRoles.GENERAL_PUBLIC,
    label: `Search Access Only - ${AssetsRoles.GENERAL_PUBLIC}`,
    productBullets: [
      AssetsPermissions.MHR_SEARCH
    ],
    hasImportantBullet: false
  },
  {
    type: AssetsRoles.LAWYERS_NOTARIES,
    label: `${AssetsRoles.QUALIFIED_SUPPLIER} - ${AssetsRoles.LAWYERS_NOTARIES}`,
    productBullets: [
      AssetsPermissions.MHR_SEARCH, AssetsPermissions.TRANSPORT_PERMITS, AssetsPermissions.TRANSFER_TRANSACTIONS,
      AssetsPermissions.RESIDENTIAL_EXEMPTIONS, AssetsPermissions.APPLICATION_REQUIRED
    ],
    hasImportantBullet: true,
    note: `General Service Providers who are not lawyers or notaries cannot request Qualified Supplier access online 
     and <a href="https://www2.gov.bc.ca/gov/content/housing-tenancy/owning-a-home/manufactured-home-registry" 
     target="_blank">must submit a paper application <span class="mdi mdi-open-in-new"></span></a> to BC Registries.`
  },
  {
    type: AssetsRoles.MANUFACTURER,
    label: `${AssetsRoles.QUALIFIED_SUPPLIER} - ${AssetsRoles.MANUFACTURER}`,
    productBullets: [
      AssetsPermissions.MHR_SEARCH, AssetsPermissions.TRANSPORT_PERMITS, AssetsPermissions.HOME_TRANSFER_TRANSACTIONS,
      AssetsPermissions.REGISTRATIONS, AssetsPermissions.APPLICATION_REQUIRED
    ],
    hasImportantBullet: true
  },
  {
    type: AssetsRoles.DEALERS,
    label: `${AssetsRoles.QUALIFIED_SUPPLIER} - ${AssetsRoles.DEALERS}`,
    productBullets: [
      AssetsPermissions.MHR_SEARCH, AssetsPermissions.TRANSPORT_PERMITS_NO_CERT,
      AssetsPermissions.APPLICATION_REQUIRED
    ],
    hasImportantBullet: true
  }
]
