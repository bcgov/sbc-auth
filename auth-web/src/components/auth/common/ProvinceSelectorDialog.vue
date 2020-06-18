<template>
  <v-card>
    <v-card-title>Create a BC Registries Account</v-card-title>
    <v-card-text>
      <p class="mb-7">Are you a resident of British Columbia?</p>
      <v-radio-group v-model="selection">
        <v-radio label="Yes" value="yes" class="font-weight-bold"></v-radio>
        <v-radio label="No" value="no" class="font-weight-bold"></v-radio>
      </v-radio-group>
    </v-card-text>
    <v-card-actions class="form__btns">
      <v-spacer></v-spacer>
      <v-btn large color="primary" :disabled="!selection" @click="next()">Next<v-icon left class="ml-3 mr-2">mdi-arrow-right</v-icon></v-btn>
      <v-btn large depressed @click="cancel()">Cancel</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
@Component({
  name: 'ProvinceSelectorDialog'
})
export default class ProvinceSelectorDialog extends Vue {
  @Prop({ default: false }) signedIn
  private selection = ''

  private next () {
    if (this.selection === 'yes') {
      if (this.signedIn) {
        this.$emit('bc-signed-in')
      } else {
        this.$emit('bc-not-signed-in')
      }
    } else {
      this.$emit('oop')
    }
  }

  private cancel () {
    this.$emit('close')
  }
}
</script>
