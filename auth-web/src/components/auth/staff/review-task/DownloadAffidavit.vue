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
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class DownloadAffidavit extends Vue {
  @Prop({ default: null }) tabNumber: number
  @Prop({ default: 'Download Affidavit' }) title: string
  @Prop({ default: 'Download the notarized affidavit associated with this account to verify the account creators ' +
    'identity and associated information.' }) subTitle: string
  @Prop({ default: '' }) affidavitName: string
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

</style>
