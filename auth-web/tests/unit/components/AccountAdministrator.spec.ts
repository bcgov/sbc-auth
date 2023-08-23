
import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountAdministrator from '@/components/auth/staff/review-task/AccountAdministrator.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountAdministrator.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 1,
    title: 'Account Admin',
    accountUnderReviewAdmin: {
      firstname: 'test',
      lastname: 'test',
      username: 'username',
      email: 'test@tets.com',
      phone: '12345689'
    },
    accountUnderReviewAdminContact: {
      email: 'test@tets.com',
      phone: '12345689'
    }

  }

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapperFactory = (propsData) => {
      return shallowMount(AccountAdministrator, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory(props)
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.findComponent(AccountAdministrator).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
