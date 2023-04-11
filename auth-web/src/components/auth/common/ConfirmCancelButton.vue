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
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:text>
        <p class="pb-1">{{subText}}</p>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="confirmDialogResponse(true)" data-test="accept-button">
          {{confirmBtnText}}
        </v-btn>
        <v-btn large color="default" @click="confirmDialogResponse(false)" data-test="reject-button">
          {{rejectBtnText}}
        </v-btn>
      </template>
    </ModalDialog>
  </v-btn>
</template>

<script lang="ts">
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Vue from 'vue'
import { Component, Emit, Prop } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

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

  @OrgModule.Action('setCurrentOrganizationFromUserAccountSettings') private setCurrentOrganizationFromUserAccountSettings!: () => Promise<void>
  @OrgModule.Action('resetAccountSetupProgress') private resetAccountSetupProgress!: () => Promise<void>

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
        // Update header
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
