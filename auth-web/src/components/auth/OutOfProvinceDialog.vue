<template>
  <v-card>
    <v-card-title>Create a BC Registries Account</v-card-title>
    <v-card-text>
      <p class="mb-1">Are you a resident of British Columbia?</p>
    </v-card-text>
    <v-radio-group class="ml-5" v-model="selection">
      <v-radio label="Yes" value="yes"></v-radio>
      <v-radio label="No" value="no"></v-radio>
    </v-radio-group>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn :disabled="!selection" large color="primary" @click="next()">Next<v-icon left class="ml-3 mr-2">mdi-arrow-right</v-icon></v-btn>
      <v-btn large @click="cancel()">Cancel</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
@Component({
  name: 'OutOfProvinceDialog'
})
export default class OutOfProvinceDialog extends Vue {
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

<style lang="scss" scoped>
</style>
