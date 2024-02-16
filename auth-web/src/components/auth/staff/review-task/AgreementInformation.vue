<template>
  <section>
    <h2 class="mb-5">
      {{ `${tabNumber !==null ? `${tabNumber}.` : ''} ${title}` }}
    </h2>
    <v-row>
      <v-col class="cols-12 py-2">
        <ProductTos
          :userName="userName"
          :orgName="orgName"
          :isTOSAlreadyAccepted="isTOSAlreadyAccepted"
          :isApprovalFlow="isApprovalFlow"
        />
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ProductTos from '@/components/auth/common/ProductTOS.vue'

@Component({
  components: {
    ProductTos
  }
})
export default class AgreementInformation extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: 'Agreement' }) private title: string
  @Prop({ default: '' }) userName: string
  @Prop({ default: '' }) orgName: string
  @Prop({ default: true }) isTOSAlreadyAccepted:boolean
  @Prop({ default: true }) isApprovalFlow:boolean
}
</script>
