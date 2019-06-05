import PasscodeForm from '@/components/auth/PasscodeForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import LoginServices from '../../src/services/login.services'
import axios from 'axios'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { access_token: 'abcd' } }))
}))


describe('PasscodeForm.vue', () => {
  let cmp

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      modules: {
        login: {
          state: {
            entityNumber: '',
            passcode: ''
          },
          getters: {
            entityNumber: (state) => state.login.entityNumber,
            passcode: (state) => state.login.passcode
          },
          mutations: {
            entityNumber (state, entityNumber) {
              state.login.entityNumber = entityNumber
            },

            passcode (state, passcode) {
              state.login.passcode = passcode
            }
          }
        }
      }
    })
    const $t = () => {}
    cmp = mount(PasscodeForm, {
      store,
      localVue,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('passcode screen login button exists', () => {
    expect(cmp.find('.sign-in-btn').text().startsWith('Sign In')).toBeTruthy()
    expect(cmp.isVueInstance()).toBeTruthy()
  })

  it('passcode and entity number is empty', () => {
    expect(cmp.vm.entityNumber).toBe('')
    expect(cmp.vm.passcode).toBe('')
  })

  it('passcode and entity number is the values in store', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      modules: {
        login: {
          state: {
            entityNumber: 'somenumber',
            passcode: 'somevalue'
          }
        }
      } })
    const $t = () => {}
    cmp = mount(PasscodeForm, {
      store,
      localVue,
      mocks: { $t }
    })

    cmp.vm.$refs.form.validate()

    expect(cmp.vm.entityNumber).toBe('somenumber')
    expect(cmp.vm.passcode).toBe('somevalue')
  })
  it('login button click invokes login method', () => {
    const stub = jest.fn()
    cmp.setMethods({ login: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.login).toBeCalled()
  })

  it('login button click invokes isValidForm method', () => {
    const stub = jest.fn()
    cmp.setMethods({ isValidForm: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.isValidForm).toBeCalled()
  })

  it('login button valid form  call  axios', () => {

    const stub = jest.fn()
    stub.mockReturnValueOnce(true)
    cmp.setMethods({ isValidForm: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.isValidForm).toBeTruthy()
    expect(axios.post).toBeCalledTimes(1)
  })

  it('login button invalid form  never call  axios', () => {
    const stub = jest.fn()
    stub.mockReturnValueOnce(false)
    cmp.setMethods({ isValidForm: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.isValidForm).toBeTruthy()
  })
})
