import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { useUserStore } from '@/stores'
import { Role } from '@/util/constants'
import InvoluntaryDissolution from '@/views/auth/staff/InvoluntaryDissolution.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

describe('StaffDashboardView tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()

    const userStore = useUserStore()
    userStore.currentUser = {
      roles: [Role.Staff]
    } as any

    wrapper = mount(InvoluntaryDissolution, {
      localVue,
      vuetify
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders view with child components', async () => {
    expect(wrapper.findComponent(InvoluntaryDissolution).exists()).toBe(true)
    expect(wrapper.find('.view-header__title').text()).toBe('Staff Involuntary Dissolution Batch')
  })
})
