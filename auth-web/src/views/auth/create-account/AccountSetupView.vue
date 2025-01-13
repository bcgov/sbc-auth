<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-container"
  >
    <!-- Loading status -->
    <v-fade-transition>
      <div
        v-if="isCurrentUserSettingLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isCurrentUserSettingLoading"
        />
      </div>
    </v-fade-transition>
    <template v-if="!isCurrentUserSettingLoading">
      <div class="view-header flex-column">
        <h1 class="view-header__title">
          {{ $t('createBCRegistriesAccount') }}
        </h1>
        <p class="mt-3 mb-0">
          Create an account to access BC Registries products and services.
        </p>
      </div>
      <v-card flat>
        <Stepper
          :stepper-configuration="stepperConfig"
          :isLoading="isLoading"
          @final-step-action="verifyAndCreateAccount"
        />
      </v-card>
      <!-- Alert Dialog (Error) -->
      <ModalDialog
        ref="errorDialog"
        :title="errorTitle"
        :text="errorText"
        dialog-class="notify-dialog"
        max-width="640"
        data-test="modal-account-setup-error"
      >
        <template #icon>
          <v-icon
            large
            color="error"
          >
            mdi-alert-circle-outline
          </v-icon>
        </template>
        <template #actions>
          <v-btn
            large
            color="error"
            class="font-weight-bold"
            @click="closeError"
          >
            OK
          </v-btn>
        </template>
      </ModalDialog>
    </template>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Member, Organization, PADInfoValidation } from '@/models/Organization'
import { Account, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapState } from 'pinia'
import AccountCreate from '@/components/auth/create-account/AccountCreate.vue'
import { Action } from 'pinia-class'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import SelectProductService from '@/components/auth/create-account/SelectProductPayment.vue'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import { namespace } from 'vuex-class'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'
// This will be taken out with Vue3.
const AuthModule = namespace('auth')

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    AccountCreate,
    PaymentMethodSelector,
    SelectProductService,
    Stepper,
    ModalDialog
  },
  computed: {
    ...mapState(useUserStore, [
      'userContact'
    ]),
    ...mapState(useOrgStore, [
      'currentOrgPaymentType'
    ])
  },
  methods: {
    ...mapActions(useUserStore,
      [
        'createUserContact',
        'updateUserContact',
        'getUserProfile',
        'createAffidavit',
        'updateUserFirstAndLastName'
      ]),
    ...mapActions(useOrgStore,
      [
        'createOrg',
        'validatePADInfo',
        'syncMembership',
        'syncOrganization'
      ])
  }
})
export default class AccountSetupView extends Vue {
  private readonly currentOrgPaymentType!: string
  protected readonly userContact!: Contact
  private readonly createOrg!: () => Promise<Organization>
  private readonly validatePADInfo!: () => Promise<PADInfoValidation>
  private readonly createUserContact!: (contact?: Contact) => Contact
  private readonly updateUserContact!: (contact?: Contact) => Contact
  private readonly getUserProfile!: (identifer: string) => User
  readonly syncOrganization!: (orgId: number) => Promise<Organization>
  readonly syncMembership!: (orgId: number) => Promise<Member>
  private errorTitle = 'Account creation failed'
  private errorText = ''
  private isLoading: boolean = false
  private isCurrentUserSettingLoading: boolean = false
  @Prop({ default: '' }) redirectToUrl !: string
  @Prop({ default: false }) skipConfirmation !: boolean

  @AuthModule.Getter('isAuthenticated') readonly isAuthenticated!: boolean
  @Action(useUserStore) readonly getUserAccountSettings!: () => Promise<any>

  $refs: {
    errorDialog: InstanceType<typeof ModalDialog>
  }

  private stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreate,
        componentProps: {}
      },
      {
        title: 'Account Administrator Information',
        stepName: 'Account Administrator Information',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true
        }
      },
      {
        title: 'Select Products and Payment',
        stepName: 'Products and Payment',
        component: SelectProductService,
        componentProps: {
          isStepperView: true
        }
      }
    ]

  private async verifyAndCreateAccount () {
    this.isLoading = true
    let isProceedToCreateAccount = false
    if (this.currentOrgPaymentType === PaymentTypes.PAD) {
      isProceedToCreateAccount = await this.verifyPAD()
    } else {
      isProceedToCreateAccount = true
    }

    if (isProceedToCreateAccount) {
      this.createAccount()
    }
  }

  private async verifyPAD () {
    const verifyPad: PADInfoValidation = await this.validatePADInfo()
    if (!verifyPad) {
      // proceed to create account even if the response is empty
      return true
    }
    if (verifyPad?.isValid) {
      // create account if PAD info is valid
      return true
    } else {
      this.isLoading = false
      this.errorText = 'Bank information validation failed'
      if (verifyPad?.message?.length) {
        let msgList = ''
        verifyPad.message.forEach((msg) => {
          msgList += `<li>${msg}</li>`
        })
        this.errorText = `<ul style="list-style-type: none;">${msgList}</ul>`
      }
      this.$refs.errorDialog.open()
      return false
    }
  }

  private async createAccount () {
    this.isLoading = true
    try {
      const organization = await this.createOrg()
      await this.saveOrUpdateContact()
      await this.getUserProfile('@me')
      await this.syncOrganization(organization.id)
      await this.syncMembership(organization.id)
      // remove GOVN accoutn type from session
      ConfigHelper.removeFromSession(SessionStorageKeys.GOVN_USER)
      // Remove with Vue 3
      this.$store.commit('updateHeader')
      this.$router.push('/setup-account-success')
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      this.isLoading = false
      switch (err?.response?.status) {
        case 409:
          this.errorText =
                  'An account with this name already exists. Try a different account name.'
          break
        case 400:
          switch (err.response.data?.code) {
            case 'MAX_NUMBER_OF_ORGS_LIMIT':
              this.errorText = 'Maximum number of accounts reached'
              break
            case 'ACTIVE_AFFIDAVIT_EXISTS':
              this.errorText = err.response.data.message || 'Affidavit already exists'
              break
            default:
              this.errorText = 'An error occurred while attempting to create your account.'
          }
          break
        default:
          this.errorText =
                  'An error occurred while attempting to create your account.'
      }
      this.$refs.errorDialog.open()
    }
  }

  private async saveOrUpdateContact () {
    if (this.userContact) {
      await this.updateUserContact()
    } else {
      await this.createUserContact()
    }
  }

  closeError () {
    this.$refs.errorDialog.close()
  }

  mounted () {
    useOrgStore().setSelectedAccountType(Account.PREMIUM)
    useOrgStore().setCurrentOrganizationType(Account.PREMIUM)
  }
}
</script>
