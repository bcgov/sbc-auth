<template>
  <v-form
    ref="form"
    data-test="form-govm-contact"
  >
    <p class="mb-9">
      Enter the IDIR email address of the ministry's employee.
      An email will be sent this user to verify and activate this account. This user will be the admin of this account.
    </p>
    <v-row>
      <v-col
        cols="12"
        class="py-0 mb-4"
      >
        <h4
          class="mb-1"
        >
          Account Admin Contact
        </h4>
      </v-col>
    </v-row>
    <!-- Email Address -->
    <v-row>
      <v-col
        cols="12"
        class="pt-0 pb-0"
      >
        <v-text-field
          v-model="emailAddress"
          filled
          label="Email Address"
          req
          persistent-hint
          data-test="email"
          readonly
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="pt-0 pb-0"
      >
        <v-text-field
          v-model="confirmedEmailAddress"
          filled
          label="Confirm Email Address"
          req
          persistent-hint
          data-test="confirm-email"
          readonly
        />
      </v-col>
    </v-row>
    <v-divider class="mt-7 mb-10" />

    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-3"
          data-test="next-button"
          @click="createAccount"
        >
          <span>
            Create Account
          </span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="true"
          :isEmit="true"
          @click-confirm="cancel"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">

import { Component, Emit, Mixins } from 'vue-property-decorator'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { User } from '@/models/user'

import { namespace } from 'vuex-class'
const userModule = namespace('user')

@Component({
  components: {
    ConfirmCancelButton
  }
})
export default class GovmContactInfoForm extends Mixins(NextPageMixin, Steppable) {
  @userModule.Action('getUserProfile') public getUserProfile!: (identifer: string) => User

  public emailAddress = ''
  public confirmedEmailAddress = ''
  // @Prop({ default: false }) isStepperView: boolean

  $refs: {
    form: HTMLFormElement
  }

  public async mounted () {
    await this.getUserProfile('@me')
    this.emailAddress = this.userProfile?.email || ''
    this.emailAddress = this.confirmedEmailAddress = this.userProfile?.email || ''
  }
  // email is readonly to show. no need to save
  @Emit('final-step-action')
  public createAccount () {
  }

  public cancel () {
    this.$router.push('/')
  }

  public goBack () {
    this.stepBack()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.legal-name {
  font-size: 1.25rem !important;
  font-weight: 700;
  letter-spacing: -0.02rem;
}
</style>
