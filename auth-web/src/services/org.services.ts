import Axios, { AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Members } from '@/models/Organization'
import { Invitations } from '@/models/Invitation'

export default class OrgService {
    public static async getOrgMembers (orgId: string): Promise<AxiosResponse<Members>> {
        return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members`)
    }
    
    public static async getOrgInvitations (orgId: string): Promise<AxiosResponse<Invitations>> {
        return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/invitations`)
    }
}
