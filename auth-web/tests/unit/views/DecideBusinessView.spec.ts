import { createLocalVue, mount } from '@vue/test-utils'
import DecideBusinessView from '@/views/auth/home/DecideBusinessView.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('DecideBusinessView.vue', () => {
  let wrapper: any
  const ob = {
    'ENTITY_SELECTOR_URL': 'https://entity-selection-dev.apps.silver.devops.gov.bc.ca/'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = mount(DecideBusinessView, {
      localVue,
      router,
      vuetify
    })

    // wrapper.vm.$data.selectorWizardUrl = ConfigHelper.getEntitySelectorUrl()
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(DecideBusinessView).exists()).toBe(true)
    expect(wrapper.findComponent(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct text and number of bullet points', async () => {
    wrapper.vm.bulletPoints = [
      { text: 'Bullet 1' }, { text: 'Bullet 2' }, { text: 'Bullet 3' }
    ]
    await flushPromises()
    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletListItems[0].textContent).toContain('Bullet 1')
    expect(bulletListItems[1].textContent).toContain('Bullet 2')
    expect(bulletListItems[2].textContent).toContain('Bullet 3')
    expect(bulletListItems.length).toStrictEqual(3)
  })
})
