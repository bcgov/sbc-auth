<template>
  <v-container class="center-container">
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <router-link :to="accountInfoUrl">
          <v-icon
            small
            color="primary"
            class="mr-1"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back to Account</span>
        </router-link>
      </div>
    </nav>
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Deactivate Account
      </h1>
      <p class="mt-3 mb-0">
        Please review the information below before deactivating your BC
        Registries and Online Services account.
      </p>
    </div>

    <div>
      <deactivate-card :type="orgType" />
    </div>
    <v-card class="mt-5 py-4 px-4">
      <v-card-title class="font-weight-bold">
        Authorize and Deactivate Account
      </v-card-title>
      <v-card-text>
        <v-row>
          <div
            v-for="(category, index) in confirmations"
            :key="confirmations[index].text"
            class="mt-3"
          >
            <v-checkbox
              v-model="category.selected"
              color="primary"
              class="ml-7 ma-0 pa-0 mr-5"
              required
              data-test="check-termsAccepted"
            >
              <template #label>
                <div class="ml-7">
                  {{ $t(category.text, params) }}
                </div>
              </template>
            </v-checkbox>
          </div>
        </v-row>
      </v-card-text>
      <v-divider class="mt-3" />
      <v-card-actions>
        <v-row>
          <v-col class="align">
            <v-btn
              large
              color="error"
              class="mr-2"
              :disabled="authorised"
              data-test="deactivate-button"
              @click="confirm()"
            >
              Deactivate account
            </v-btn>

            <v-btn
              large
              depressed
              align="right"
              class="cancel-btn"
              :to="accountInfoUrl"
              color="default"
              data-test="cancel-button"
            >
              Cancel
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
      <template #icon>
        <v-fade-transition>
          <div
            v-if="isLoading"
            class="loading-container"
          >
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>
        </v-fade-transition>
        <v-icon
          large
          color="primary"
        >
          mdi-help-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="deactivate-btn"
          class="mr-5 px-4"
          @click="deactivate()"
        >
          Deactivate
        </v-btn>
        <v-btn
          large
          data-test="close-dialog-btn"
          class="px-4"
          @click="closeConfirmModal()"
        >
          Cancel
        </v-btn>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="successModal"
      title="Account Deactivated"
      dialog-class="notify-dialog"
      max-width="640"
      :text="message"
    >
      <template #icon>
        <v-icon
          large
          color="primary"
        >
          mdi-check
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="deactivate-btn"
          class="mr-5"
          @click="navigateTohome()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="errorModal"
      title="This account can’t be deactivated yet"
      dialog-class="notify-dialog"
      max-width="640"
      :text="message"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-information-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="deactivate-btn"
          class="mr-5"
          :to="accountInfoUrl"
        >
          Back to Account Information
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Prop } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import CommonUtil from '@/util/common-util'
import { DEACTIVATE_ACCOUNT_MESSAGE } from '@/util/constants'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Vue from 'vue'
import { useOrgStore } from '@/store/org'

@Component({
  components: {
    DeactivateCard,
    AccountSuspendAlert,
    ModalDialog
  }
})
export default class AccountDeactivate extends Vue {
  @State(useOrgStore) public currentOrganization!: Organization
  @State(useOrgStore) public currentMembership!: Member
  @Prop({ default: '' }) private name: string
  @Action(useOrgStore) public deactivateOrg!: () => Promise<void>
  @Action(useOrgStore) private setCurrentOrganizationFromUserAccountSettings!: () => Promise<void>
  message = ''
  isLoading = false

  $refs: {
    confirmModal: ModalDialog,
    successModal: ModalDialog,
    errorModal: ModalDialog

  }
  confirmationsList: { text: string, type?: string, selected: boolean }[] = [
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

  async confirm () {
    this.$refs.confirmModal.open()
  }

  get confirmations () {
    return this.confirmationsList.filter(obj => !obj.type || obj.type === this.currentOrganization?.orgType)
  }

  private get params () {
    return {
      'name': (this.currentMembership?.user?.firstname || '') + ' ' + (this.currentMembership?.user?.lastname || ''),
      'id': this.currentOrganization?.id,
      'date': CommonUtil.formatCurrentDate()
    }
  }

  get accountInfoUrl (): string {
    return `/account/${this.currentOrganization?.id}/settings`
  }

  async closeConfirmModal () {
    this.$refs.confirmModal.close()
  }

  get orgType (): string {
    return this.currentOrganization?.orgType
  }

  async navigateTohome () {
    this.$refs.successModal.close()
    await this.setCurrentOrganizationFromUserAccountSettings()
    // Update header
    // Remove with Vue 3
    await this.$store.commit('updateHeader')
    this.$router.push(`/home`)
  }

  async deactivate () {
    try {
      this.isLoading = true
      await this.deactivateOrg()
      this.isLoading = false
      await this.closeConfirmModal()
      this.message = `The account <strong>${this.currentOrganization.name}</strong> has been deactivated.`
      this.$refs.successModal.open()
    } catch (err) {
      // eslint-disable-next-line no-console
      this.message = this.$t(DEACTIVATE_ACCOUNT_MESSAGE.get(err.response?.data?.code || 'DEFAULT')).toString()
      this.$refs.confirmModal.close()
      this.$refs.errorModal.open()
    }
  }

  get authorised (): boolean {
    return this.confirmations.some(obj => obj.selected === false)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.back-btn {
  font-weight: 700;

  span {
    margin-top: -1px;
  }

  &:hover {
    span {
      text-decoration: underline;
    }
  }
}

.crumbs a {
  font-size: 0.875rem;
  text-decoration: none;

  i {
    margin-top: -2px;
  }
}

.crumbs a:hover {
  span {
    text-decoration: underline;
  }
}

.crumbs-visible {
  padding-top: 0 !important;
}
</style>
