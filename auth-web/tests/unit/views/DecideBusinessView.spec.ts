import { createLocalVue, mount } from '@vue/test-utils'
import DecideBusinessView from '@/views/auth/home/DecideBusinessView.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('DecideBusinessView.vue', () => {
  let wrapper: any
  var ob = {
    'ENTITY_SELECTOR_URL': 'https://entity-selection-dev.apps.silver.devops.gov.bc.ca/'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapper = mount(DecideBusinessView, {
      store,
      localVue,
      router,
      vuetify
    })

    // wrapper.vm.$data.selectorWizardUrl = ConfigHelper.getEntitySelectorUrl()
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(DecideBusinessView).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
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
