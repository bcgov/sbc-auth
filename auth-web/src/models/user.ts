import { Contact } from '@/models/contact'

export interface User {
    firstname: string;
    lastname: string;
    username: string;
    contacts?: Contact[];
    modified?: Date
    // eslint-disable-next-line camelcase
    terms_of_use_version?: string,
    // eslint-disable-next-line camelcase
    is_terms_of_use_accepted?: boolean
}
