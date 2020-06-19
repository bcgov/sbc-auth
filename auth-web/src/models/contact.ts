export interface Contact {
    email: string;
    phone: string;
    phoneExtension: string;
    city?: string;
    country?: string;
    street?: string;
    streetAdditional?: string;
    postalCode?: string;
    region?: string;
}

export interface Contacts {
    contacts: Contact[]
}
