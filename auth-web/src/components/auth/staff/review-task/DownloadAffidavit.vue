<template>
  <section>
    <h2 class="mb-7">
      {{ `${tabNumber !==null ? `${tabNumber}.` : ''} ${title}` }}
    </h2>
    <p class="mb-9">
      {{ subTitle }}
    </p>
    <v-btn
      x-large=""
      outlined
      color="primary"
      class="font-weight-bold"
      @click="$emit('emit-download-affidavit')"
    >
      <v-icon
        left
        class="mr-2"
      >
        mdi-file-download-outline
      </v-icon>
      {{ `${affidavitName}-affidavit` }}
    </v-btn>
  </section>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'DownloadAffidavit',
  props: {
    tabNumber: {
      type: Number,
      default: null
    },
    title: {
      type: String,
      default: 'Download Affidavit'
    },
    subTitle: {
      type: String,
      default: 'Download the notarized affidavit associated with this account to verify the account creators ' +
        'identity and associated information.'
    },
    affidavitName: {
      type: String,
      default: ''
    }
  }
})
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

</style>
