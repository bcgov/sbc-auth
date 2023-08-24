<template>
  <v-btn
    large
    depressed
    color="default"
    data-test="confirm-cancel-button"
    :disabled="disabled"
    @click="openModalDialog"
  >
    Cancel
    <!-- Confirm Dialog Popup -->
    <ModalDialog
      ref="confirmCancelDialog"
      :title="mainText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #text>
        <p class="pb-1">
          {{ subText }}
        </p>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          data-test="accept-button"
          @click="confirmDialogResponse(true)"
        >
          {{ confirmBtnText }}
        </v-btn>
        <v-btn
          large
          color="default"
          data-test="reject-button"
          @click="confirmDialogResponse(false)"
        >
          {{ rejectBtnText }}
        </v-btn>
      </template>
    </ModalDialog>
  </v-btn>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import { Action } from 'pinia-class'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Vue from 'vue'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    ModalDialog
  }
})
export default class ConfirmCancelButton extends Vue {
  @Prop({ default: false }) isEmit: boolean
  @Prop({ default: true }) showConfirmPopup: boolean
  @Prop({ default: false }) disabled: boolean
  @Prop({ default: 'Cancel Account Creation' }) mainText: string
  @Prop({ default: 'Are you sure you want to cancel your account creation set-up?' }) subText: string
  @Prop({ default: 'Yes' }) confirmBtnText: string
  @Prop({ default: 'No' }) rejectBtnText: string
  // targetRoute can be passed in when different page has to be shown after cancelling
  @Prop({ default: '/' }) targetRoute: string
  // for not to clear current org values [for account change , while clicking on cancel , current org has to stay]
  @Prop({ default: true }) clearCurrentOrg: boolean

  @Action(useOrgStore) private setCurrentOrganizationFromUserAccountSettings!: () => Promise<void>
  @Action(useOrgStore) private resetAccountSetupProgress!: () => Promise<void>

  $refs: {
      confirmCancelDialog: ModalDialog
  }

  private async confirmDialogResponse (response) {
    if (response) {
      this.clickConfirm()
    }
    this.$refs.confirmCancelDialog.close()
  }

  private async clickConfirm () {
    try {
      if (this.clearCurrentOrg) {
        await this.resetAccountSetupProgress()
        await this.setCurrentOrganizationFromUserAccountSettings()
        // Remove in Vue 3
        await this.$store.commit('updateHeader')
      }
      if (this.isEmit) {
        this.emitClickConfirm()
      } else {
        this.$router.push(this.targetRoute)
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.log('Error while cancelling account creation flow', err)
    }
  }

  @Emit('click-confirm')
  emitClickConfirm () {
  }

  private openModalDialog () {
    if (this.showConfirmPopup) {
      this.$refs.confirmCancelDialog.open()
    } else {
      this.clickConfirm()
    }
  }
}
</script>
