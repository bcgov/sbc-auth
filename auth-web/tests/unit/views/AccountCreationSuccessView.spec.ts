import '@/composition-api-setup'
import { AccessType, Pages } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import AccountCreationSuccessView from '@/views/auth/create-account/AccountCreationSuccessView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { createTestingPinia } from '@pinia/testing'

Vue.use(Vuetify)
Vue.use(VueRouter)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountCreationSuccessView.vue', () => {
  it('routes set up team directly to team members', async () => {
    const localVue = createLocalVue()
    const router = new VueRouter()
    const push = vi.spyOn(router, 'push').mockImplementation(async () => undefined as any)

    const pinia = createTestingPinia({
      initialState: {
        org: {
          currentOrganization: {
            id: 123,
            accessType: AccessType.REGULAR
          }
        }
      }
    })

    const wrapper = mount(AccountCreationSuccessView, {
      pinia,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })

    wrapper.vm.goTo('setup-team')
    await wrapper.vm.$nextTick()

    expect(push).toHaveBeenCalledWith(`/${Pages.MAIN}/123/settings/team-members`)
  })
})
