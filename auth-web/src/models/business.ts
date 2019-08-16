import { Contact } from './contact'

export interface Business {
    businessIdentifier: string;
    contacts?: Contact[];
}
