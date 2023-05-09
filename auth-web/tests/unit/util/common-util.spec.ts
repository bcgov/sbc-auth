import CommonUtil from '@/util/common-util'
import { Permission } from '@/util/constants'

const dateStr = new Date('2020-10-22 00:00:00 PDT')

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

  const { pathname } = window.location

  beforeEach(async () => {
    // mock the window.location.pathname function
    delete window.location
    window.location = { pathname: jest.fn() } as any
  })

  it('is isUrl [positive]', () => {
    expect(CommonUtil.isUrl('http://localhost:8000')).toBe(true)
    expect(CommonUtil.isUrl('https://localhost:8000')).toBe(true)
  })

  it('is isUrl [negative]', () => {
    expect(CommonUtil.isUrl('abcd')).toBe(false)
    expect(CommonUtil.isUrl('localhost:8080')).toBe(false)
    expect(CommonUtil.isUrl('/confirmtoken/xxxxx.Y-qrVg.jqfdfdfdfd')).toBe(false)
  })

  it('formatIncorporationNumber returns null', () => {
    expect(CommonUtil.formatIncorporationNumber(null)).toBeNull()
    expect(CommonUtil.formatIncorporationNumber('')).toBeNull()
  })

  it('formatIncorporationNumber returns correct incorporation number', () => {
    expect(CommonUtil.formatIncorporationNumber('CP33')).toBe('CP0000033')
    expect(CommonUtil.formatIncorporationNumber('CP1234567')).toBe('CP1234567')
  })

  it('validateIncorporationNumber returns True with valid incorp number', () => {
    expect(CommonUtil.validateIncorporationNumber('BC0000033')).toBe(true)
  })

  it('validateIncorporationNumber returns False with invalid incorp number', () => {
    expect(CommonUtil.validateIncorporationNumber(null)).toBe(false)
    expect(CommonUtil.validateIncorporationNumber('XX000033')).toBe(false)
  })

  it('isCooperativeNumber returns True with valid coop number', () => {
    expect(CommonUtil.isCooperativeNumber('CP000033')).toBe(true)
  })

  it('isCooperativeNumber returns False with invalid coop number', () => {
    expect(CommonUtil.isCooperativeNumber(null)).toBe(false)
    expect(CommonUtil.isCooperativeNumber('')).toBe(false)
    expect(CommonUtil.isCooperativeNumber('XX000033')).toBe(false)
  })

  it('is validating email format [positive]', () => {
    expect(CommonUtil.validateEmailFormat('peterparker07@spider-man.com')).toBe(true)
    expect(CommonUtil.validateEmailFormat('peterparker07+1@spider-man.com')).toBe(true)
  })

  it('is validating email format [negative]', () => {
    expect(CommonUtil.validateEmailFormat('peterparker07$spider-man.com')).toBe(false)
  })

  it('validatePhoneNumber returns True with valid phone number', () => {
    expect(CommonUtil.validatePhoneNumber('123-123-1234')).toBe(true)
  })

  it('validatePhoneNumber returns False with invalid phone number', () => {
    expect(CommonUtil.validatePhoneNumber('123-123-12345')).toBe(false)
  })

  it('validateCooperativePasscode returns True with valid passcode', () => {
    expect(CommonUtil.validateCooperativePasscode('123456789')).toBe(true)
  })

  it('validateCooperativePasscode returns False with invalid passcode', () => {
    expect(CommonUtil.validateCooperativePasscode(null)).toBe(false)
    expect(CommonUtil.validateCooperativePasscode('')).toBe(false)
    expect(CommonUtil.validateCooperativePasscode('12345678')).toBe(false)
    expect(CommonUtil.validateCooperativePasscode('1234567890')).toBe(false)
    expect(CommonUtil.validateCooperativePasscode('abcdefghi')).toBe(false)
  })

  it('validateCorporatePassword returns True with valid password', () => {
    expect(CommonUtil.validateCorporatePassword('AAAAAAAA')).toBe(true)
    expect(CommonUtil.validateCorporatePassword('ZZZZZZZZZZZZZZZ')).toBe(true)
    expect(CommonUtil.validateCorporatePassword('12345678')).toBe(true)
    expect(CommonUtil.validateCorporatePassword('123456789012345')).toBe(true)
  })

  it('validateCorporatePassword returns False with invalid password', () => {
    expect(CommonUtil.validateCorporatePassword(null)).toBe(false)
    expect(CommonUtil.validateCorporatePassword('')).toBe(false)
    expect(CommonUtil.validateCorporatePassword('1234567')).toBe(false)
    expect(CommonUtil.validateCorporatePassword('1234567890123456')).toBe(false)
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
    expect(CommonUtil.formatDisplayDate(dateStr)).toBe('2020-10-22')
    expect(CommonUtil.formatDisplayDate(dateStr, 'DD/MM/YYYY')).toBe('22/10/2020')
    expect(CommonUtil.formatDisplayDate(null)).toBe('')
  })

  it('is format datepicker date correctly', () => {
    expect(CommonUtil.formatDatePickerDate(dateStr)).toBe('2020-10-22')
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
    window.location.pathname = 'http://localhost:8000/business/auth/signin'
    expect(CommonUtil.isSigningIn()).toBe(true)
  })

  it('is path is signOut', () => {
    window.location.pathname = 'http://localhost:8000/business/auth/signout'
    expect(CommonUtil.isSigningOut()).toBe(true)
  })

  it('is doing custom sort correctly', () => {
    expect(CommonUtil.customSort(items, ['name'], [false])).toMatchObject(sorted)
  })

  it('is doing custom sort dec correctly', () => {
    expect(CommonUtil.customSort(items, ['name'], [true])).toMatchObject(sortedDec)
  })

  it('formats number to two places correctly', () => {
    expect(CommonUtil.formatNumberToTwoPlaces(2)).toBe('02')
    expect(CommonUtil.formatNumberToTwoPlaces(10)).toBe('10')
  })

  it('trims trailing slash URL correctly', () => {
    expect(CommonUtil.trimTrailingSlashURL(null)).toBe('')
    expect(CommonUtil.trimTrailingSlashURL('abc/')).toBe('abc')
  })

  afterEach(() => {
    window.location.pathname = pathname
  })
})
