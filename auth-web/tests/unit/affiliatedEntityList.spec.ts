import VuexPersistence from 'vuex-persist'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import Vue from 'vue'
import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import UserService from '../../src/services/user.services'
import UserModule from '@/store/modules/user'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('../../src/services/user.services')

describe('AffiliatedEntityList.vue', () => {
  let localVue
  let store

  const config = {
    VUE_APP_ROOT_API: 'https://localhost:8080/api/v1/11',
    VUE_APP_COPS_REDIRECT_URL: 'https://coops-dev.pathfinder.gov.bc.ca/',
    VUE_APP_PAY_ROOT_API: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)

    const vuexPersist = new VuexPersistence({
      key: 'AUTH_WEB',
      storage: sessionStorage
    })

    store = new Vuex.Store({
      strict: false,
      modules: {
        user: UserModule
      },
      plugins: [vuexPersist.plugin]
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Shows empty panel message if no affiliated entities', () => {
    UserService.getOrganizations = jest.fn().mockResolvedValue({ orgs: [] })
    const $t = () => 'You have no businesses to manage'
    const wrapper = shallowMount(AffiliatedEntityList, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.text()).toContain('You have no businesses to manage')
  })

  it('Renders affiliated entity list', () => {
    UserService.getOrganizations = jest.fn().mockResolvedValue({
      data: {
        orgs: [
          {
            affiliatedEntities: [
              {
                businessIdentifier: 'CP0001245',
                businessNumber: '791861073BC0001',
                created: '2019-08-26T11:50:32.620965+00:00',
                created_by: 'BCREGTEST Jeong SIX',
                id: 11,
                modified: '2019-08-26T11:50:32.620989+00:00',
                name: 'Foobar, Inc.'
              }
            ],
            id: 27,
            name: 'Test Org'
          }
        ]
      }
    })
    const $t = () => ''
    const wrapper = shallowMount(AffiliatedEntityList, {
      store,
      localVue,
      mocks: { $t }
    })
    setTimeout(() => {
      const item = wrapper.vm.$el.querySelectorAll('.list-item')[0]
      expect(item.querySelector('.list-item_business-number').textContent).toEqual('791861073BC0001')
      expect(item.querySelector('.list-item_incorp-number').textContent).toEqual('CP0001245')
    }, 1000)
  })
})
