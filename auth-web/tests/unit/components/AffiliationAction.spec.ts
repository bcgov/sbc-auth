import '../test-utils/composition-api-setup' // important to import this first

vi.mock('../../../src/services/user.services')

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

describe('AffiliationAction.vue', () => {
  // TODO: Fill in - Move content from AffiliatedEntityTable.
})
