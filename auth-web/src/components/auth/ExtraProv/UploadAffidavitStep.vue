<template>
  <div>
    <p class="mb-7">
      This will be reviewed by Registries staff and the account will be approved
      when authenticated.
    </p>
    <h4 class="my-4">Attach your Notarized Affidavit</h4>
    <FileUploadPreview @file-selected="fileSelected"></FileUploadPreview>
    <NotaryInformationForm
      :input-notary-info="notaryInformation"
      @notaryinfo-update="updateNotaryInformation"
      class="pt-5"
      v-if="notaryInformation"
    ></NotaryInformationForm>
    <NotaryContactForm
      :input-notary-contact="notaryContact"
      @notarycontact-update="updateNotaryContact"
      class="pt-5"
    ></NotaryContactForm>
    <v-row class="mt-8">
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn large depressed color="default" @click="goBack">
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="mr-3"
          :loading="saving"
          :disabled="saving"
          @click="next"
          data-test="next-button"
        >
          <span
            >Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>
        </v-btn>
        <ConfirmCancelButton
          :disabled="saving"
          :target-route="cancelUrl"
          :showConfirmPopup="true"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { NotaryContact, NotaryInformation } from '@/models/notary'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import FileUploadPreview from '@/components/auth/common/FileUploadPreview.vue'
import NotaryContactForm from '@/components/auth/NotaryContactForm.vue'
import NotaryInformationForm from '@/components/auth/NotaryInformationForm.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/stepper/Steppable.vue'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BcolLogin,
    NotaryInformationForm,
    NotaryContactForm,
    ConfirmCancelButton,
    FileUploadPreview
  },
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('user', [
      'userProfile',
      'currentUser',
      'notaryInformation',
      'notaryContact'
    ])
  },
  methods: {
    ...mapMutations('org', ['setCurrentOrganization', 'setOrgName']),
    ...mapMutations('user', ['setNotaryInformation', 'setNotaryContact']),
    ...mapActions('org', [
      'createOrg',
      'syncMembership',
      'syncOrganization',
      'isOrgNameAvailable',
      'changeOrgType'
    ])
  }
})
export default class UploadAffidavitStep extends Mixins(Steppable) {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private errorMessage: string = ''
  private saving = false
  private notaryInformation!: NotaryInformation
  private readonly notaryContact!: NotaryContact
  private readonly setNotaryInformation!: (
    notaryInformation: NotaryInformation
  ) => void
  private readonly setNotaryContact!: (notaryContact: NotaryContact) => void
  private readonly currentOrganization!: Organization
  private orgName: string = ''
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string

  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly orgNameRules = [(v) => !!v || 'An account name is required']

  private isFormValid (): boolean {
    return !!this.orgName
  }

  private async mounted () {
    if (this.currentOrganization) {
      this.orgName = this.currentOrganization.name
    }
    if (!this.notaryInformation) {
      this.setNotaryInformation({ notaryName: '', address: {} })
    }
  }

  private async next () {
    this.stepForward(this.currentOrganization?.orgType === Account.PREMIUM)
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }

  private goBack () {
    this.stepBack()
  }

  private goNext () {
    this.stepForward()
  }

  private fileSelected (file) {
    // eslint-disable-next-line no-console
    console.log(file)
  }

  private updateNotaryInformation (notaryInfo: NotaryInformation) {
    this.setNotaryInformation(notaryInfo)
  }

  private updateNotaryContact (notaryContact: NotaryContact) {
    this.setNotaryContact(notaryContact)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}

.bcol-acc-label {
  font-size: 1.35rem;
  font-weight: 600;
}

.grant-access {
  font-size: 1rem !important;
}
</style>
