export interface Contact {
    firstName?: string,
    lastName?: string,
    email: string;
    phone: string;
    phoneExtension: string;
}

export interface Contacts {
    contacts: Contact[]
}
