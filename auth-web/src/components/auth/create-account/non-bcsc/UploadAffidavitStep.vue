<template>
  <div>
    <p class="mb-7">
      This will be reviewed by Registries staff and the account will be approved
      when authenticated.
    </p>
    <h4 class="my-4">Attach your Notarized Affidavit</h4>
    <FileUploadPreview
      :maxSize="MAX_FILE_SIZE"
      v-bind:input-file="affidavitDoc"
      @file-selected="fileSelected"
      @is-file-valid="isFileUploadValidFn"
    ></FileUploadPreview>
    <NotaryInformationForm
      :input-notary-info="notaryInformation"
      @notaryinfo-update="updateNotaryInformation"
      @is-form-valid="isNotaryInformationValidFn"
      class="pt-5"
      v-if="notaryInformation"
    ></NotaryInformationForm>
    <NotaryContactForm
      :input-notary-contact="notaryContact"
      @notarycontact-update="updateNotaryContact"
      @is-form-valid="isNotaryContactValidFn"
      class="pt-5"
    ></NotaryContactForm>
    <v-alert
      dense
      text
      type="error"
      class="mt-6"
      v-if="errorMessage"
    >
      {{errorMessage}}
    </v-alert>
    <v-row class="mt-8">
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn large depressed color="default" @click="goBack" v-if="!isAffidavitUpload">
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="mr-3"
          :loading="saving"
          :disabled="saving || !isNextValid"
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
          v-if="!isAffidavitUpload"
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
import { Address } from '@/models/address'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import FileUploadPreview from '@/components/auth/common/FileUploadPreview.vue'
import NotaryContactForm from '@/components/auth/create-account/non-bcsc/NotaryContactForm.vue'
import NotaryInformationForm from '@/components/auth/create-account/non-bcsc/NotaryInformationForm.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
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
      'notaryContact',
      'affidavitDoc'
    ])
  },
  methods: {
    ...mapMutations('org', ['setCurrentOrganization', 'setOrgName']),
    ...mapMutations('user', ['setNotaryInformation', 'setNotaryContact', 'setAffidavitDoc']),
    ...mapActions('org', [
    ]),
    ...mapActions('user', [
      'uploadPendingDocsToStorage'
    ])
  }
})
export default class UploadAffidavitStep extends Mixins(Steppable) {
  @Prop({ default: false }) isAffidavitUpload: boolean
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private errorMessage: string = ''
  private saving: boolean = false
  private MAX_FILE_SIZE = 10000 // 10 MB in KB
  private isNotaryContactValid: boolean = false
  private isNotaryInformationValid: boolean = false
  private isFileUploadValid: boolean = false
  private readonly notaryInformation!: NotaryInformation
  private readonly affidavitDoc!:File
  private readonly notaryContact!: NotaryContact
  private readonly uploadPendingDocsToStorage!: () => void
  private readonly setNotaryInformation!: (
    notaryInformation: NotaryInformation
  ) => void
  private readonly setAffidavitDoc!: (
          affidavitDoc: File
  ) => void
  private readonly setNotaryContact!: (notaryContact: NotaryContact) => void
  private readonly currentOrganization!: Organization

  @Prop() cancelUrl: string

  private async mounted () {
    this.errorMessage = ''
    if (!this.notaryInformation) {
      this.setNotaryInformation({ notaryName: '', address: {} as Address })
    }
  }

  private async next () {
    try {
      this.errorMessage = ''
      this.saving = true
      // save the file here so that in the final steps its less network calls to make
      // await this.uploadPendingDocsToStorage()
      if (this.isAffidavitUpload) {
        // emit event to let parent know the upload affidavit step is complete
        this.$emit('emit-admin-affidavit-complete')
      } else {
        this.stepForward(this.currentOrganization?.orgType === Account.PREMIUM)
      }
    } catch (error) {
      this.errorMessage = `Something happend while uploading the document, please try again`
      // eslint-disable-next-line no-console
      console.error(error)
    } finally {
      this.saving = false
    }
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }

  private goBack () {
    this.stepBack()
  }

  private async goNext () {
    this.stepForward()
  }

  private fileSelected (file) {
    this.errorMessage = ''
    this.setAffidavitDoc(file)
  }

  private updateNotaryInformation (notaryInfo: NotaryInformation) {
    this.setNotaryInformation(notaryInfo)
  }

  private updateNotaryContact (notaryContact: NotaryContact) {
    this.setNotaryContact(notaryContact)
  }

  private get isNextValid () {
    return this.isFileUploadValid && this.isNotaryInformationValid && this.isNotaryContactValid
  }

  private isNotaryContactValidFn (val) {
    this.isNotaryContactValid = val
  }

  private isNotaryInformationValidFn (val) {
    this.isNotaryInformationValid = val
  }

  private isFileUploadValidFn (val) {
    this.isFileUploadValid = val
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
