<template>
  <v-card>
    <v-card-title class="font-weight-bold mb-5" >
      When this account is deactivated...
    </v-card-title>

    <v-card-text>
      <div v-for="item in info" :key="item" class="d-flex align-center">
        <div>
          <v-icon color="error" class="mt-1 mr-4">mdi-alert-circle-outline</v-icon>
        </div>
        <div><h4 class="font-weight-bold ">  {{ $t(item.title) }}</h4>
          <p>{{ $t(item.description) }}</p>
        </div>

      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'

@Component({
})
export default class DeactivateCard {
  @Prop() private type: string

  // no type matches means show it for all types
  private infoArray: { title: string, description?: string, type?: string }[] = [
    {
      title: 'deactivateMemberRemovalTitle',
      description: 'deactivateMemberRemovalDesc'
    },
    {
      title: 'businessRemovalTitle',
      description: 'businessRemovalDesc'
    },
    {
      title: 'padRemovalTitle',
      type: 'PREMIUM'
    }

  ]

  private get info () {
    return this.infoArray.filter(obj => !obj.type || obj.type === this.orgType)
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

</style>
