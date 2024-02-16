
import { createLocalVue, shallowMount } from '@vue/test-utils'
import DownloadAffidavit from '@/components/auth/staff/review-task/DownloadAffidavit.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('DownloadAffidavit.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 1,
    title: 'Download Affidavit',
    affidavitName: 'test affidavit'
  }

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapperFactory = (propsData) => {
      return shallowMount(DownloadAffidavit, {
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

  it('renders the components properly ', () => {
    expect(wrapper.findComponent(DownloadAffidavit).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
