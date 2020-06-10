<template>
  <div>
    <OutOfProvinceAccountInstructions v-if="page === PAGES.SETUP_ACCOUNT_OUT_OF_PROVINCE_INSTRUCTIONS"></OutOfProvinceAccountInstructions>
    <OutOfProvinceAccountDownloadAffidavit v-if="page === PAGES.SETUP_ACCOUNT_OUT_OF_PROVINCE_DOWNLOAD"></OutOfProvinceAccountDownloadAffidavit>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import AccountInstructions from '@/components/auth/extraprovince/AccountInstructions.vue'
import AffidavitDownload from '@/components/auth/extraprovince/AffidavitDownload.vue'
import { Pages } from '@/util/constants'

@Component({
  components: {
    OutOfProvinceAccountInstructions: AccountInstructions,
    OutOfProvinceAccountDownloadAffidavit: AffidavitDownload
  }
})
export default class OutOfProvinceAccountView extends Vue {
  @Prop({ default: '' }) private page: string
  private readonly PAGES = Pages
}
</script>

<style lang="scss" scoped>

</style>
