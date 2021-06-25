<template>
  <v-container>
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb">
      <div>
        <router-link :to="`/account/${currentOrganization.id}`">
          <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
          <span>Back to Account</span>
        </router-link>
      </div>
    </nav>
    <header class="view-header mb-9">
      <h2 class="view-header__title">Deactivate Account</h2>
    </header>
    <div class="mb-9">
      Please review the information below before deactivating your BC Registries and Online Services account.
    </div>
    <div>
      <deactivate-card :org-type="currentOrganization.orgType"></deactivate-card>
    </div>
    <v-card class="mt-10">
      <v-card-title class="font-weight-bold">
        Authorize and Deactivate Account
      </v-card-title>
      <v-card-text>
        <v-layout row wrap>
          <v-row v-for="(category,index) in confirmations" :key="confirmations[index].text">
            <v-checkbox
              color="primary"
              class="ml-10 ma-0 pa-0 mr-5"
              required
              v-model="category.selected"
              data-test="check-termsAccepted"
            >
              <template v-slot:label>
                <span>
               {{ $t(category.text, params) }}
                  </span>
              </template>
            </v-checkbox>
          </v-row>
        </v-layout>
      </v-card-text>
      <v-divider class="mt-3 mb-10"></v-divider>
      <v-card-actions>
        <v-row>
          <v-col align="right">
            <v-btn
              large
              color="error"
              class="mr-2"
              @click="confirm()"
              :disabled="authorised"
              data-test="deactivate-button"
            >Deactivate account
            </v-btn>

            <v-btn
              large
              depressed
              align="right"
              class="cancel-btn"
              @click="closeConfirmModal()"
              color="default"
              data-test="cancel-button"
            >Cancel
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
    <!-- Dialog for confirming deactivation -->
    <ModalDialog
      ref="confirmModal"
      title="Deactivate Account?"
      dialog-class="notify-dialog"
      max-width="640"
      text="Are you sure you want to deactivate this account?"
    >

      <template v-slot:icon>
        <v-fade-transition>
          <div class="loading-container" v-if="isLoading">
            <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
          </div>
        </v-fade-transition>
        <v-icon large color="primary">mdi-help-circle</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="deactivate()" data-test="deactivate-btn" class="mr-5">Deactivate</v-btn>
        <v-btn large @click="close()" data-test="close-dialog-btn">Cancel</v-btn>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="successModal"
      title="Account Deactivated"
      dialog-class="notify-dialog"
      max-width="640"
      :text="message"
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-check</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" data-test="deactivate-btn" class="mr-5" @click="navigateTohome()">OK</v-btn>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="errorModal"
      title="You can't currently deactivate account"
      dialog-class="notify-dialog"
      max-width="640"
      :text="message"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-information-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" data-test="deactivate-btn" class="mr-5" :to="`/account/${currentOrganization.id}`">
          Back to Account Information
        </v-btn>
      </template>
    </ModalDialog>

  </v-container>
</template>

<script lang="ts">

import { Component, Prop } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import CommonUtil from '@/util/common-util'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Vue from 'vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  components: {
    DeactivateCard,
    AccountSuspendAlert,
    ModalDialog
  }
})
export default class AccountDeactivate extends Vue {
  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @OrgModule.State('currentMembership') public currentMembership!: Member
  @Prop({ default: '' }) private name: string
  @OrgModule.Action('deactivateOrg') public deactivateOrg!: () => Promise<void>
  @OrgModule.Action('setCurrentOrganizationFromUserAccountSettings') private setCurrentOrganizationFromUserAccountSettings!: () => Promise<void>
  private message = ''
  private isLoading = false

  $refs: {
    confirmModal: ModalDialog,
    successModal: ModalDialog,
    errorModal: ModalDialog

  }
  private confirmationsList: { text: string, type?: string, selected: boolean }[] = [
    {
      text: 'deactivateTeamConfirmation',
      selected: false
    },
    {
      text: 'deactivatePadConfirmation',
      type: 'PREMIUM',
      selected: false
    }

  ]

  private async confirm () {
    // eslint-disable-next-line no-console
    this.$refs.confirmModal.open()
  }

  private get confirmations () {
    return this.confirmationsList.filter(obj => !obj.type || obj.type === this.currentOrganization.orgType)
  }

  private get params () {
    return {
      'name': (this.currentMembership.user.firstname || '') + ' ' + (this.currentMembership.user.lastname || ''),
      'id': this.currentOrganization.id,
      'date': CommonUtil.formatCurrentDate()
    }
  }

  private async closeConfirmModal () {
    this.$refs.confirmModal.close()
  }

  private async navigateTohome () {
    this.$refs.successModal.close()
    await this.setCurrentOrganizationFromUserAccountSettings()
    // Update header
    await this.$store.commit('updateHeader')
    this.$router.push(`/home`)
  }

  private async deactivate () {
    try {
      this.isLoading = true
      await this.deactivateOrg()
      this.isLoading = false
      await this.closeConfirmModal()
      this.message = `The account <strong>${this.currentOrganization.name}</strong> has been deactivated.`
      this.$refs.successModal.open()
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      switch (err?.response?.status) {
        case 400:
          this.message = err.response.data.message
          break
        default:
          this.message =
            'An error occurred while attempting to deactivate your account.Please try again'
      }
      this.$refs.confirmModal.close()
      this.$refs.errorModal.open()
    }
  }

  private get authorised (): boolean {
    return this.confirmations.some(obj => obj.selected === false)
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

</style>
