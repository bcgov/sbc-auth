<template>
  <v-dialog
      v-model="showConfirmDialog"
      width="360"
    >
    <template v-slot:activator="{ on }">
      <v-btn
        large
        color="default"
        :disabled="disabled"
        @click="showConfirmDialog = true"
        v-on="on"
      >
        Cancel
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        <h3>{{mainText}}</h3>
      </v-card-title>
      <v-card-text>
        {{subText}}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="confirmDialogResponse(false)">
          <strong>{{rejectText}}</strong>
        </v-btn>
        <v-btn color="primary" text @click="confirmDialogResponse(true)">
          <strong>{{acceptText}}</strong>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import Vue from 'vue'
import { mapActions } from 'vuex'

@Component({
  methods: {
    ...mapActions('org', [
      'resetAccountSetupProgress'
    ])
  }
})
export default class CancelButton extends Vue {
  @Prop({ default: false }) isEmit: boolean
  @Prop({ default: false }) disabled: boolean
  @Prop({ default: 'Are you sure?' }) mainText: string
  @Prop({ default: 'Your progress will be lost' }) subText: string
  @Prop({ default: 'Yes' }) acceptText: string
  @Prop({ default: 'No' }) rejectText: string
  private showConfirmDialog: boolean = false

  private readonly resetAccountSetupProgress!: () => Promise<void>

  private confirmDialogResponse (response) {
    if (response) {
      this.clickConfirm()
    }
    this.showConfirmDialog = false
  }

  private async clickConfirm () {
    await this.resetAccountSetupProgress()
    if (this.isEmit) {
      this.emitClickConfirm()
    } else {
      this.$router.push('/')
    }
  }

  @Emit('click-confirm')
  emitClickConfirm () {
  }
}
</script>
