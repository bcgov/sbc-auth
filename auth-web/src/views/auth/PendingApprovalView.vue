<template>
  <div>
    <template v-if="isGVMUser">
      <GovmAccountCreationSuccessView />
    </template>
    <template v-else>
      <template v-if="isDenied">
        <interim-landing
          :summary="$t('notAuthorized')"
          :description="$t('deniedInvitationMsg', { team: teamName })"
          icon="mdi-alert-circle-outline"
          iconColor="error"
        />
      </template>
      <template v-else>
        <div v-if="teamName">
          <interim-landing
            :summary="$t(title, { team: teamName })"
            :description="$t(description, descriptionParams)"
            icon="mdi-information-outline"
          />
        </div>
        <div v-if="!teamName">
          <interim-landing
            :summary="$t('noPendingInvitationTitle')"
            :description="$t('noPendingInvitationMsg')"
            icon="mdi-information-outline"
          />
        </div>
      </template>
    </template>
  </div>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import GovmAccountCreationSuccessView from '@/views/auth/create-account/GovmAccountCreationSuccessView.vue'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import Vue from 'vue'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

@Component({
  components: { InterimLanding, GovmAccountCreationSuccessView }
})

export default class PendingApprovalView extends Vue {
  @State(useOrgStore) private currentMembership!: Member
  @State(useOrgStore) public currentOrganization!: Organization
  @State(useUserStore) private currentUser!: KCUserProfile
  @Action(useOrgStore) private syncMembership!: (orgId: number) => Promise<Member>

  private readonly descriptionParams: any = { 'days': ConfigHelper.getAccountApprovalSlaInDays() }

  private isDenied: boolean = false
  public isGVMUser: boolean = false
  public isAffidaventPendingAdmin:boolean = false

  @Prop({ default: '' }) teamName: string
  @Prop({ default: '' }) pendingAffidavit: string

  async mounted () {
    // if current membership is not there we request here
    if (!this.currentMembership && this.currentOrganization?.id) {
      await this.syncMembership(this.currentOrganization.id)
    }
    this.isGVMUser = this.currentUser.roles.includes(Role.GOVMAccountUser) || false
    this.isDenied = (this.currentMembership?.membershipStatus === MembershipStatus.Rejected ||
      this.currentMembership?.membershipStatus === MembershipStatus.Inactive)
    this.isAffidaventPendingAdmin = this.currentMembership?.membershipStatus === MembershipStatus.PendingStaffReview
  }

  get title () {
    if (this.isAffidaventPendingAdmin) {
      return 'pendingAffidavitAdminReviewTitle'
    }
    return this.pendingAffidavit === 'true' ? 'pendingAffidavitReviewTitle' : 'pendingInvitationTitle'
  }
  get description () {
    if (this.isAffidaventPendingAdmin) {
      return 'pendingAffidvitAdminReviewMessage'
    }
    return this.pendingAffidavit === 'true' ? 'pendingAffidvitReviewMessage' : 'pendingInvitationMsg'
  }
}
</script>
