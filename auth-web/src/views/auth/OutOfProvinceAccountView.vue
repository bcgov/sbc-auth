<template>
  <div>
    <OutOfProvinceAccountInstructions v-if="page === PAGES.SETUP_ACCOUNT_OUT_OF_PROVINCE_INSTRUCTIONS"></OutOfProvinceAccountInstructions>
    <OutOfProvinceAccountDownloadAffidavit v-if="page === PAGES.SETUP_ACCOUNT_OUT_OF_PROVINCE_DOWNLOAD"></OutOfProvinceAccountDownloadAffidavit>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import OutOfProvinceAccountDownloadAffidavit from '@/components/auth/OutOfProvinceAccountDownloadAffidavit.vue'
import OutOfProvinceAccountInstructions from '@/components/auth/OutOfProvinceAccountInstructions.vue'
import { Pages } from '@/util/constants'

@Component({
  components: {
    OutOfProvinceAccountInstructions,
    OutOfProvinceAccountDownloadAffidavit
  }
})
export default class OutOfProvinceAccountView extends Vue {
  @Prop({ default: '' }) private page: string
  private readonly PAGES = Pages
}
</script>

<style lang="scss" scoped>

</style>
