<template>
  <v-form ref="form" lazy-validation data-test="form-profile">
    <p class="mb-9" v-if="isStepperView">Which products will this account require access to?</p>

    <v-divider class="mt-7 mb-10"></v-divider>

    <v-row>
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <!-- The deactivate profile button should be hidden for account stepper view -->

        <v-btn
          large
          depressed
          v-if="isStepperView"
          color="default"
          @click="goBack"
          data-test="btn-back"
        >
          <v-icon left class="mr-2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>

        <v-btn
          large
          color="primary"
          class="save-continue-button mr-3"

          @click="next"
          v-if="isStepperView"
          data-test="next-button"
        >
          <span >
            Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>

        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="isStepperView"
          :isEmit="true"
          @click-confirm="cancel"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>

  </v-form>
</template>

<script lang="ts">
// keep it simple later edit
import { Component, Mixins, Prop } from 'vue-property-decorator'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'

import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    ConfirmCancelButton
  }
})
export default class ProductPackages extends Mixins(NextPageMixin, Steppable) {
  @Prop({ default: false }) isStepperView: boolean

  $refs: {
    form: HTMLFormElement
  }

  public goBack () {
    this.stepBack()
  }
  public next () {
    this.stepForward()
  }
  private cancel () {
    this.$router.push('/')
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

</style>
