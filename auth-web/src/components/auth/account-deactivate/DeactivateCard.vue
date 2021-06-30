<template>
  <v-card class="py-4 px-4">
    <v-card-title data-test="title-deactivate" class="font-weight-bold mb-4">
      When this account is deactivated...
    </v-card-title>

    <v-card-text>
      <div v-for="item in info" :key="item.title" class="d-flex ml-3 mt-1">
        <div>
          <v-icon size="30" color="error" class="mt-1 mr-4"
            >mdi-alert-circle-outline</v-icon
          >
        </div>
        <div class="ml-3 mt-1">
          <h4 class="font-weight-bold">{{ $t(item.title) }}</h4>
          <p>{{ $t(item.description) }}</p>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import Vue from 'vue'

@Component({
})
export default class DeactivateCard extends Vue {
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
    return this.infoArray.filter(obj => !obj.type || obj.type === this.type)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
