export enum APISearchTypes {
  AIRCRAFT = 'AIRCRAFT_DOT',
  BUSINESS_DEBTOR = 'BUSINESS_DEBTOR',
  INDIVIDUAL_DEBTOR = 'INDIVIDUAL_DEBTOR',
  MHR_NUMBER = 'MHR_NUMBER',
  REGISTRATION_NUMBER = 'REGISTRATION_NUMBER',
  SERIAL_NUMBER = 'SERIAL_NUMBER'
}
export enum UISearchTypes {
  AIRCRAFT = 'Aircraft Airframe D.O.T. Number',
  BUSINESS_DEBTOR = 'Business Debtor Name',
  INDIVIDUAL_DEBTOR = 'Individual Debtor Name',
  MHR_NUMBER = 'Manufactured Home Registration Number',
  REGISTRATION_NUMBER = 'Registration Number',
  SERIAL_NUMBER = 'Serial Number'
}

export enum APIMHRSearchTypes {
  MHRMHR_NUMBER = 'MHR_NUMBER',
  MHROWNER_NAME = 'OWNER_NAME',
  MHRORGANIZATION_NAME = 'ORGANIZATION_NAME',
  MHRSERIAL_NUMBER = 'SERIAL_NUMBER'
}
export enum APIMHRMapSearchTypes {
  MHRMHR_NUMBER = 'MHR-MHR_NUMBER',
  MHROWNER_NAME = 'MHR-OWNER_NAME',
  MHRORGANIZATION_NAME = 'MHR-ORGANIZATION_NAME',
  MHRSERIAL_NUMBER = 'MHR-SERIAL_NUMBER'
}
export enum UIMHRSearchTypes {
  MHRMHR_NUMBER = 'Manufactured Home Registration Number',
  MHROWNER_NAME = 'Owner Name',
  MHRORGANIZATION_NAME = 'Organization Name',
  MHRSERIAL_NUMBER = 'Serial Number'
}

export enum UIMHRSearchTypeValues {
  MHRMHR_NUMBER = 'mhrNumber',
  MHROWNER_NAME = 'ownerName',
  MHRORGANIZATION_NAME = 'organizationName',
  MHRSERIAL_NUMBER = 'serialNumber'
}

export const UIMHRSearchTypeMap = {
  [UIMHRSearchTypes.MHRMHR_NUMBER]: UIMHRSearchTypeValues.MHRMHR_NUMBER,
  [UIMHRSearchTypes.MHROWNER_NAME]: UIMHRSearchTypeValues.MHROWNER_NAME,
  [UIMHRSearchTypes.MHRORGANIZATION_NAME]: UIMHRSearchTypeValues.MHRORGANIZATION_NAME,
  [UIMHRSearchTypes.MHRSERIAL_NUMBER]: UIMHRSearchTypeValues.MHRSERIAL_NUMBER
}

// for blank or header options in the drop down
export enum BlankSearchTypes {
  BLANK1 = '1',
  BLANK2 = '2',
  BLANK3 = '3',
  BLANK4 = '4'
}
