import Axios, { AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Invitation } from '@/models/Invitation'

export default class InvitationService {
    public static async createInvitation (invitation: Invitation): Promise<AxiosResponse<Invitation>> {
        return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations`, invitation)
    }
}