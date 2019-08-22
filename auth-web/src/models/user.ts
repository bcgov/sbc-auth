import { UserContact } from './usercontact'

export interface User {
    firstname: string;
    lastname: string;
    username: string;
    contacts: UserContact[]
}
