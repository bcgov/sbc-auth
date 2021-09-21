<template>
  <div>
    <template v-if="isGVMUser">
      <GovmAccountCreationSuccessView />
    </template>
    <template v-else>
      <template v-if="isDenied">
        <interim-landing :summary="$t('notAuthorized')" :description="$t('deniedInvitationMsg', { team: teamName })" icon="mdi-alert-circle-outline" iconColor="error">
        </interim-landing>
      </template>
      <template v-else>
        <div v-if="teamName">
          <interim-landing :summary="$t(title, { team: teamName })" :description="$t(description, descriptionParams)" icon="mdi-information-outline">
          </interim-landing>
        </div>
        <div v-if="!teamName">
          <interim-landing :summary="$t('noPendingInvitationTitle')" :description="$t('noPendingInvitationMsg')" icon="mdi-information-outline">
          </interim-landing>
        </div>
      </template>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import GovmAccountCreationSuccessView from '@/views/auth/create-account/GovmAccountCreationSuccessView.vue'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  components: { InterimLanding, GovmAccountCreationSuccessView },
  computed: {
    ...mapState('org', [
      'currentMembership'
    ]),
    ...mapState('user', [
      'currentUser'
    ])
  }
})

export default class PendingApprovalView extends Vue {
  protected readonly currentMembership!: Member
  protected readonly currentUser!: KCUserProfile

  private readonly descriptionParams: any = { 'days': ConfigHelper.getAccountApprovalSlaInDays() }

  private isDenied: boolean = false
  public isGVMUser: boolean = false

  @Prop({ default: '' }) teamName: string
  @Prop({ default: '' }) pendingAffidavit: string

  mounted () {
    this.isGVMUser = this.currentUser.roles.includes(Role.GOVMAccountUser) || false

    this.isDenied = (this.currentMembership?.membershipStatus === MembershipStatus.Rejected || this.currentMembership?.membershipStatus === MembershipStatus.Inactive)
  }

  get title () {
    return this.pendingAffidavit === 'true' ? 'pendingAffidavitReviewTitle' : 'pendingInvitationTitle'
  }
  get description () {
    return this.pendingAffidavit === 'true' ? 'pendingAffidvitReviewMessage' : 'pendingInvitationMsg'
  }
}
</script>
