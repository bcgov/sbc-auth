export const businesses = [
  // BEN Name Request - Processing
  {
    identifier: 'NR 4045467',
    legalType: 'NR',
    name: 'BEN NAME REQUEST LIMITED - PROCESSING',
    nameRequest: {
      legalType: 'BEN',
      names: [{ 'name': 'BEN NAME REQUEST LIMITED - PROCESSING' }],
      nrNumber: 'NR 4045467',
      state: 'Processing',
      expirationDate: null
    },
    status: 'Processing'
  },
  // BEN Name Request
  {
    identifier: 'NR 4045466',
    legalType: 'NR',
    name: 'BEN NAME REQUEST LIMITED',
    nameRequest: {
      legalType: 'BEN',
      names: [{ 'name': 'BEN NAME REQUEST LIMITED' }],
      nrNumber: 'NR 4045466',
      state: 'APPROVED',
      expirationDate: '2022-11-02T19:42:13+00:00'
    },
    passCodeClaimed: true,
    status: 'APPROVED'
  },
  // BEN Name Request DRAFT with expiration date
  {
    identifier: 'NR 4045467',
    legalType: 'NR',
    created: '2022-11-12T19:36:29+00:00',
    name: 'BEN NAME REQUEST LIMITED',
    nameRequest: {
      legalType: 'BEN',
      names: [{ 'name': 'BEN NAME REQUEST LIMITED' }],
      nrNumber: 'NR 4045467',
      state: 'DRAFT',
      expirationDate: '2022-11-22T19:42:13+00:00'
    },
    passCodeClaimed: true,
    status: 'DRAFT'
  },
  // BEN Incorporation Application (numbered)
  {
    businessIdentifier: 'TIQcIs5qvA',
    corpType: {
      code: 'TMP'
    },
    corpSubType: {
      code: 'BEN'
    }
  },
  // SP Registration
  {
    corpType: {
      code: 'TMP'
    },
    identifier: 'TKmp4A16B1',
    legalType: null,
    nameRequest: {
      entityTypeCd: 'FR',
      expirationDate: '2022-07-20T06:59:00+00:00',
      id: 2264498,
      legalType: 'SP',
      names: [
        {
          name: 'AC SP 2022.MAY.25 15.38 TEST',
          state: 'APPROVED'
        }
      ],
      natureBusinessInfo: 'asdf',
      nrNum: 'NR 2821990',
      requestTypeCd: 'FR',
      state: 'CONSUMED',
      target: 'lear'
    },
    nrNumber: 'NR 2821990'
  },
  // alert icons
  {
    adminFreeze: true,
    goodStanding: false,
    businessIdentifier: 'TIQcIs5sss',
    corpType: {
      code: 'TMP'
    },
    corpSubType: {
      code: 'BEN'
    }
  }
]
