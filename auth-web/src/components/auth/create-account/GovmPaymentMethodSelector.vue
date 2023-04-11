<template>
  <div data-test="div-stepper-payment-method-selector">
    <GLPaymentForm @is-gl-info-form-valid="isGLInfoValid"></GLPaymentForm>
    <v-divider class="my-10"></v-divider>
      <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
          data-test="btn-stepper-back"
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
          data-test="next-button"
          :disabled="!isGLValid"
        >
          <span >
            Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>

        </v-btn>
        <ConfirmCancelButton
          showConfirmPopup="true"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { Component, Mixins } from 'vue-property-decorator'

@Component({
  components: {
    ConfirmCancelButton,
    GLPaymentForm
  }
})
// GovmPaymentMethodSelector
export default class GovmPaymentMethodSelector extends Mixins(Steppable) {
  public isGLValid: boolean = false

  public isGLInfoValid (isValid) {
    this.isGLValid = isValid
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

</style>
