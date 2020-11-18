import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-4">Please review your pre-authorized debit information. If anything is wrong please edit your information.</p>
    <v-row class="mb-12 pb-12">
      <v-col md="10">
        <PADInfoForm
          :padInformation="{}"
          @is-pre-auth-debit-form-valid="isPADValid"
          @emit-pre-auth-debit-info="getPADInfo"
          :isAcknowledgeNeeded="false"
          :isTOSNeeded="false"
        ></PADInfoForm>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
        >
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          @click="goNext"
          :disabled="!padValid"
        >
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Organization, PADInfo } from '@/models/Organization'
import { mapMutations, mapState } from 'vuex'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    PADInfoForm
  },
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  }
})
export default class ReviewBankInformation extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization
  private padInfo: PADInfo = {} as PADInfo
  private padValid: boolean = false

  private goNext () {
    this.stepForward()
  }

  private goBack () {
    this.stepBack()
  }

  private getPADInfo (padInfo: PADInfo) {
    this.padInfo = padInfo
  }

  private isPADValid (isValid) {
    this.padValid = isValid
  }
}
</script>
