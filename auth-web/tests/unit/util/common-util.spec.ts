import CommonUtil from '@/util/common-util'
import { Permission } from '@/util/constants'

const setPathName = (url) => {
  global.window = Object.create(window)
  Object.defineProperty(window, 'location', {
    value: {
      pathname: url
    }
  })
}

describe('Common Util Test', () => {
  const addressComp = {
    city: 'Victoria',
    country: 'Canada',
    street: '4000 Seymour',
    postalCode: 'V8X W14',
    region: 'BC'
  }
  const addressAuth = {
    addressCity: 'Victoria',
    addressCountry: 'Canada',
    streetAddress: '4000 Seymour',
    postalCode: 'V8X W14',
    addressRegion: 'BC'
  }

  const items = [
    { id: 1, name: 'Bruce Wayne', alterEgo: 'Batman' },
    { id: 2, name: 'Peter Parker', alterEgo: 'Spider-Man' },
    { id: 3, name: 'Barry Allen', alterEgo: 'Flash' }
  ]
  const sortedDec = [
    { id: 3, name: 'Barry Allen', alterEgo: 'Flash' },
    { id: 1, name: 'Bruce Wayne', alterEgo: 'Batman' },
    { id: 2, name: 'Peter Parker', alterEgo: 'Spider-Man' }
  ]
  const sorted = [
    { id: 2, name: 'Peter Parker', alterEgo: 'Spider-Man' },
    { id: 1, name: 'Bruce Wayne', alterEgo: 'Batman' },
    { id: 3, name: 'Barry Allen', alterEgo: 'Flash' }
  ]

  it('is isUrl [positive]', () => {
    expect(CommonUtil.isUrl('http://localhost:8000')).toBe(true)
    expect(CommonUtil.isUrl('https://localhost:8000')).toBe(true)
  })

  it('is isUrl [negative]', () => {
    expect(CommonUtil.isUrl('abcd')).toBe(false)
    expect(CommonUtil.isUrl('localhost:8080')).toBe(false)
  })

  it('is formatIncorporationNumber returns correct CP Number', () => {
    expect(CommonUtil.formatIncorporationNumber('CP33')).toBe('CP0000033')
  })

  it('is formatIncorporationNumber returns correct NR Number', () => {
    expect(CommonUtil.formatIncorporationNumber('NR77', true)).toBe('NR 0000077')
  })

  it('is validating IncorporationNumber [positive]', () => {
    expect(CommonUtil.validateIncorporationNumber('CP0000033')).toBe(true)
  })

  it('is validating IncorporationNumber [negative]', () => {
    expect(CommonUtil.validateIncorporationNumber('XX000033')).toBe(false)
  })

  it('is validating NameRequestNumber [positive]', () => {
    expect(CommonUtil.validateNameRequestNumber('NR 0000077')).toBe(true)
  })

  it('is validating NameRequestNumber [negative]', () => {
    expect(CommonUtil.validateNameRequestNumber('CP0000033')).toBe(false)
  })

  it('is validating email format [positive]', () => {
    expect(CommonUtil.validateEmailFormat('peterparker07@spider-man.com')).toBe(true)
    expect(CommonUtil.validateEmailFormat('peterparker07+1@spider-man.com')).toBe(true)
  })

  it('is validating email format [negative]', () => {
    expect(CommonUtil.validateEmailFormat('peterparker07$spider-man.com')).toBe(false)
  })

  it('is validating Password [positive]', () => {
    expect(CommonUtil.validatePasswordRules('ValarMorghulis@99')).toBe(true)
  })

  it('is validating NameRequestNumber [negative]', () => {
    expect(CommonUtil.validatePasswordRules('ValarDohaeris')).toBe(false)
    expect(CommonUtil.validatePasswordRules('ValarDohaeris@')).toBe(false)
    expect(CommonUtil.validatePasswordRules('ValarDohaeris88')).toBe(false)
    expect(CommonUtil.validatePasswordRules('Val@88')).toBe(false)
  })

  it('is format display date correctly', () => {
    expect(CommonUtil.formatDisplayDate(new Date('2020-10-22'))).toBe('10-21-2020')
    expect(CommonUtil.formatDisplayDate(new Date('2020-10-22'), 'DD/MM/YYYY')).toBe('21/10/2020')
    expect(CommonUtil.formatDisplayDate(null)).toBe('')
  })

  it('is format datepicker date correctly', () => {
    expect(CommonUtil.formatDatePickerDate(new Date('2020-10-22'))).toBe('2020-10-21')
  })

  it('is getAdminPermissions correctly', () => {
    expect(CommonUtil.getAdminPermissions().length).toBeGreaterThan(1)
    expect(CommonUtil.getAdminPermissions()).toContain(Permission.INVITE_MEMBERS)
    expect(CommonUtil.getAdminPermissions()).toContain(Permission.RESET_OTP)
  })

  it('is getViewOnlyPermissions correctly', () => {
    expect(CommonUtil.getViewOnlyPermissions().length).toBeGreaterThan(1)
    expect(CommonUtil.getViewOnlyPermissions()).toContain(Permission.VIEW_ACCOUNT)
    expect(CommonUtil.getViewOnlyPermissions()).not.toContain(Permission.TRANSACTION_HISTORY)
  })

  it('is convertAddressForComponent correctly', () => {
    expect(CommonUtil.convertAddressForComponent(addressComp)).toMatchObject(addressAuth)
  })

  it('is convertAddressForAuth correctly', () => {
    expect(CommonUtil.convertAddressForAuth(addressAuth)).toMatchObject(addressComp)
  })

  it('is path is signIn', () => {
    setPathName('business/auth/signin')
    expect(CommonUtil.isSigningIn()).toBe(true)
  })

  it('is path is signOut', () => {
    setPathName('business/auth/signout')
    expect(CommonUtil.isSigningOut()).toBe(false)
  })

  it('is doing custom sort correctly', () => {
    expect(CommonUtil.customSort(items, ['name'], [false])).toMatchObject(sorted)
  })

  it('is doing custom sort dec correctly', () => {
    expect(CommonUtil.customSort(items, ['name'], [true])).toMatchObject(sortedDec)
  })
})
