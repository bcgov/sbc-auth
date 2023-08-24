import NameRequestLookupServices from '@/services/name-request-lookup.services'
import { axios } from '@/util/http-util'
import sinon from 'sinon'

describe('Name Request Lookup Services', () => {
  it('returns a result when the name request is found', async () => {
    const result = {
      // TODO - remove comments when BE ready with status
      // 'names': [
      //   { 'name': 'TEST NAME 1 CORP.', 'status': 'Accepted' },
      //   { 'name': 'TEST NAME 2 INC.', 'status': 'Rejected' },
      //   { 'name': 'TEST NAME 3 LIMITED', 'status': 'Not Examined' }
      // ],
      'names': [
        'TEST NAME 1 CORP.',
        'TEST NAME 2 INC.',
        'TEST NAME 3 LIMITED'
      ],
      'nrNum': 'NR 1752813'
    }

    const url = NameRequestLookupServices.namexApiUrl + 'requests/search' +
      `?query=${encodeURIComponent('NR 1752813')}` + '&start=0&rows=20'

    sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: [result] })
    )

    // search and look at results
    const results = await NameRequestLookupServices.search('NR 1752813')
    expect(results.length).toBe(1)
    expect(results[0]).toEqual(result)
    sinon.restore()
  })
  it('does not return a result when the name request is not found', async () => {
  // mock unsuccesssful search
    const url = NameRequestLookupServices.namexApiUrl + 'requests/search' +
    `?query=${encodeURIComponent('NR 1752814')}` + '&start=0&rows=20'

    sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: [] })
    )

    const results = await NameRequestLookupServices.search('NR 1752814')
    expect(results.length).toBe(0)
  })
})
