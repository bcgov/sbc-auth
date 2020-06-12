<template>
  <div>
    <p class="mb-7">This will be reviewed by Registries staff and the account will be approved when authenticated.</p>
    <h4 class="my-4">Attach your Notarized Affidavit</h4>
    <FileUploadPreview
      @file-selected="fileSelected"
    ></FileUploadPreview>
    <NotaryInformationForm
      @notaryinfo-update="notaryInformation"
      class="pt-5"
    ></NotaryInformationForm>
    <NotaryContactForm
      @notarycontact-update="notaryContact"
      class="pt-5"
    ></NotaryContactForm>
    <v-row class="mt-8">
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack">
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
          <span>Next
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
import { Account, Actions, Pages } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import FileUploadPreview from '@/components/auth/common/FileUploadPreview.vue'
import NotaryContactForm from '@/components/auth/NotaryContactForm.vue'
import NotaryInformationForm from '@/components/auth/NotaryInformationForm.vue'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/stepper/Steppable.vue'
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
    ...mapState('user', ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganization', 'setOrgName'
    ]),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization', 'isOrgNameAvailable', 'changeOrgType'])
  }
})
export default class UploadAffidavitStep extends Mixins(Steppable) {
  private orgStore = getModule(OrgModule, this.$store)
  private errorMessage: string = ''
  private saving = false
  private readonly createOrg!: () => Promise<Organization>
  private readonly changeOrgType!: (action:Actions) => Promise<Organization>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly isOrgNameAvailable!: (orgName: string) => Promise<boolean>
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly currentOrganization!: Organization
  private orgName: string = ''
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string

  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly orgNameRules = [v => !!v || 'An account name is required']
  private isFormValid (): boolean {
    return !!this.orgName
  }

  private async mounted () {
    if (this.currentOrganization) {
      this.orgName = this.currentOrganization.name
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

  private notaryInformation (notaryInfo) {
    // eslint-disable-next-line no-console
    console.log(notaryInfo)
  }

  private notaryContact (notaryContact) {
    // eslint-disable-next-line no-console
    console.log(notaryContact)
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
