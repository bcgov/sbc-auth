import { createLocalVue, mount } from '@vue/test-utils'
import SearchBusinessNameRequest from '@/components/auth/manage-business/SearchBusinessNameRequest.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('SearchBusinessNameRequest Component', () => {
  let wrapper
  let vuetify

  beforeEach(() => {
    const localVue = createLocalVue()
    vuetify = new Vuetify({})
    wrapper = mount(SearchBusinessNameRequest, {
      localVue,
      vuetify,
      mocks: { $t: msg => msg } // Mocking the translation function
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders radio buttons for Incorporated and Name Request', () => {
    expect(wrapper.find('[value="Incorporated"]').exists()).toBe(true)
    expect(wrapper.find('[value="NameRequest"]').exists()).toBe(true)
  })

  it('renders BusinessLookup component when Incorporated is selected', async () => {
    wrapper.setData({ searchType: 'Incorporated' })
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent({ name: 'BusinessLookup' }).exists()).toBe(true)
  })

  it.todo('renders Name Request search field when NameRequest is selected')
})
